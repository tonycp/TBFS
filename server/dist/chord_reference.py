from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

import socket, json, logging

from logic.configurable import Configurable
from logic.handlers import *
from data.const import *

from .utils import hash_sha1_key

__all__ = ["ChordReference"]


class ChordReference:
    def __init__(
        self,
        config: Configurable,
    ):
        self.protocol = config[PROTOCOL_KEY]
        self.ip = config[HOST_KEY]
        self.chord_port = config[NODE_PORT_KEY]
        self.data_port = config[PORT_KEY]
        self.id = hash_sha1_key(f"{self.ip}:{self.chord_port}")
        self._config = config

    # region Properties
    @property
    def sucs(self) -> ChordReference:
        return self._get_chord_reference("sucs")

    @property
    def pred(self) -> ChordReference:
        return self._get_chord_reference("pred")

    @property
    def is_alive(self) -> bool:
        return self._ping_pong()

    @sucs.setter
    def sucs(self, node: ChordReference):
        self._set_chord_reference("sucs", node.id)

    @pred.setter
    def pred(self, node: ChordReference):
        self._set_chord_reference("pred", node.id)

    # endregion

    # region Reference Methods
    def _call_finding_methods(self, func_name: str, key: int) -> ChordReference:
        logging.info(f"Calling {func_name} with key: {key}")
        data = {"func_name": func_name, "key": key}
        response = self._send_chord_message(CHORD_DATA.FIND_CALL, data)
        logging.info(f"{func_name} call complete with result: {response}")
        ip = response.get("ip")
        if not ip:
            return None
        updated_config = self._config.copy_with_updates({HOST_KEY: ip})
        return ChordReference(updated_config)

    def _call_notify_methods(
        self, func_name: str, node: Optional[ChordReference]
    ) -> None:
        ip = node.ip if node else None
        logging.info(f"Calling {func_name} with node: {ip}")
        data = {"func_name": func_name, "node": ip}
        self._send_chord_message(CHORD_DATA.NOTIFY_CALL, data)
        logging.info(f"{func_name} call complete")

    def _get_property(self, property: str) -> Any:
        logging.info(f"Getting property: {property}")
        data = {"property": property}
        response = self._send_chord_message(CHORD_DATA.GET_PROPERTY, data)
        value = response.get("value")
        logging.info(f"Property {property} retrieved with value: {value}")
        return value

    def _set_property(self, property: str, value: Any) -> None:
        logging.info(f"Setting property: {property} to value: {value}")
        data = {"property": property, "value": value}
        self._send_chord_message(CHORD_DATA.SET_PROPERTY, data)
        logging.info(f"Property {property} set to value: {value}")

    def _get_chord_reference(self, property: str) -> ChordReference:
        logging.info(f"Getting chord reference for property: {property}")
        data = {"property": property}
        response = self._send_chord_message(CHORD_DATA.GET_CHORD_REFERENCE, data)
        logging.info(f"Chord reference for {property} retrieved: {response}")
        ip = response.get("ip")
        if not ip:
            return None
        updated_config = self._config.copy_with_updates({HOST_KEY: ip})
        return ChordReference(updated_config)

    def _set_chord_reference(self, property: str, ip: int):
        logging.info(f"Setting chord reference for property: {property} to value: {ip}")
        data = {"property": property, "ip": ip}
        self._send_chord_message(CHORD_DATA.SET_CHORD_REFERENCE, data)
        logging.info(f"Chord reference for {property} set to ip: {ip}")

    def _get_replication(self, key: str, ls_time: Optional[datetime]) -> None:
        logging.info("Getting replication reference")
        data = {"key": key, "ls_time": ls_time}
        response = self._send_chord_message(CHORD_DATA.GET_REPLICATION, data)
        value = response.get("value")
        logging.info(f"Getting replication complete")
        return value

    def _set_replication(self, key: str, data: Dict[str, Any]) -> None:
        logging.info("Setting replication reference")
        self._send_chord_message(CHORD_DATA.SET_REPLICATION, {key, data})
        logging.info(f"Setting replication complete")

    # endregion

    # region Chord Methods
    def closest_preceding_node(self, key: int) -> ChordReference:
        return self._call_finding_methods("closest_preceding_node", key)

    def get_sucs(self, key: int) -> ChordReference:
        return self._call_finding_methods("get_sucs", key)

    def get_replication(self, key: str, ls_time: Optional[datetime]) -> Dict[str, Any]:
        return self._get_replication(key, ls_time)

    def set_replication(self, key: str, data: Dict[str, Any]) -> None:
        self._set_replication(key, data)

    def join(self, node: Optional[ChordReference] = None) -> None:
        self._call_notify_methods("join", node)

    def get_replications(self) -> List[Tuple[ChordReference, str]]:
        return [(self.sucs, "sucs"), (self.pred, "pred")]

    # endregion

    # region Message Methods
    def _socket_call(self, header: str, data: Dict[str, Any]) -> Dict[str, Any]:
        message = json.dumps({"header": header, "data": data})
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(WAIT_CHECK)
        port = self.chord_port

        logging.info(f"Sending message to {self.ip}:{port} from chord reference")
        try:
            sock.connect((self.ip, port))
            sock.sendall(message.encode("utf-8"))
            response = sock.recv(1024)
            logging.info(f"Received response from {self.ip}:{port}: {response}")
            return json.loads(response.decode("utf-8"))
        except ConnectionRefusedError:
            logging.error(f"Connection refused by {self.ip}:{port}")
            return {"error": "Connection refused"}
        except socket.timeout:
            logging.error(f"Timeout occurred while communicating with {self.ip}:{port}")
            return {"error": "Timeout"}
        except Exception as e:
            logging.error(
                f"An error occurred while communicating with {self.ip}:{port}: {e}"
            )
            return {"error": str(e)}
        finally:
            sock.close()

    def _send_chord_message(
        self, chord_data: CHORD_DATA, data: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        logging.info(f"Sending chord message with data: {data}")
        header = header_data(**CHORD_DATA_COMMANDS[chord_data])
        response = self._socket_call(header, data)
        logging.info(f"Chord message sent with response: {response}")
        return response or {}

    def _ping_pong(self) -> bool:
        logging.info("Sending ping message")
        data = {"message": "Ping"}
        response = self._send_chord_message(CHORD_DATA.PON_CALL, data)
        logging.info("Ping message sent with response: Pong")
        return response.get("message") == "Pong"

    # endregion
