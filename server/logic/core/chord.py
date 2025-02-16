import multiprocessing, threading, zmq
import time, logging, os

from typing import List, Optional, Dict, Union
from __future__ import annotations

from .server import Server
from .chord_reference import ChordReference
from .const import *

__all__ = ["ChordNode"]


class ChordNode(Server, ChordReference):
    def __init__(self, config: Optional[Dict[str, Optional[Union[str, int]]]] = None):
        ChordNode._check_default(config or {})
        Server.__init__(self, config)

        self.successor: ChordReference = self
        self.leader: Optional[ChordReference] = None
        self.predecessor: Optional[ChordReference] = None
        self.finger_table: List[Optional[ChordReference]] = [self] * SHA_1
        self.im_the_leader: bool = True
        self.in_election: bool = False

        chord_ref = ChordReference.get_config(self._config, self.context)
        ChordReference.__init__(self, **chord_ref)

    @staticmethod
    def _check_default(
        config: Dict[str, Optional[Union[str, int]]]
    ) -> Dict[str, Optional[Union[str, int]]]:
        """Check and set default values for the configuration."""
        Server._check_default(config)

        default_config = {
            NODE_PORT_KEY: int(os.getenv(NODE_PORT_ENV_KEY, DEFAULT_NODE_PORT)),
            MCAST_ADDR_KEY: os.getenv(MCAST_ADDR_ENV_KEY, DEFAULT_MCAST_ADDR),
        }

        for key, value in default_config.items():
            config.setdefault(key, value)
        return config

    # region Finding Methods
    def _closest_preceding_node(self, node_id: int) -> ChordReference:
        for finger_node in reversed(self.finger_table):
            if finger_node and self.in_between(finger_node.id, node_id):
                return finger_node
        return self

    def _find_successor(self, node_id: int) -> ChordReference:
        if self.id == node_id:
            return self

        if self.in_between(node_id, self.successor.id):
            return self.successor

        node = self._closest_preceding_node(node_id)
        if node != self:
            return node._find_successor(node_id)
        return self.successor

    def _find_predecessor(self, node_id: int) -> ChordReference:
        node = self
        while not node.in_between(node_id, node.successor.id):
            node = node.successor
        return node

    # endregion

    # region Notification Methods
    def adopt_leader(self, node: Optional[ChordReference] = None):
        self.leader = node or self
        self.im_the_leader = node is self

    def join(self, node: Optional[ChordReference] = None):
        if node:
            logging.info(f"❕ Joining to {node.id}...")
            if not node.check_node():
                raise Exception(f"There is no node using the address {node.ip}")

            self.predecessor = None
            self.successor = node._find_successor(self.id)
            self.adopt_leader(node.leader)

            if self.successor.id == self.successor.successor.id:
                self.predecessor = self.successor
                # self.predpred = self.ref
                self.successor.not_alone_notify(self)
        else:
            logging.info("❕ Joining as the first node...")
            self.successor = self
            self.predecessor = None
            # self.predpred = None
            self.adopt_leader()

        logging.info(f"✔️ Node {self.id} joined the network")

    def notify(self, node: ChordReference):
        logging.info(f"❕ Notifying {node.id}...")
        if node.id == self.id:
            return

        if self.predecessor is None:
            self.predecessor = node

            # self.pred = node
            # self.predpred = node.pred
            # self.update_replication(False, True)

            # pull replication to predecessor
        elif node.is_alive and self.predecessor.in_between(node.id, self.id):
            self.predecessor = node

            # self.predpred = self.pred
            # self.pred = node
            # self.update_replication(True, False)

            # push replication delegation to predecessor

        logging.info(f"✔️ Node {node.id} notified {self.id}")

    def reverse_notify(self, node: ChordReference):
        logging.info(f"❕ Reversing notifying {node.id}...")

        self.successor = node

        logging.info(f"✔️ Node {node.id} reversed notified {self.id}")

    def not_alone_notify(self, node: ChordReference):
        logging.info(f"❕ Notifying {node.id} that I am not alone...")

        self.successor = node
        self.predecessor = node
        # Update replication with new successor
        # self.update_replication(delegate_data=True, case_2=True)

        logging.info(f"✔️ Node {node.id} notified {self.id} that I am not alone")

    # endregion

    # region Broadcast Methods
    def zmq_PUB(self, header: str, data: str, mcast_addr: str, port: int):
        message = [header.encode("utf-8"), data.encode("utf-8")]
        s = self.context.socket(zmq.PUB)
        s.bind(f"tcp://{mcast_addr}:{port}")
        s.send_multipart(message)
        s.close()

    def send_PUB_message(self, header, data):
        mcast_addr = self._config[MCAST_ADDR_KEY]
        port = self._config[PORT_KEY]
        func = self.zmq_PUB
        multiprocessing.Process(
            target=func, args=(header, data, mcast_addr, port)
        ).start()

    # endregion

    # region Threading Methods
    def _stabilize(self):
        while True:
            if self.successor is self:
                time.sleep(WAIT_CHECK * STABLE_MOD)
                continue

            logging.info("🔵 Checking stability...")
            if self.successor.is_alive:
                x = self.successor.predecessor
                if x.id != self.id:
                    logging.warning(f"🟡 Stabilizing: {self.id} -> {x.id}")
                    if x and self.in_between(x.id, self.successor.id):
                        self.successor = x

                        # pull replication to successor

                    self.successor.notify(self)
                else:
                    logging.info("🟢 Stabilized")
            else:
                logging.error("🔴 No successor found, waiting for predecesor check...")
            time.sleep(WAIT_CHECK * STABLE_MOD)

    def _check_predecessor(self):
        while True:
            if self.successor is self:
                time.sleep(WAIT_CHECK * STABLE_MOD)
                continue

            logging.info("🔵 Checking predecessor...")
            if self.predecessor:
                if not self.predecessor.is_alive:
                    logging.warning(f"🟡 Predecessor {self.predecessor.id} is dead")
                else:
                    logging.info(f"🟢 Predecessor {self.predecessor.id} is alive")
            else:
                logging.warning("🔴 No predecessor found")
                self.predecessor = None
                self.successor = self
            time.sleep(WAIT_CHECK * STABLE_MOD)

    def _election_loop(self):
        socket = self.context.socket(zmq.SUB)
        url = f"tcp://{self._config[HOST_KEY]}:{self._config[NODE_PORT_KEY]}"
        self._connect_socket(socket, url, zmq.POLLIN)
        socket.setsockopt_string(zmq.SUBSCRIBE, "")

        start = Server.header_data(**ELECTION_COMMANDS[ELECTION.START])
        winner = Server.header_data(**ELECTION_COMMANDS[ELECTION.WINNER])
        data = {"id": self.id}

        counter = 0
        while True:
            if not self.leader and not self.in_election:
                self.send_PUB_message(start, data)
                logging.info("🔶 Starting leader election...")
                self.in_election = True
                self.leader = None
            elif self.in_election:
                counter += 1
                if counter == ELECTION_TIMEOUT:
                    if not self.leader and self.im_the_leader:
                        self.im_the_leader = True
                        self.leader = self.id
                        self.in_election = False
                        self.send_PUB_message(winner, data)
                        logging.info(f"💠 I am the new leader")
                    counter = 0
                    self.in_election = False
            else:
                logging.info(f"🔷 Leader: {self.leader}")
            logging.info(f"waiting... {counter}")
            time.sleep(WAIT_CHECK * ELECTION_MOD)

    def _fix_fingers(self, remain: int = 0):
        while True:
            for i in range(remain, remain + BATCH_SIZE):
                start = (self.id + 2**i) % (2**SHA_1)
                self.finger_table[i] = self._find_successor(start)
            remain = (remain + BATCH_SIZE) % SHA_1
            time.sleep(WAIT_CHECK)

    # endregion

    def run(self):
        Server.run(self)

        # Start threads
        threading.Thread(target=self._stabilize, daemon=True).start()
        threading.Thread(target=self._check_predecessor, daemon=True).start()
        threading.Thread(target=self._start_listening, daemon=True).start()
        threading.Thread(target=self._election_loop, daemon=True).start()
        threading.Thread(target=self._leader_checker, daemon=True).start()
        threading.Thread(target=self.start_broadcast_server, daemon=True).start()
        threading.Thread(target=self._fix_fingers, daemon=True).start()
