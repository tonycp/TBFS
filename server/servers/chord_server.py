import socket
from typing import Any, List, Optional, Dict, Tuple

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
        self._subscribe_read_upd_port(DEFAULT_ELECTION_PORT)

        self.is_leader_req = False
        self.is_node_req = False

    def _subscribe_read_upd_port(self, port: int) -> socket.socket:
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
        header = header_data(**ELECTION_COMMANDS[elect])
        message = json.dumps({"header": header, "data": data})
        self.send_multicast_notification(port, message)

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

    def _is_node_request(self, addr: Tuple[str, int]) -> bool:
        """Check if the request is from a node based on the port."""
        node_port = self._config[NODE_PORT_KEY]
        election_port = DEFAULT_ELECTION_PORT
        return addr[1] == node_port or addr[1] == election_port

    def _is_leader_request(self, addr: Tuple[str, int]) -> bool:
        """Check if the request is from the leader based on the endpoint."""
        return self.leader and addr[0] == self.leader.ip

    def _process_mesage(self, message: bytes, addr: Tuple[str, int]) -> None:
        is_node_req = self._is_node_request(addr)
        while not is_node_req and (self.in_election or not self.leader):
            logging.warning("Waiting for new leader...")
            time.sleep(WAIT_CHECK * START_MOD)
        return Server._process_mesage(self, message, addr)

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

    def _solver_request(
        self,
        header: Tuple[str, str, List[str]],
        data: Dict[str, Any],
        addr: Tuple[str, int],
    ) -> str:
        """Solve the request and return the result."""
        is_leader_req = self._is_leader_request(addr)
        is_node_req = self._is_node_request(addr)

        if is_leader_req or is_node_req:
            logging.info("Handling the request as a node...")
            return Server._solver_request(self, header, data, addr)
        elif not self.im_the_leader:
            logging.info("Forwarding the request to the leader...")
            node, port = self.leader, self.data_port
            return self.send_request_message(node, header, data, port)
        logging.info("Handling the request as leader...")
        return self._handle_leader_request(header, data, addr)

    def _handle_leader_request(
        self,
        header: Tuple[str, str, List[str]],
        data: Dict[str, Any],
        addr: Tuple[str, int],
    ) -> str:
        """Handle the request as the leader and aggregate responses from other nodes."""
        data["header"] = header
        header[1] = handle_leader_conversion(header[1])
        return Server._solver_request(self, header, data, addr)

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
            if not self.im_the_leader or self.in_election:
                continue

            threading.Thread(target=send_func, args=params).start()
            conn, addr = sock.recvfrom(1024)

            if self.ip == addr[0] or self.ip == "127.0.0.1":
                continue

            logging.info(f"Received a multicast message: {conn} from {addr}")

            data = json.loads(conn.decode("utf-8"))

            ref_config = self._config.copy_with_updates({HOST_KEY: data["ip"]})
            ChordReference(ref_config).join(self)

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

    def run(self) -> None:
        # Start threads
        ChordNode.run(self)
        threading.Thread(target=self._multicast_server, daemon=True).start()
        threading.Thread(target=self._election_loop, daemon=True).start()
        self._start_listening()
