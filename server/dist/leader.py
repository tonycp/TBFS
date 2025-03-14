import asyncio
from typing import Any, List, Optional, Dict, Tuple

import json, logging, time
import selectors, socket, threading

from logic.configurable import Configurable
from .leader_reference import LeaderReference
from servers.server import Server
from logic.handlers import *
from data.const import *

from .chord import ChordNode
from .chord_reference import ChordReference

__all__ = ["ChordLeader"]


class ChordLeader(LeaderReference, ChordNode, Server):
    _leader: Optional[ChordReference]
    _im_the_leader: bool
    _in_election: bool

    def __init__(self, config: Optional[Configurable] = None):
        config = config or Configurable()
        LeaderReference.__init__(self, config)
        ChordNode.__init__(self, config)
        self._subscribe_read_udp_port(DEFAULT_ELECTION_PORT)

        self.leader: ChordReference = self
        self.im_the_leader: bool = True
        self.in_election: bool = False

    # region Properties
    @property
    def leader(self) -> ChordReference:
        return self._leader

    @property
    def im_the_leader(self) -> bool:
        return self._im_the_leader

    @property
    def in_election(self) -> bool:
        return self._in_election

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

    # region Server Methods
    def _is_leader_request(self, addr: Tuple[str, int]) -> bool:
        """Check if the request is from the leader based on the endpoint."""
        return self.leader and addr[0] == self.leader.ip

    # endregion

    # region Server UDP
    def _subscribe_read_udp_port(self, port: int) -> socket.socket:
        """Subscribe to a specific port for incoming requests."""
        multicast_ip = self._config[MCAST_ADDR_KEY]
        data = (self._process_udp_request, port)
        membership = socket.inet_aton(multicast_ip) + socket.inet_aton("0.0.0.0")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", port))

        sock.setblocking(False)
        self.selector.register(sock, selectors.EVENT_READ, data)
        logging.info(f"Subscribed to port {port}")
        return sock

    def _process_udp_request(
        self,
        sock: socket.socket,
        mask: int,
        ori_port: int,
    ) -> None:
        """Process incoming UDP requests."""
        try:
            message, addr = sock.recvfrom(1024)
            ori_addr = (addr[0], ori_port)
            if self.ip == addr[0] or self.ip == "127.0.0.1":
                return
            logging.info(f"Received UDP message from {addr}")
            result = self._process_mesage(message, ori_addr)
            logging.info(f"Processed UDP result: {result}")
        except BlockingIOError as e:
            logging.warning(f"Resource temporarily unavailable: {addr} - {e}")
        except ValueError as e:
            logging.error(f"Error processing UDP message from {addr}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    # endregion

    # region Chord Methods
    def adopt_leader(self, node: Optional[ChordReference] = None) -> None:
        logging.info(f"Adopting leader: {node.ip if node else 'self'}")
        self.leader = node or self
        self.im_the_leader = node is self
        logging.info(f"Leader adopted: {node or self}, I am the leader: {node is self}")

    def join(self, node: Optional[LeaderReference] = None) -> None:
        """Join the network and adopt the leader."""
        if self.im_the_leader:
            nodes = [n for n in self.finger_table if n and n.id != self]
            if nodes:
                asyncio.run(join_nodes(node, nodes))

        ChordNode.join(self, node)
        if not node:
            self.adopt_leader()
        elif node.leader:
            self.adopt_leader(node.leader)

    # endregion

    # region Message Methods
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

    def send_multicast_notification(self, port: int, data: str) -> None:
        """Multicast the leader information to all nodes."""
        multicast_ip = self._config[MCAST_ADDR_KEY]

        logging.info("Sending multicast notification...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.sendto(data.encode("utf-8"), (multicast_ip, port))
            time.sleep(WAIT_CHECK)

    def send_election_message(
        self,
        elect: ELECTION,
        port: int,
        data: Dict[str, Any],
    ) -> None:
        """Send an election message to the specified port."""
        logging.info(f"Sending election message: {elect.name}")
        header = ELECTION_COMMANDS[elect]
        message = json.dumps({"header": header, "data": data})
        self.send_multicast_notification(port, message)

    # endregion

    # region Threading Methods
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

    def _multicast_server(self) -> None:
        multicast_ip, port = self._config[MCAST_ADDR_KEY], DEFAULT_BROADCAST_PORT
        membership = socket.inet_aton(multicast_ip) + socket.inet_aton("0.0.0.0")
        params = (port, json.dumps({"ip": self.ip}))
        send_func = self.send_multicast_notification

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", port))

        sock.settimeout(WAIT_CHECK)
        logging.info(f"Starting the multicast server on {self.ip}...")

        while True:
            time.sleep(WAIT_CHECK * BROADCAST_MOD)
            if self.in_election:
                continue

            if self.im_the_leader:
                threading.Thread(target=send_func, args=params).start()

            conn, addr = sock.recvfrom(1024)
            data = json.loads(conn.decode("utf-8"))
            ip = self.leader.ip

            if ip == addr[0] or ip == data["ip"] or ip == "127.0.0.1":
                continue

            ref_config = self._config.copy_with_updates({HOST_KEY: data["ip"]})
            node = ChordReference(ref_config)

            if self.closest_preceding_node(node.id) != self:
                continue

            logging.info(f"Received a multicast message: {conn} from {addr}")
            node.join(self)

    def _election_loop(self) -> None:
        port, data = DEFAULT_ELECTION_PORT, {"id": self.id, "ip": self.ip}
        counter = 0
        while True:
            if not self.leader and not self.in_election:
                self.send_election_message(ELECTION.START, port, data)
                logging.info("Starting leader election...")
                self.in_election = True
                self.leader = None
            elif self.in_election:
                counter += 1
                logging.info(f"Waiting for election result... {counter}")
                if counter == ELECTION_TIMEOUT:
                    if not self.leader and not self.im_the_leader:
                        self.im_the_leader = True
                        self.leader = self
                        self.in_election = False
                        self.send_election_message(ELECTION.WINNER, port, data)
                        logging.info("I am the new leader")
                    counter = 0
                    self.in_election = False
            else:
                logging.info(f"Current leader ip: {self.leader.ip}")
                time.sleep(WAIT_CHECK)
            time.sleep(WAIT_CHECK * ELECTION_MOD)

    # endregion

    def run(self) -> None:
        # Start threads
        threading.Thread(target=self._leader_checker, daemon=True).start()
        threading.Thread(target=self._multicast_server, daemon=True).start()
        threading.Thread(target=self._election_loop, daemon=True).start()
        ChordNode.run(self)


async def join_nodes(
    node: Optional[ChordReference], nodes: List[Optional[ChordReference]]
) -> None:
    async def join_async(internal: Optional[ChordReference], sucs):
        await asyncio.to_thread(internal.join(sucs))

    task = []
    for internal in nodes:
        sucs = node.get_sucs(internal.id)
        task.append(join_async(internal, sucs))
    await asyncio.gather(*task)
