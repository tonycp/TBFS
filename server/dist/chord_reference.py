from __future__ import annotations
import logging
from typing import Optional, Dict, Any, Union

import socket, hashlib, json, time

from logic.handlers import *
from data.const import *

from logic.configurable import Configurable

__all__ = ["ChordReference", "in_between"]


def in_between(k: int, start: int, end: int) -> bool:
    """Check if an id is between two other ids in the Chord ring."""
    if start < end:
        return start < k <= end
    else:
        return start < k or k <= end


def bully(id: int, other_id: int) -> bool:
    """Check if the current node is more powerful than the other node."""
    return int(id) > int(other_id)


class ChordReference:
    def __init__(
        self,
        config: Configurable,
    ):
        self.protocol = config[PROTOCOL_KEY]
        self.ip = config[HOST_KEY]
        self.chord_port = config[NODE_PORT_KEY]
        self.data_port = config[PORT_KEY]
        self.id = ChordReference._hash_key(f"{self.ip}:{self.chord_port}")
        self._config = config

    @staticmethod
    def _hash_key(key: str) -> int:
        return int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16)

    # region Properties Methods
    @property
    def successor(self) -> ChordReference:
        return self._get_chord_reference("successor")

    @property
    def predecessor(self) -> ChordReference:
        return self._get_chord_reference("predecessor")

    @property
    def leader(self) -> ChordReference:
        return self._get_chord_reference("leader")

    @property
    def im_the_leader(self) -> bool:
        return self._get_property("im_the_leader")

    @property
    def in_election(self) -> bool:
        return self._get_property("in_election")

    @property
    def is_alive(self) -> bool:
        return self._ping_pong()

    @successor.setter
    def successor(self, node: ChordReference):
        self._set_chord_reference("successor", node.id)

    @predecessor.setter
    def predecessor(self, node: ChordReference):
        self._set_chord_reference("predecessor", node.id)

    @leader.setter
    def leader(self, node: ChordReference):
        self._set_chord_reference("leader", node.id)

    @im_the_leader.setter
    def im_the_leader(self, value: bool):
        self._set_property("im_the_leader", value)

    @in_election.setter
    def in_election(self, value: bool):
        self._set_property("in_election", value)

    # endregion

    # region Finding Methods
    def _closest_preceding_node(self, key: int) -> ChordReference:
        return self._call_finding_methods("_closest_preceding_node", key)

    def _find_successor(self, key: int) -> ChordReference:
        return self._call_finding_methods("_find_successor", key)

    def _find_predecessor(self, key: int) -> ChordReference:
        return self._call_finding_methods("_find_predecessor", key)

    # endregion

    # region Notification Methods
    def adopt_leader(self, node: Optional[ChordReference] = None) -> None:
        logging.info(f"Adopting leader: {node.ip if node else 'self'}")
        self._call_notify_methods("adopt_leader", node)
        logging.info(f"Leader adopted: {node.ip if node else 'self'}")

    def join(self, node: Optional[ChordReference] = None) -> None:
        self._call_notify_methods("join", node)

    def notify(self, node: ChordReference) -> None:
        self._call_notify_methods("notify", node)

    def reverse_notify(self, node: ChordReference) -> None:
        self._call_notify_methods("reverse_notify", node)

    def not_alone_notify(self, node: ChordReference) -> None:
        self._call_notify_methods("not_alone_notify", node)

    # endregion

    # region Message Methods

    def _call_finding_methods(self, function_name: str, key: int) -> ChordReference:
        logging.info(f"Calling {function_name} with key: {key}")
        data = {"function_name": function_name, "key": key}
        response = self._send_chord_message(CHORD_DATA.FIND_CALL, data)
        logging.info(f"{function_name} call complete with result: {response}")
        updated_config = self._config.copy_with_updates({HOST_KEY: response["ip"]})
        return ChordReference(updated_config)

    def _call_notify_methods(
        self, function_name: str, node: Optional[ChordReference]
    ) -> None:
        logging.info(
            f"Calling {function_name} with node: {node.ip if node else 'None'}"
        )
        data = {"function_name": function_name, "node": node.ip if node else None}
        self._send_chord_message(CHORD_DATA.NOTIFY_CALL, data)
        logging.info(f"{function_name} call complete")

    def _get_property(self, property: str) -> Any:
        logging.info(f"Getting property: {property}")
        data = {"property": property}
        response = self._send_chord_message(CHORD_DATA.GET_PROPERTY, data)
        logging.info(f"Property {property} retrieved with value: {response['value']}")
        return response["value"]

    def _set_property(self, property: str, value: Any) -> None:
        logging.info(f"Setting property: {property} to value: {value}")
        data = {"property": property, "value": value}
        self._send_chord_message(CHORD_DATA.SET_PROPERTY, data)
        logging.info(f"Property {property} set to value: {value}")

    def _get_chord_reference(self, property: str) -> ChordReference:
        logging.info(f"Getting chord reference for property: {property}")
        data = {"property": property}
        response = self._send_chord_message(CHORD_DATA.GET_CHORD_REFERENCE, data)
        ip = response["ip"]
        logging.info(f"Chord reference for {property} retrieved: {ip}")
        ref = None
        if ip:
            updated_config = self._config.copy_with_updates({HOST_KEY: ip})
            ref = ChordReference(updated_config)
        return ref

    def _set_chord_reference(self, property: str, ip: int):
        logging.info(f"Setting chord reference for property: {property} to value: {ip}")
        data = {"property": property, "ip": ip}
        self._send_chord_message(CHORD_DATA.SET_CHORD_REFERENCE, data)
        logging.info(f"Chord reference for {property} set to ip: {ip}")

    def _send_chord_message(self, chord_data: CHORD_DATA, data: str) -> Dict[str, Any]:
        logging.info(f"Sending chord message with data: {data}")
        header = header_data(**CHORD_DATA_COMMANDS[chord_data])
        response = self._socket_call(header, data)
        logging.info(f"Chord message sent with response: {response}")
        return response

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

    def _ping_pong(self) -> bool:
        logging.info("Sending ping message")
        data = {"message": "Ping"}
        response = self._send_chord_message(CHORD_DATA.PON_CALL, data)
        logging.info("Ping message sent with response: Pong")
        return response.get("message") == "Pong"

    # endregion
