from __future__ import annotations
import logging
from typing import Optional, Dict, Any, Union

import zmq, hashlib, json

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
        context=zmq.Context(),
    ):
        self.protocol = config[PROTOCOL_KEY]
        self.ip = config[HOST_KEY]
        self.chord_port = config[NODE_PORT_KEY]
        self.data_port = config[PORT_KEY]
        self.context = context
        self.id = ChordReference._hash_key(f"{self.ip}:{self.chord_port}")
        self._config = config

        socket = self.context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 100000)
        socket.connect(f"{self.protocol}://{self.ip}:{self.chord_port}")
        self.socket = socket

    @staticmethod
    def _hash_key(key: str) -> int:
        return int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16)

    # region Properties Methods
    @property
    def successor(self) -> ChordReference:
        return self._get_chord_reference("id")

    @property
    def predecessor(self) -> ChordReference:
        return self._get_chord_reference("id")

    @property
    def leader(self) -> ChordReference:
        return self._get_chord_reference("id")

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
        self._set_property("successor", node.id)

    @predecessor.setter
    def predecessor(self, node: ChordReference):
        self._set_property("predecessor", node.id)

    @leader.setter
    def leader(self, node: ChordReference):
        self._set_property("leader", node.id)

    @im_the_leader.setter
    def im_the_leader(self, value: bool):
        self._set_property("im_the_leader", value)

    @in_election.setter
    def in_election(self, value: bool):
        self._set_property("in_election", value)

    # endregion

    # region Finding Methods
    def _closest_preceding_node(self, key: int) -> ChordReference:
        self._call_finding_methods("_closest_preceding_node", key)

    def _find_successor(self, key: int) -> ChordReference:
        self._call_finding_methods("_find_successor", key)

    def _find_predecessor(self, key: int) -> ChordReference:
        self._call_finding_methods("_find_predecessor", key)

    # endregion

    # region Notification Methods
    def adopt_leader(self, node: Optional[ChordReference] = None) -> None:
        self._call_notify_methods("adopt_leader", node)

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
        data = json.dumps({"function_name": function_name, "key": key})
        logging.info(f"Calling {function_name} with key: {key}")
        return self._send_chord_message(CHORD_DATA.FIND_CALL, data)["node"]

    def _call_notify_methods(self, function_name: str, node: ChordReference) -> None:
        data = json.dumps({"function_name": function_name, "node": node.ip})
        self._send_chord_message(CHORD_DATA.NOTIFY_CALL, data)

    def _get_property(self, property: str) -> Any:
        data = json.dumps({"property": property})
        return self._send_chord_message(CHORD_DATA.GET_PROPERTY, data)["value"]

    def _set_property(self, property: str, value: Any) -> None:
        data = json.dumps({"property": property, "value": value})
        self._send_chord_message(CHORD_DATA.SET_PROPERTY, data)

    def _get_chord_reference(self, property: str) -> ChordReference:
        response = self._get_property(property)
        updated_config = self._config.copy_with_updates({HOST_KEY: response})
        return ChordReference(updated_config, self.context)

    def _send_chord_message(self, chord_data: CHORD_DATA, data: str) -> Dict[str, Any]:
        header = header_data(**CHORD_DATA_COMMANDS[chord_data])
        return self._zmq_call(header, data)

    def _zmq_call(self, header: str, data: str) -> Dict[str, Any]:
        message = [header.encode("utf-8"), data.encode("utf-8")]
        port, socket = self.chord_port, self.socket

        logging.info(f"Call to chord reference: {self.ip}:{self.chord_port}")
        try:
            socket.send_multipart(message)
            response = socket.recv_json()
            logging.info(f"Get response: {response} from {self.ip}:{port}")
        except zmq.error.Again:
            logging.error(f"Timeout occurred receiving with {self.ip}:{port}")
            response = {"error": "Timeout"}
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            response = {"error": str(e)}

        return response

    def _ping_pong(self) -> bool:
        data = json.dumps({"message": "Ping"})
        response = self._send_chord_message(CHORD_DATA.PON_CALL, data)
        return response.get("message") == "Pong"

    # endregion
