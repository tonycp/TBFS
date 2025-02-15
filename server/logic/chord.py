from __future__ import annotations
from typing import List, Optional, Dict, Any
import threading, hashlib, time, zmq, json

from server.logic.handlers import handle_request
from .server import Server

SHA_1 = 160


class ChordNode(Server):
    def __init__(self, address: str):
        super().__init__()
        self.node_id = self._hash_key(address)
        self.address = address
        self.successor: ChordNode = self
        self.predecessor: Optional[ChordNode] = None
        self.finger_table: List[Optional[ChordNode]] = [self] * SHA_1

    @staticmethod
    def _hash_key(key: str) -> int:
        return int(hashlib.sha1(key.encode()).hexdigest(), 16) % (2**SHA_1)

    @staticmethod
    def _is_alive(node: ChordNode) -> bool:
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
        if node.predecessor and not ChordNode._is_alive(node.predecessor):
            node.predecessor = None

    def _closest_preceding_node(self, key: int) -> ChordNode:
        for finger_node in reversed(self.finger_table):
            if finger_node and self.node_id < finger_node.node_id < key:
                return finger_node
        return self

    def _find_successor(self, key: int) -> ChordNode:
        if self.successor == self:
            return self
        if self.node_id < key <= self.successor.node_id:
            return self.successor
        else:
            node = self._closest_preceding_node(key)
            return self if node == self else node._find_successor(key)

    def _find_predecessor(self, key: int) -> ChordNode:
        node = self
        while not (node.node_id < key <= node.successor.node_id):
            node = node._closest_preceding_node(key)
        return node

    def _update_others(self):
        for i in range(SHA_1):
            pred = self._find_predecessor((self.node_id - 2**i) % (2**SHA_1))
            pred._update_finger_table(self, i)

    def _update_finger_table(self, s: ChordNode, i: int):
        if (
            self.finger_table[i] is None
            or self.node_id <= s.node_id < self.finger_table[i].node_id
        ):
            self.finger_table[i] = s
            pred = self.predecessor
            if pred:
                pred._update_finger_table(s, i)

    def _init_finger_table(self, existing_node: ChordNode):
        self.finger_table[0] = existing_node._find_successor(self.node_id)
        self.predecessor = self.finger_table[0].predecessor
        self.finger_table[0].predecessor = self
        for i in range(1, SHA_1):
            start = (self.node_id + 2**i) % (2**SHA_1)
            if self.node_id <= self.finger_table[i - 1].node_id < start:
                self.finger_table[i] = self.finger_table[i - 1]
            else:
                self.finger_table[i] = existing_node._find_successor(start)

    def _notify(self, node: ChordNode):
        if self.predecessor is None or (
            self.predecessor.node_id < node.node_id < self.node_id
        ):
            self.predecessor = node

    def _stabilize(self):
        if self.successor is None or not ChordNode._is_alive(self.successor):
            return
        x = self.successor.predecessor
        if x and self.node_id < x.node_id < self.successor.node_id:
            self.successor = x
        self.successor._notify(self)

    def _fix_fingers(self):
        for i in range(SHA_1):
            start = (self.node_id + 2**i) % (2**SHA_1)
            self.finger_table[i] = self._find_successor(start)

    def _run(self):
        while True:
            try:
                ChordNode._check_predecessor(self)
                self._stabilize()
                self._fix_fingers()
                super()._start_listening()
                time.sleep(1)
            except Exception as e:
                print(f"Error in _run: {e}")

    def _solver_request(self, header_str: str) -> str:
        """Solve the request and return the result."""
        command_name, func_name, dataset = self._parse_header(header_str)
        if command_name == "ChordNode":
            return self._handle_chord_request(func_name, dataset)
        return handle_request((command_name, func_name, dataset))

    def _handle_chord_request(self, func_name: str, data: Dict[str, Any]) -> str:
        """Handle requests specific to ChordNode."""
        if func_name == "find_successor":
            key = data.get("key")
            return json.dumps(self._find_successor(key).address)
        # ...handle other ChordNode methods...
        return json.dumps({"error": "Unknown ChordNode function"})

    def join(self, existing_node: Optional[ChordNode] = None):
        if existing_node:
            self._init_finger_table(existing_node)
            self._update_others()
        else:
            self.finger_table = [self] * SHA_1
            self.predecessor = self

    def start(self):
        threading.Thread(target=self._run).start()
