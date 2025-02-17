from __future__ import annotations
from typing import Optional, Dict, Any, Union

import zmq, hashlib, json

from servers.server import Server
from data.const import *

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
        address: str,
        chord_port: int = DEFAULT_NODE_PORT,
        data_port: int = DEFAULT_DATA_PORT,
        context: zmq.Context = zmq.Context(),
    ):
        self.id = ChordReference._hash_key(address)
        self.address = address
        self.chord_port = chord_port
        self.data_port = data_port
        self.context = context

    @staticmethod
    def get_config(
        config: Dict[str, Optional[Union[str, int]]],
        context: zmq.Context = zmq.Context(),
    ) -> Dict[str, Any]:
        return {
            "address": f"{config[PROTOCOL_KEY]}://{config[HOST_KEY]}",
            "chord_port": config[NODE_PORT_KEY],
            "data_port": config[PORT_KEY],
            "context": context,
        }

    @staticmethod
    def _hash_key(key: str) -> int:
        return int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16)

    # region Properties Methods
    @property
    def successor(self) -> ChordReference:
        return self._get_chord_reference("address")

    @property
    def predecessor(self) -> ChordReference:
        return self._get_chord_reference("address")

    @property
    def leader(self) -> ChordReference:
        return self._get_chord_reference("address")

    @property
    def im_the_leader(self) -> bool:
        return self._get_property(__name__)

    @property
    def in_election(self) -> bool:
        return self._get_property(__name__)

    @property
    def is_alive(self) -> bool:
        return self._ping_pong()

    @successor.setter
    def successor(self, node: ChordReference):
        self._set_property(__name__, node.address)

    @predecessor.setter
    def predecessor(self, node: ChordReference):
        self._set_property(__name__, node.address)

    @leader.setter
    def leader(self, node: ChordReference):
        self._set_property(__name__, node.address)

    @im_the_leader.setter
    def im_the_leader(self, value: bool):
        self._set_property(__name__, value)

    @in_election.setter
    def in_election(self, value: bool):
        self._set_property(__name__, value)

    # endregion

    # region Finding Methods
    def _closest_preceding_node(self, key: int) -> ChordReference:
        self._call_finding_methods(__name__, key)

    def _find_successor(self, key: int) -> ChordReference:
        self._call_finding_methods(__name__, key)

    def _find_predecessor(self, key: int) -> ChordReference:
        self._call_finding_methods(__name__, key)

    # endregion

    # region Notification Methods
    def adopt_leader(self, node: Optional[ChordReference] = None) -> None:
        self._call_notify_methods(__name__, node)

    def join(self, node: Optional[ChordReference] = None) -> None:
        self._call_notify_methods(__name__, node)

    def notify(self, node: ChordReference) -> None:
        self._call_notify_methods(__name__, node)

    def reverse_notify(self, node: ChordReference) -> None:
        self._call_notify_methods(__name__, node)

    def not_alone_notify(self, node: ChordReference) -> None:
        self._call_notify_methods(__name__, node)

    # endregion

    # region Message Methods

    def _call_finding_methods(self, function_name: str, key: int) -> ChordReference:
        data = json.dumps({"function_name": function_name, "key": key})
        return self._send_chord_message(CHORD_DATA.FIND_CALL, data)["node"]

    def _call_notify_methods(self, function_name: str, node: ChordReference) -> None:
        data = json.dumps({"function_name": function_name, "node": node.address})
        self._send_chord_message(CHORD_DATA.NOTIFY_CALL, data)

    def _get_property(self, property: str) -> Any:
        data = json.dumps({"property": property})
        return self._send_chord_message(CHORD_DATA.GET_PROPERTY, data)["value"]

    def _set_property(self, property: str, value: Any) -> None:
        data = json.dumps({"property": property, "value": value})
        self._send_chord_message(CHORD_DATA.SET_PROPERTY, data)

    def _get_chord_reference(self, property: str) -> ChordReference:
        chord_port, data_port, context = self.chord_port, self.data_port, self.context
        response = self._get_property(property)
        return ChordReference(response, chord_port, data_port, context)

    def _send_chord_message(self, chord_data: CHORD_DATA, data: str) -> Dict[str, Any]:
        header = Server.header_data(**CHORD_DATA_COMMANDS[chord_data])
        return self._zmq_call(header, data)

    def _zmq_call(self, header: str, data: str) -> Dict[str, Any]:
        message = [header.encode("utf-8"), data.encode("utf-8")]
        socket = self.context.socket(zmq.REQ)

        socket.connect(f"{self.address}:{self.chord_port}")
        socket.send_multipart(message)
        response = socket.recv_json()
        socket.close()

        return response

    def _ping_pong(self) -> bool:
        data = json.dumps({"message": "Ping"})
        self._send_chord_message(CHORD_DATA.PON_CALL, data)

    # endregion
