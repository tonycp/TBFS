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

    def send_broadcast_notification(self) -> str:
        """Broadcast the leader information to all nodes."""
        data = json.dumps({"ip": self.ip})
        port = DEFAULT_BROADCAST_PORT
        multicast_ip = self._config[MCAST_ADDR_KEY]

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.sendto(data.encode("utf-8"), (multicast_ip, port))
            time.sleep(WAIT_CHECK)

    def _is_node_request(self, last_endpoint: str) -> bool:
        node_port = self._config.get(NODE_PORT_KEY)
        return last_endpoint.endswith(f":{node_port}")

    def _is_leader_request(self, last_endpoint: str) -> bool:
        """Check if the request is from the leader based on the endpoint."""
        return last_endpoint.endswith(f"{self.leader.ip}:{self.leader.data_port}")

    def _solver_request(
        self, header_str: str, rest_mesg: List[bytes], last_endpoint: str
    ) -> str:
        """Solve the request and return the result."""
        logging.info(f"Received a message from: {last_endpoint}")

        while not self.leader.is_alive:
            logging.warning("Leader is dead, waiting for new leader...")
            time.sleep(WAIT_CHECK * START_MOD)

        is_leader_req = self._is_leader_request(last_endpoint)
        is_node_req = self._is_node_request(last_endpoint)

        if not self.im_the_leader and not is_leader_req:
            node, port = self.leader, self.data_port
            return self.send_request_message(node, header_str, rest_mesg, port)

        header = parse_header(header_str)
        data = rest_mesg[0].decode("utf-8")

        if is_leader_req or is_node_req:
            return handle_request(header, data)
        return self._handle_leader_request(header, data)

    def _handle_leader_request(
        self, header: Tuple[str, str, Dict[str, Any]], data: Dict[str, Any]
    ) -> str:
        """Handle the request as the leader and aggregate responses from other nodes."""
        command, func, dataset = header
        func = handlers_lider_conv(func)
        header = command, func, dataset

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
            time.sleep(WAIT_CHECK * START_MOD)
            if not self.im_the_leader:
                continue

            threading.Thread(target=self.send_broadcast_notification).start()
            conn, addr = sock.recvfrom(1024)

            if self.ip == addr[0] or self.ip == "127.0.0.1":
                continue

            logging.info(f"Received a multicast message: {conn} from: {addr}")

            data = json.loads(conn.decode("utf-8"))

            ref_config = self._config.copy_with_updates({HOST_KEY: data["ip"]})
            ChordReference(ref_config, self.context).join(self)
            self.im_the_leader = False
            self.leader = None

    def run(self) -> None:
        # Start threads
        threading.Thread(target=self._multicast_server, daemon=True).start()
        ChordNode.run(self)
        Server.run(self)
