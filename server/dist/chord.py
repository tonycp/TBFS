from __future__ import annotations
from typing import List, Optional, Dict, Union

import threading, socket
import time, logging, json

from data.const import *
from logic.handlers import *
from logic.configurable import Configurable

from .chord_reference import ChordReference, in_between

__all__ = ["ChordNode"]


class ChordNode(ChordReference):
    _successor: ChordReference
    _predecessor: Optional[ChordReference]
    _leader: Optional[ChordReference]
    _im_the_leader: bool
    _in_election: bool

    def __init__(self, config: Optional[Configurable] = None):
        config = config or Configurable()
        ChordReference.__init__(self, config)

        self.successor: ChordReference = self
        self.leader: Optional[ChordReference] = self
        self.predecessor: Optional[ChordReference] = None
        self.finger_table: List[Optional[ChordReference]] = [self] * SHA_1
        self.im_the_leader: bool = True
        self.in_election: bool = False

            # region Properties Methods
    @property
    def successor(self) -> ChordReference:
        return self._successor

    @property
    def predecessor(self) -> ChordReference:
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

    @successor.setter
    def successor(self, node: ChordReference):
        self._successor = node

    @predecessor.setter
    def predecessor(self, node: ChordReference):
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
    def _closest_preceding_node(self, node_id: int) -> ChordReference:
        for finger_node in reversed(self.finger_table):
            if finger_node and in_between(finger_node.id, self.id, node_id):
                return finger_node
        return self

    def _find_successor(self, node_id: int) -> ChordReference:
        if self.id == node_id:
            return self

        if in_between(node_id, self.id, self.successor.id):
            return self.successor

        node = self._closest_preceding_node(node_id)
        if node != self:
            return node._find_successor(node_id)
        return self.successor

    def _find_predecessor(self, node_id: int) -> ChordReference:
        node = self
        while not in_between(node_id, node.id, node.successor.id):
            node = node.successor
        return node

    # endregion

    # region Notification Methods
    def adopt_leader(self, node: Optional[ChordReference] = None) -> None:
        logging.info(f"Adopting leader: {node.ip if node else 'self'}")
        self.leader = node or self
        self.im_the_leader = node is self
        logging.info(f"Leader adopted: {self.leader.ip}, I am the leader: {self.im_the_leader}")

    def join(self, node: Optional[ChordReference] = None) -> None:
        if node:
            logging.info(f"Joining to {node.ip}...")
            if not node.is_alive:
                raise Exception(f"There is no node using the address {node.ip}")

            self.predecessor = None
            # self.predpred = None
            self.successor = node._find_successor(self.id)
            self.adopt_leader(node.leader)

            if self.successor.id == self.successor.successor.id:
                self.predecessor = self.successor
                # self.predpred = self
                self.successor.not_alone_notify(self)
        else:
            logging.info("Joining as the first node...")
            self.successor = self
            self.predecessor = None
            # self.predpred = None
            self.adopt_leader()

        logging.info(f"Node {self.ip} joined the network")

    def notify(self, node: ChordReference) -> None:
        if node.id == self.id:
            return
        logging.info(f"Notifying {node.ip}...")
        if self.predecessor is None:
            self.predecessor = node
            # self.predpred = node.pred
            # pull replication to predecessor
            # self.update_replication(False, True)

        elif node.is_alive and in_between(node.id, self.predecessor.id, self.id):
            self.predecessor = node
            # self.predpred = self.pred
            # push replication delegation to predecessor
            # self.update_replication(True, False)
        logging.info(f"Node {node.ip} notified {self.ip}")

    def reverse_notify(self, node: ChordReference) -> None:
        logging.info(f"Reversing notifying {node.ip}...")
        self.successor = node
        logging.info(f"Node {node.ip} reversed notified {self.ip}")

    def not_alone_notify(self, node: ChordReference) -> None:
        logging.info(f"Notifying {node.ip} that I am not alone...")

        self.successor = node
        self.predecessor = node
        # self.predpred = self
        # Update replication with new successor
        # self.update_replication(delegate_data=True, case_2=True)

        logging.info(f"Node {node.ip} notified {self.ip} that I am not alone")

    # endregion

    # region Threading Methods
    def _stabilize(self) -> None:
        time.sleep(WAIT_CHECK * START_MOD)

        while True:
            logging.info("Checking stability...")
            if self.successor.id == self.id:
                time.sleep(WAIT_CHECK * STABLE_MOD)
                continue

            if self.successor.is_alive:
                x = self.successor.predecessor
                if x and x.id == self.id:
                    logging.info("Already stable")
                else:
                    logging.warning(f"Stabilizing...")
                    if x and in_between(x.id, self.id, self.successor.id):
                        self.successor = x
                        # update replication with new successor
                        # self.update_replication(False, True, False, False)

                    self.successor.notify(self)

                # if self.pred and self.pred.check_node():
                #     self.predpred = self.pred.pred
            else:
                logging.error("No successor found, waiting for predecessor check...")
            logging.info("Stability check complete")
            time.sleep(WAIT_CHECK * STABLE_MOD)

    def _check_predecessor(self) -> None:
        time.sleep(WAIT_CHECK * START_MOD)

        while True:
            logging.info("Checking predecessor...")
            if self.successor is self:
                time.sleep(WAIT_CHECK * STABLE_MOD)
                continue

            if self.predecessor:
                if not self.predecessor.is_alive:
                    logging.warning(f"Predecessor {self.predecessor.ip} is dead")
                    two_in_a_row = False
                    predpred = self.predecessor.predecessor
                    if predpred.is_alive:
                        self.predecessor = predpred
                        # self.predpred = self.predpred.pred
                    else:
                        self.predecessor = self._find_predecessor(predpred.id)
                        # self.predpred = self.predpred.pred
                        two_in_a_row = True

                    if self.predecessor.id == self.id:
                        self.successor = self
                        self.predecessor = None
                        # self.predpred = None
                        if two_in_a_row:
                            pass
                            # self.update_replication(
                            #     False, False, True, assume_predpred=self.ip
                            # )
                        else:
                            continue
                            # self.update_replication(False, False, True)

                    self.predecessor.reverse_notify(self)

                    # # Assume
                    # if two_in_a_row:
                    #     # Assume pred pred data
                    #     self.update_replication(
                    #         False, False, True, assume_predpred=self.pred.ip
                    #     )
                    # else:
                    #     self.update_replication(False, False, True)
                else:
                    logging.info(f"Predecessor {self.predecessor.ip} is alive")
            else:
                logging.warning("No predecessor found")
            logging.info("Predecessor check complete")
            time.sleep(WAIT_CHECK * STABLE_MOD)

    def _leader_checker(self) -> None:
        time.sleep(WAIT_CHECK * START_MOD)

        while True:
            logging.info("Checking leader status...")
            if self.leader:
                if not self.leader.is_alive:
                    self.leader = None
                    logging.error("Leader is dead")
                else:
                    logging.info(f"Leader {self.leader.ip} is alive")
            logging.info("Leader status check complete")
            time.sleep(WAIT_CHECK * STABLE_MOD)

    def _fix_fingers(self, remain: int = 0) -> None:
        time.sleep(WAIT_CHECK * START_MOD)

        while True:
            logging.info("Fixing fingers...")
            for i in range(remain, remain + BATCH_SIZE):
                start = (self.id + 2**i) % (2**SHA_1)
                self.finger_table[i] = self._find_successor(start)
            remain = (remain + BATCH_SIZE) % SHA_1
            logging.info("Finger fix complete")
            time.sleep(WAIT_CHECK)

    # endregion

    def run(self) -> None:
        # Start threads
        threading.Thread(target=self._stabilize, daemon=True).start()
        threading.Thread(target=self._check_predecessor, daemon=True).start()
        threading.Thread(target=self._leader_checker, daemon=True).start()
        threading.Thread(target=self._fix_fingers, daemon=True).start()
