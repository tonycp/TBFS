import hashlib
import json
import threading
import zmq
from typing import Optional, Tuple

SHA1_HASH = 160


class ChordNode:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.node_id = ChordNode._hash(f"{host}:{port}")
        self.successor = self
        self.predecessor = None
        self.finger_table = [self] * SHA1_HASH
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)

    @staticmethod
    def _hash(key: str) -> int:
        return int(hashlib.sha1(key.encode()).hexdigest(), 16)

    @staticmethod
    def _in_interval(key_id: int, start: int, end: int) -> bool:
        if start < end:
            return start < key_id <= end
        else:
            return start < key_id or key_id <= end

    def _join(self, known_node: Tuple[str, int]):
        # Implement logic to join the network using a known node
        pass

    def _closest_preceding_node(self, key_id: int) -> "ChordNode":
        for node in reversed(self.finger_table):
            if self._in_interval(node.node_id, self.node_id, key_id):
                return node
        return self

    def join_network(self, known_node: Optional[Tuple[str, int]] = None):
        if known_node:
            self._join(known_node)
        else:
            self.successor = self

    def find_successor(self, key: str) -> "ChordNode":
        key_id = ChordNode._hash(key)
        if self._in_interval(key_id, self.node_id, self.successor.node_id):
            return self.successor
        else:
            node = self._closest_preceding_node(key_id)
            return node.find_successor(key)

    def send_request(self, command_name: str, func_name: str, data: dict) -> str:
        self.socket.connect(f"tcp://{self.successor.host}:{self.successor.port}")
        request = json.dumps(
            {"command_name": command_name, "function": func_name, "dataset": data}
        )
        self.socket.send_string(request)
        response = self.socket.recv_string()
        self.socket.disconnect(f"tcp://{self.successor.host}:{self.successor.port}")
        return response

    def stabilize(self):
        # Implement stabilization logic
        pass

    def fix_fingers(self):
        # Implement finger table fixing logic
        pass

    def run(self):
        threading.Thread(target=self.stabilize).start()
        threading.Thread(target=self.fix_fingers).start()
