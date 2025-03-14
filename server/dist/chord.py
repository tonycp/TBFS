from __future__ import annotations
from typing import Any, List, Optional

import threading, asyncio
import time, logging

from logic.configurable import Configurable
from logic.handlers import *
from data.const import *
from servers.server import Server

from .chord_reference import ChordReference
from .utils import in_between

__all__ = ["ChordNode"]


class ChordNode(ChordReference, Server):
    _successor: ChordReference
    _predecessor: Optional[ChordReference]

    def __init__(self, config: Optional[Configurable] = None):
        config = config or Configurable()
        ChordReference.__init__(self, config)

        self.leader: Optional[ChordReference] = self
        self.sucs: Optional[ChordReference] = self
        self.pred: Optional[ChordReference] = self
        self.finger_table: List[Optional[ChordReference]] = [self] * SHA_1

        Server.__init__(self, config)
        self._subscribe_read_port(self._config[NODE_PORT_KEY])

    # region Properties
    @property
    def sucs(self) -> ChordReference:
        return self._successor

    @property
    def pred(self) -> ChordReference:
        return self._predecessor

    @property
    def is_alive(self) -> bool:
        return True

    @sucs.setter
    def sucs(self, node: ChordReference):
        self._successor = node

    @pred.setter
    def pred(self, node: ChordReference):
        self._predecessor = node
        self.replication(node, "pred.db")

    # endregion

    # region Findings Methods
    def _get_other_sucs(self):
        for node in self.finger_table:
            if node and node.id != self.sucs.id and node.is_alive:
                return node

    def closest_preceding_node(self, node_id: int) -> ChordReference:
        for finger_node in reversed(self.finger_table):
            if (
                finger_node
                and in_between(finger_node.id, self.id, node_id)
                and finger_node.is_alive
            ):
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

    # endregion

    # region Notify Methods
    def join(self, node: Optional[ChordReference] = None) -> None:
        if node:
            logging.info(f"Joining to {node.ip}...")
            if not node.is_alive:
                raise Exception(f"There is no node using the address {node.ip}")

            self.sucs = node.get_sucs(self.id)
            self.pred = self.sucs.pred
            self.sucs.pred = self
            self.pred.sucs = self
        else:
            logging.info("Joining as the first node...")
            self.sucs.pred = self.pred
            self.pred.sucs = self.sucs
            self.sucs = self
            self.pred = self

        logging.info(f"Node {self.ip} joined the network")

    def replication(self, node: ChordReference, key: str) -> None:
        logging.info(f"Sending replication to {node.ip}")
        data = self.get_replication()
        node.set_replication(key, data)

    # endregion

    # region Threading Methods
    def _stabilize(self) -> None:
        time.sleep(WAIT_CHECK * START_MOD)

        while True:
            time.sleep(WAIT_CHECK * STABLE_MOD)
            if self.sucs.id == self.id:
                continue

            logging.info("Checking stability...")

            if self.sucs.is_alive:
                logging.info("Already stable")
                continue

            node = self._get_other_sucs()
            if node:
                logging.info(f"Changing successor to {node.ip}")
                self.sucs = node
                self.replication(node, "sucs.db")
                node.pred = self
            else:
                logging.info("I am alone...")
                self.sucs = self
                self.pred = self
            logging.info("Stability check complete")

    async def _fix_fingers(self, remain: int = 0) -> None:
        async def _get_sucs_async(index: int, start: int) -> None:
            self.finger_table[index] = await asyncio.to_thread(self.get_sucs, start)

        await asyncio.sleep(WAIT_CHECK * START_MOD)

        while True:
            logging.info("Fixing fingers...")
            tasks = []
            for i in range(remain, remain + BATCH_SIZE):
                start = (self.id + 2**i) % (2**SHA_1)
                tasks.append(_get_sucs_async(i, start))
            await asyncio.gather(*tasks)
            remain = (remain + BATCH_SIZE) % SHA_1
            logging.info("Finger fix complete")
            await asyncio.sleep(WAIT_CHECK)

    # endregion

    def run(self) -> None:
        # Start threads
        threading.Thread(target=self._stabilize, daemon=True).start()
        asyncio.run(self._fix_fingers())
        self._start_listening()
