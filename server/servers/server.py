from typing import List, Optional

import time, zmq, json, logging, threading

from data.const import *
from logic.handlers import *
from logic.configurable import Configurable


__all__ = ["Server"]


class Server:
    def __init__(self, config: Optional[Configurable] = None):
        self._config = config or Configurable()
        url = f"{self._config[PROTOCOL_KEY]}://{self._config[HOST_KEY]}:{self._config[PORT_KEY]}"
        self.poller = zmq.Poller()
        self.context = zmq.Context()
        socket = self.context.socket(zmq.REP)
        self._bind_socket(socket, url, zmq.POLLIN)

    def _bind_socket(
        self,
        socket: zmq.Socket,
        url: str,
        poller_flags: int = zmq.POLLOUT | zmq.POLLIN,
    ) -> None:
        """Bind the socket to the specified URL and register it with the poller."""
        socket.bind(url)
        self.poller.register(socket, poller_flags)
        logging.info(f"Binding socket on {url}")

    def _connect_socket(
        self,
        socket: zmq.Socket,
        url: str,
        poller_flags: int = zmq.POLLOUT | zmq.POLLIN,
    ) -> None:
        """Connect the socket to the specified URL and register it with the poller."""
        socket.connect(url)
        self.poller.register(socket, poller_flags)
        logging.info(f"Connected socket on {url}")

    def _solver_request(
        self, header_str: str, rest_message: List[bytes], last_endpoint: str
    ) -> str:
        """Solve the request and return the result."""
        logging.info(f"Received a message from: {last_endpoint}")
        header = parse_header(header_str)
        data = json.loads(rest_message[0].decode("utf-8"))
        return handle_request(header, data)

    def _process_request(self, socket: zmq.Socket) -> None:
        """Process incoming requests and send responses."""
        try:
            message = socket.recv_multipart(flags=zmq.NOBLOCK)
            last_endpoint = socket.getsockopt(zmq.LAST_ENDPOINT).decode("utf-8")

            header_code = message[0].decode("utf-8")
            rest_message = message[1:]

            result = self._solver_request(header_code, rest_message, last_endpoint)
            logging.info(f"Result: {result}")

            socket.send_multipart([result.encode("utf-8")])
            logging.info(f"Response sent to: {last_endpoint}")
        except ValueError as e:
            logging.error(f"Error processing message: {e}")

            socket.send_multipart([json.dumps({"error": str(e)}).encode("utf-8")])
            logging.info(f"Error sent to: {last_endpoint}")
        except zmq.Again:
            pass

    def _start_listening(self) -> None:
        """Start listening for incoming requests and process them."""
        while True:
            events = self.poller.poll()
            for sock, event in events:
                if event == zmq.POLLIN:
                    self._process_request(sock)
            time.sleep(WAIT_CHECK * STABLE_MOD)

    def run(self) -> None:
        """Start the server threads."""
        logging.info("Server started and listening for requests...")
        self._start_listening()
