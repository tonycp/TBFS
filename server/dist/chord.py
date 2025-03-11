from __future__ import annotations
from typing import Any, List, Optional, Dict, Tuple, Union

import threading, socket
import time, logging, json

from data.const import *
from logic.handlers import *
from logic.configurable import Configurable
from servers.server import Server

from .chord_reference import ChordReference, in_between

__all__ = ["ChordNode"]


class ChordNode(Server, ChordReference):
    _successor: ChordReference
    _predecessor: Optional[ChordReference]
    _leader: Optional[ChordReference]
    _im_the_leader: bool
    _in_election: bool

    def __init__(self, config: Optional[Configurable] = None):
        config = config or Configurable()
        ChordReference.__init__(self, config)

        self.finger_table: List[Optional[ChordReference]] = [self] * SHA_1
        self.leader: Optional[ChordReference] = self
        self.sucs: Optional[ChordReference] = self
        self.pred: Optional[ChordReference] = None
        self.im_the_leader: bool = True

        Server.__init__(self, config)
        self._subscribe_read_port(self._config[NODE_PORT_KEY])

    # region Properties Methods

    @property
    def sucs(self) -> ChordReference:
        return self._successor

    @property
    def pred(self) -> ChordReference:
        return self._predecessor

    @property
    def leader(self) -> ChordReference:
        return self._leader

    @property
    def im_the_leader(self) -> bool:
        return self._im_the_leader

    @property
    def in_election(self) -> bool:
        return self._in_election

    @property
    def is_alive(self) -> bool:
        return True

    @sucs.setter
    def sucs(self, node: ChordReference):
        self._successor = node

    @pred.setter
    def pred(self, node: ChordReference):
        self._predecessor = node

    @leader.setter
    def leader(self, node: ChordReference):
        self._leader = node

    @im_the_leader.setter
    def im_the_leader(self, value: bool):
        self._im_the_leader = value

    @in_election.setter
    def in_election(self, value: bool):
        self._in_election = value

    # endregion

    # region Finding Methods
    def closest_preceding_node(self, node_id: int) -> ChordReference:
        for finger_node in reversed(self.finger_table):
            if finger_node and in_between(finger_node.id, self.id, node_id):
                return finger_node
        return self

    def get_sucs(self, node_id: int) -> ChordReference:
        if self.id == node_id:
            return self

        if in_between(node_id, self.id, self.sucs.id):
            return self.sucs

        node = self
        closest = self.closest_preceding_node(node_id)
        while node != closest:
            node = closest
            closest = node.closest_preceding_node(node_id)

        return node.sucs

    def get_pred(self, node_id: int) -> ChordReference:
        node = self
        while not in_between(node_id, node.id, node.sucs.id):
            node = node.sucs
        return node

    def _get_other_sucs(self):
        for node in self.finger_table:
            if node and node.id != self.sucs.id and node.is_alive:
                return node

    # endregion

    # region Notification Methods
    def adopt_leader(self, node: Optional[ChordReference] = None) -> None:
        logging.info(f"Adopting leader: {node.ip if node else 'self'}")
        self.leader = node or self
        self.im_the_leader = node is self
        logging.info(f"Leader adopted: {node or self}, I am the leader: {node is self}")

    def adopt_network(self, node: ChordReference) -> None:
        logging.info(f"Notifying {node.ip} that I am not alone...")

        self.sucs = node
        self.pred = node
        # Update replication with new sucs

        logging.info(f"Node {node.ip} notified {self.ip} that I am not alone")

    def join(self, node: Optional[ChordReference] = None) -> None:
        if node:
            logging.info(f"Joining to {node.ip}...")
            if not node.is_alive:
                raise Exception(f"There is no node using the address {node.ip}")

            self.pred = None
            # self.predpred = None
            self.sucs = node.get_sucs(self.id)
            self.adopt_leader(node.leader)

            if self.sucs.id == self.sucs.sucs.id:
                self.pred = self.sucs
                # self.predpred = self
                self.sucs.adopt_network(self)
        else:
            logging.info("Joining as the first node...")
            self.sucs = self
            self.pred = None
            # self.predpred = None
            self.adopt_leader()

        logging.info(f"Node {self.ip} joined the network")

    def send_request_message(
        self,
        node: ChordReference,
        header: Tuple[str, str, List[str]],
        data: Dict[str, Any],
        port: int,
    ) -> str:
        """Send a request message to the specified node and return the response."""
        logging.info(f"Sending request message to {node.ip}:{port}")
        header_str = header_data(*header)
        message = json.dumps({"header": header_str, "data": data})
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((node.ip, port))
            sock.sendall(message.encode("utf-8"))
            response = sock.recv(1024)
        logging.info(f"Sent request to {node.ip}:{port}, received response")
        return response.decode("utf-8")

    # endregion

    # region Threading Methods
    def _stabilize(self) -> None:
        time.sleep(WAIT_CHECK * START_MOD)

        while True:
            time.sleep(WAIT_CHECK * STABLE_MOD)
            if self.sucs.id == self.id:
                continue

            logging.info("Checking stability...")

            node = self.sucs.pred if self.sucs.is_alive else self._get_other_sucs()

            if node:
                if node.id == self.id:
                    logging.info("Already stable")
                else:
                    logging.warning(f"Stabilizing...")
                    if node and in_between(node.id, self.id, self.sucs.id):
                        self.sucs = node
                        # update replication with new sucs

                    self.sucs.pred = self
            else:
                logging.info("I am alone...")
                self.sucs = self
                self.pred = None
                self.adopt_leader()

            logging.info("Stability check complete")

    def _leader_checker(self) -> None:
        time.sleep(WAIT_CHECK * START_MOD)

        while True:
            time.sleep(WAIT_CHECK * STABLE_MOD)
            if not self.leader:
                continue

            logging.info("Checking leader status...")
            if not self.leader.is_alive:
                self.leader = None
                logging.error("Leader is dead")
                continue

            other = self.leader.leader
            if not other or other.id != self.leader.id:
                logging.warning("Leader is not the same as the node")
                self.leader = None
                continue

            logging.info(f"Leader {self.leader.ip} is alive")

    def _fix_fingers(self, remain: int = 0) -> None:
        time.sleep(WAIT_CHECK * START_MOD)

        while True:
            logging.info("Fixing fingers...")
            for i in range(remain, remain + BATCH_SIZE):
                start = (self.id + 2**i) % (2**SHA_1)
                self.finger_table[i] = self.get_sucs(start)
            remain = (remain + BATCH_SIZE) % SHA_1
            logging.info("Finger fix complete")
            time.sleep(WAIT_CHECK)

    # endregion

    def run(self) -> None:
        # Start threads
        threading.Thread(target=self._stabilize, daemon=True).start()
        threading.Thread(target=self._leader_checker, daemon=True).start()
        threading.Thread(target=self._fix_fingers, daemon=True).start()
        self._start_listening()
