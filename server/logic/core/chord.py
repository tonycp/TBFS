from __future__ import annotations
import os
from typing import List, Optional, Dict, Any, Union
import threading, hashlib, time, zmq, json, logging

from .handlers import handle_request
from .server import Server
from .chord_reference import ChordReference

__all__ = ["ChordNode"]

SHA_1 = 160


class ChordNode(Server, ChordReference):
    def __init__(self, config: Optional[Dict[str, Optional[Union[str, int]]]] = None):
        ChordNode._check_default(config or {})
        self.successor: ChordReference = self
        self.predecessor: Optional[ChordReference] = None
        self.finger_table: List[Optional[ChordReference]] = [self] * SHA_1
        self.in_election = False
        self.work_done = True
        self.leader = None
        self.its_me = False

        address = f"{config['protocol']}://{config['host']}:{config['port']}"
        ChordReference.__init__(self, address)
        Server.__init__(self, config)
        threading.Thread(target=self._election_loop).start()

    @staticmethod
    def _check_default(
        config: Dict[str, Optional[Union[str, int]]]
    ) -> Dict[str, Optional[Union[str, int]]]:
        """Check and set default values for the configuration."""
        Server._check_default(config)
        key, value = "chord_port", int(os.getenv("CHORD_PORT", 5556))
        config.setdefault(key, value)
        return config

    def _closest_preceding_node(self, key: int) -> ChordReference:
        for finger_node in reversed(self.finger_table):
            if finger_node and self.node_id < finger_node.node_id < key:
                return finger_node
        return self

    def _find_successor(self, key: int) -> ChordReference:
        if self.successor == self:
            return self
        if self.node_id < key <= self.successor.node_id:
            return self.successor
        else:
            node = self._closest_preceding_node(key)
            return self if node == self else node._find_successor(key)

    def _find_predecessor(self, key: int) -> ChordReference:
        node = self
        while not (node.node_id < key <= node.successor.node_id):
            node = node._closest_preceding_node(key)
        return node

    def _update_others(self):
        for i in range(SHA_1):
            pred = self._find_predecessor((self.node_id - 2**i) % (2**SHA_1))
            pred._update_finger_table(self, i)

    def _update_finger_table(self, s: ChordReference, i: int):
        if (
            self.finger_table[i] is None
            or self.node_id <= s.node_id < self.finger_table[i].node_id
        ):
            self.finger_table[i] = s
            pred = self.predecessor
            if pred:
                pred._update_finger_table(s, i)

    def _init_finger_table(self, existing_node: ChordReference):
        self.finger_table[0] = existing_node._find_successor(self.node_id)
        self.predecessor = self.finger_table[0].predecessor
        self.finger_table[0].predecessor = self
        for i in range(1, SHA_1):
            start = (self.node_id + 2**i) % (2**SHA_1)
            if self.node_id <= self.finger_table[i - 1].node_id < start:
                self.finger_table[i] = self.finger_table[i - 1]
            else:
                self.finger_table[i] = existing_node._find_successor(start)

    def _notify(self, node: ChordReference):
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
                Server._start_listening(self)
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error in _run: {e}")

    def _handle_chord_request(self, func_name: str, data: Dict[str, Any]) -> str:
        """Handle requests specific to ChordNode."""
        if func_name == "find_successor":
            key = data.get("key")
            return json.dumps(self._find_successor(key).address)
        elif func_name == "election":
            self._handle_election_message(data)
            return json.dumps({"status": "election message received"})
        # ...handle other ChordNode methods...
        return json.dumps({"error": "Unknown ChordNode function"})

    def _handle_election_message(self, data: Dict[str, Any]):
        node_id = data.get("node_id")
        if node_id > self.node_id:
            self.in_election = False
            self._send_message(
                self.successor.address, {"type": "election", "node_id": node_id}
            )
        elif node_id < self.node_id:
            self._send_message(
                self.successor.address, {"type": "election", "node_id": self.node_id}
            )
        else:
            self.leader = self
            self.its_me = True
            self.in_election = False
            self._send_message(
                self.successor.address, {"type": "leader", "node_id": self.node_id}
            )

    def _handle_leader_message(self, data: Dict[str, Any]):
        node_id = data.get("node_id")
        self.leader = self._find_node_by_id(node_id)
        self.in_election = False
        self.its_me = False
        self._send_message(
            self.successor.address, {"type": "leader", "node_id": node_id}
        )

    def _find_node_by_id(self, node_id: int) -> Optional[ChordReference]:
        for node in self.finger_table:
            if node and node.node_id == node_id:
                return node
        return None

    def _send_message(self, address: str, message: Dict[str, Any]):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(address)
        socket.send(json.dumps(message).encode("utf-8"))
        socket.close()

    def _election_loop(self):
        while True:
            if not self.in_election and not self.its_me:
                self._start_election()
            time.sleep(5)

    def _start_election(self):
        self.in_election = True
        self.work_done = False
        self.leader = None
        self._send_election_message()

    def _send_election_message(self):
        for node in self.finger_table:
            if node and node != self:
                self._send_message(
                    node.address, {"type": "election", "node_id": self.node_id}
                )

    def join(self, existing_node: Optional[ChordReference] = None):
        if existing_node:
            self._init_finger_table(existing_node)
            self._update_others()
        else:
            self.finger_table = [self] * SHA_1
            self.predecessor = self
        threading.Thread(target=self._election_loop).start()
