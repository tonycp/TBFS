import socket
from typing import Any, List, Optional, Dict, Tuple, Union

import threading, json, logging, time

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

    def send_multicast_notification(self) -> str:
        """Multicast the leader information to all nodes."""
        data = json.dumps({"ip": self.ip})
        port = DEFAULT_BROADCAST_PORT
        multicast_ip = self._config[MCAST_ADDR_KEY]

        logging.info("Sending multicast notification...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.sendto(data.encode("utf-8"), (multicast_ip, port))
            time.sleep(WAIT_CHECK)

    def _is_node_request(self, last_endpoint: str) -> bool:
        node_port = self._config[NODE_PORT_KEY]
        return last_endpoint.endswith(f":{node_port}")

    def _is_leader_request(self, last_endpoint: str) -> bool:
        """Check if the request is from the leader based on the endpoint."""
        return last_endpoint[0] == self.leader.ip

    def _solver_request(self, header: dict, data: dict, addr: str) -> str:
        """Solve the request and return the result."""
        logging.info(f"Received a message from: {addr}")

        while self.in_election or not self.leader:
            logging.warning("Waiting for new leader...")
            time.sleep(WAIT_CHECK * START_MOD)

        is_leader_req = self._is_leader_request(addr)
        is_node_req = self._is_node_request(addr)

        if not self.im_the_leader and not is_leader_req:
            logging.info("Forwarding the request to the leader...")
            node, port = self.leader, self.data_port
            return self.send_request_message(node, header, data, port)

        if is_leader_req or is_node_req:
            logging.info("Handling the request as a node...")
            return handle_request(header, data)
        logging.info("Handling the request as leader...")
        return self._handle_leader_request(header, data)

    def _handle_leader_request(
        self, header: Dict[str, Any], data: Dict[str, Any]
    ) -> str:
        """Handle the request as the leader and aggregate responses from other nodes."""
        header["function"] = handlers_lider_conv(header["function"])
        handle_request(header, data)

    def _multicast_server(self):
        multicast_ip = self._config[MCAST_ADDR_KEY]
        membership = socket.inet_aton(multicast_ip) + socket.inet_aton("0.0.0.0")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", DEFAULT_BROADCAST_PORT))

        sock.settimeout(WAIT_CHECK)
        logging.info(f"Starting the multicast server in {self.ip}...")

        while True:
            time.sleep(WAIT_CHECK * START_MOD * START_MOD)
            if not self.im_the_leader or self.in_election:
                continue

            threading.Thread(target=self.send_multicast_notification).start()
            conn, addr = sock.recvfrom(1024)

            if self.ip == addr[0] or self.ip == "127.0.0.1":
                continue

            logging.info(f"Received a multicast message: {conn} from: {addr}")

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
                logging.info(f"waiting... {counter}")
                if counter == ELECTION_TIMEOUT:
                    if not self.leader and not self.im_the_leader:
                        self.im_the_leader = True
                        self.leader = self
                        self.in_election = False
                        self.send_election_message(ELECTION.WINNER)
                        logging.info(f"I am the new leader")
                    counter = 0
                    self.in_election = False
            else:
                logging.info(f"Leader: {self.leader.id}")
                time.sleep(WAIT_CHECK)
            time.sleep(WAIT_CHECK * ELECTION_MOD)

    def run(self) -> None:
        # Start threads
        ChordNode.run(self)
        threading.Thread(target=self._multicast_server, daemon=True).start()
        threading.Thread(target=self._election_loop, daemon=True).start()
        Server.run(self)
