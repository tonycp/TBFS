from __future__ import annotations
from typing import List, Optional, Dict, Any

import zmq, hashlib


class ChordReference:
    def __init__(self, address: str):
        self.node_id = ChordReference._hash_key(address)
        self.address = address

    @staticmethod
    def _hash_key(key: str) -> int:
        return int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16)

    @staticmethod
    def _is_alive(node: ChordReference) -> bool:
        try:
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(node.address)
            socket.send(b"PING")
            response = socket.recv()
            socket.close()
            return response == b"PONG"
        except:
            return False

    @staticmethod
    def _check_predecessor(node):
        if node.predecessor and not ChordReference._is_alive(node.predecessor):
            node.predecessor = None

    @staticmethod
    def _inbetween(k: int, start: int, end: int) -> bool:
        """Check if an id is between two other ids in the Chord ring."""
        if start < end:
            return start < k <= end
        else:
            return start < k or k <= end

    def _closest_preceding_node(self, key: int) -> ChordReference:
        pass

    def _find_successor(self, key: int) -> ChordReference:
        pass

    def _find_predecessor(self, key: int) -> ChordReference:
        pass

    def _update_others(self):
        pass

    def _update_finger_table(self, s: ChordReference, i: int):
        pass

    def _init_finger_table(self, existing_node: ChordReference):
        pass

    def _notify(self, node: ChordReference):
        pass

    def _stabilize(self):
        pass

    def _fix_fingers(self):
        pass

    def _handle_election_message(self, data: Dict[str, Any]):
        pass

    def _handle_leader_message(self, data: Dict[str, Any]):
        pass

    def _find_node_by_id(self, node_id: int) -> Optional[ChordReference]:
        pass

    def _send_message(self, address: str, message: Dict[str, Any]):
        pass

    def _election_loop(self):
        pass

    def _start_election(self):
        pass

    def _send_election_message(self):
        pass

    def join(self, existing_node: Optional[ChordReference] = None):
        pass
