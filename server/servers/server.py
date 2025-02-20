from typing import List, Optional, Dict, Any, Tuple

import time, zmq, json, logging, threading, socket, selectors

from data.const import *
from logic.handlers import *
from logic.configurable import Configurable


__all__ = ["Server"]


class Server:
    def __init__(self, config: Optional[Configurable] = None):
        self._config = config or Configurable()
        self.selector = selectors.DefaultSelector()
        self._subscribe_read_port(self._config[PORT_KEY])

    def _solver_request(self, header: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Solve the request and return the result."""
        return handle_request(header, data)

    def _parse_message(self, message: bytes) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Parse the incoming message and return the header and data."""
        try:
            message_dict: dict = json.loads(message.decode("utf-8"))
            header = message_dict.get("header", {})
            data = message_dict.get("data", {})
            return header, data
        except ValueError as e:
            logging.error(f"Error parsing message: {e}")
            raise

    def _process_mesage(self, message: bytes, addr: Tuple[str, int]) -> None:
        header, data = self._parse_message(message)
        logging.info(f"Processing message from {addr}: {header}")

        return self._solver_request(header, data)

    def _process_request(self, conn: socket.socket, mask: int) -> None:
        """Process incoming requests and send responses."""
        addr = conn.getpeername()
        try:
            message = conn.recv(1024)
            if not message:
                return

            result = self._process_mesage(message, addr)
            logging.info(f"Processed result: {result}")

            conn.sendall(result.encode("utf-8"))
            logging.info(f"Response sent to {addr}")
        except ValueError as e:
            logging.error(f"Error processing message from {addr}: {e}")

            conn.sendall(json.dumps({"error": str(e)}).encode("utf-8"))
            logging.info(f"Error response sent to {addr}")
        finally:
            self.selector.unregister(conn)
            conn.close()

    def _accept(self, sock: socket.socket) -> None:
        conn, addr = sock.accept()
        logging.info(f"Accepted connection from {addr}")
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, self._process_request)

    def _subscribe_read_port(self, port: int, listen: int = 5) -> None:
        """Subscribe to a specific port for incoming requests."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._config[HOST_KEY], port))
        sock.listen(listen)
        sock.setblocking(False)
        self.selector.register(sock, selectors.EVENT_READ, self._accept)
        logging.info(f"Subscribed to port {port}")

    def _start_listening(self, timeout=None) -> None:
        """Start listening for incoming requests and process them."""
        while True:
            events = self.selector.select(timeout)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
            time.sleep(WAIT_CHECK * STABLE_MOD)

    def run(self) -> None:
        """Start the server threads."""
        logging.info("Server started and listening for requests...")
        self._start_listening()
