import socket
from typing import Any, List, Optional, Dict, Tuple, Union

import threading, json, logging, time
import selectors

from dist.chord import ChordNode
from logic.configurable import Configurable
from logic.handlers import *
from data.const import *
from dist.chord_reference import ChordReference

from .server import Server

__all__ = ["ChordServer"]


class ChordServer(Server, ChordNode):
    def __init__(self, config: Optional[Configurable] = None):
        config = config or Configurable()
        ChordNode.__init__(self, config)
        Server.__init__(self, config)
        self._subscribe_read_port(self._config[NODE_PORT_KEY])

        self.is_leader_req = False
        self.is_node_req = False

    def send_multicast_notification(self) -> None:
        """Multicast the leader information to all nodes."""
        data = json.dumps({"ip": self.ip})
        port = DEFAULT_BROADCAST_PORT
        multicast_ip = self._config[MCAST_ADDR_KEY]

        logging.info("Sending multicast notification...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.sendto(data.encode("utf-8"), (multicast_ip, port))
            time.sleep(WAIT_CHECK)

    def send_request_message(
        self,
        node: ChordReference,
        header: Tuple[str, str, List[str]],
        data: List[str],
        port: int,
    ) -> str:
        """Send a request message to the specified node and return the response."""
        header_str = header_data(*header)
        message = json.dumps({"header": header_str, "data": data})
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((node.ip, port))
            sock.sendall(message.encode("utf-8"))
            response = sock.recv(1024)
        logging.info(f"Sent request to {node.ip}:{port}, received response")
        return response.decode("utf-8")

    def _is_node_request(self, addr: Tuple[str, int]) -> bool:
        node_port = self._config[NODE_PORT_KEY]
        return addr[1] == node_port

    def _is_leader_request(self, addr: Tuple[str, int]) -> bool:
        """Check if the request is from the leader based on the endpoint."""
        return addr[0] == self.leader.ip

    def _process_mesage(self, message: bytes, addr: Tuple[str, int]) -> None:
        while self.in_election or not self.leader:
            logging.warning("Waiting for new leader...")
            time.sleep(WAIT_CHECK * START_MOD)
        return Server._process_mesage(self, message, addr)

    def _solver_request(
        self,
        header: Tuple[str, str, List[str]],
        data: Dict[str, Any],
        addr: Tuple[str, int],
    ) -> str:
        """Solve the request and return the result."""
        is_leader_req = self._is_leader_request(addr)
        is_node_req = self._is_node_request(addr)

        if not self.im_the_leader and not is_leader_req:
            logging.info("Forwarding the request to the leader...")
            node, port = self.leader, self.data_port
            return self.send_request_message(node, header, data, port)

        if is_leader_req or is_node_req:
            logging.info("Handling the request as a node...")
            return Server._solver_request(self, header, data, addr)
        logging.info("Handling the request as leader...")
        return self._handle_leader_request(header, data, addr)

    def _handle_leader_request(
        self,
        header: Tuple[str, str, List[str]],
        data: Dict[str, Any],
        addr: Tuple[str, int],
    ) -> str:
        """Handle the request as the leader and aggregate responses from other nodes."""
        header[1] = handle_leader_conversion(header[1])
        return Server._solver_request(self, header, data, addr)

    def _multicast_server(self) -> None:
        multicast_ip = self._config[MCAST_ADDR_KEY]
        membership = socket.inet_aton(multicast_ip) + socket.inet_aton("0.0.0.0")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", DEFAULT_BROADCAST_PORT))

        sock.settimeout(WAIT_CHECK)
        logging.info(f"Starting the multicast server on {self.ip}...")

        while True:
            time.sleep(WAIT_CHECK * BROADCAST_MOD)
            if not self.im_the_leader or self.in_election:
                continue

            threading.Thread(target=self.send_multicast_notification).start()
            conn, addr = sock.recvfrom(1024)

            if self.ip == addr[0] or self.ip == "127.0.0.1":
                continue

            logging.info(f"Received a multicast message: {conn} from {addr}")

            data = json.loads(conn.decode("utf-8"))

            ref_config = self._config.copy_with_updates({HOST_KEY: data["ip"]})
            ChordReference(ref_config).join(self)

    def _election_loop(self) -> None:
        time.sleep(WAIT_CHECK * START_MOD)

        url = (self._config[HOST_KEY], int(self._config[NODE_PORT_KEY]))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(url)
        sock.listen(5)
        logging.info(f"Binding socket on {url}")

        sock.settimeout(WAIT_CHECK)
        counter = 0
        while True:
            if not self.leader and not self.in_election:
                self.send_election_message(ELECTION.START)
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
                        self.send_election_message(ELECTION.WINNER)
                        logging.info("I am the new leader")
                    counter = 0
                    self.in_election = False
            else:
                logging.info(f"Current leader: {self.leader.id}")
                time.sleep(WAIT_CHECK)
            time.sleep(WAIT_CHECK * ELECTION_MOD)

    def run(self) -> None:
        # Start threads
        ChordNode.run(self)
        threading.Thread(target=self._multicast_server, daemon=True).start()
        # threading.Thread(target=self._election_loop, daemon=True).start()
        self._start_listening()
