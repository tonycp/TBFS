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

    def _process_mesage(self, message: bytes, addr: Tuple[str, int]) -> str:
        header_dict, data = self._parse_message(message)
        header = parse_header(header_dict)
        logging.info(f"Processing message from {addr}: {header}")

        return self._solver_request(header, data, addr)

    def _solver_request(
        self,
        header: Tuple[str, str, List[str]],
        data: Dict[str, Any],
        addr: Tuple[str, int],
    ) -> str:
        """Solve the request and return the result."""
        return handle_request(header, data)

    def _process_request(self, conn: socket.socket, mask: int, ori_port: int) -> None:
        """Process incoming requests and send responses."""
        addr = conn.getpeername()
        ori_addr = (addr[0], ori_port)
        try:
            message = conn.recv(1024)
            if message:
                logging.info(f"Received message from {addr}")
                result = self._process_mesage(message, ori_addr)
                logging.info(f"Processed result: {result}")

                conn.sendall(result.encode("utf-8"))
                logging.info(f"Response sent to {addr}")
                
                self.selector.unregister(conn)
                conn.close()
                logging.info(f"Connection closed with {addr}")
        except BlockingIOError as e:
            logging.warning(f"Resource temporarily unavailable: {addr} - {e}")
        except ValueError as e:
            logging.error(f"Error processing message from {addr}: {e}")

            conn.sendall(json.dumps({"error": str(e)}).encode("utf-8"))
            logging.info(f"Error response sent to {addr}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            self.selector.unregister(conn)
            conn.close()

    def _accept(self, sock: socket.socket, mask: int, ori_port: int) -> None:
        """Accept incoming connections and process them."""
        conn, addr = sock.accept()
        logging.info(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = (self._process_request, ori_port)
        self.selector.register(conn, mask, data)
        time.sleep(START_MOD)
        self._process_request(conn, mask, ori_port)

    def _subscribe_read_port(self, port: int, listen: int = 10) -> None:
        """Subscribe to a specific port for incoming requests."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._config[HOST_KEY], port))
        sock.listen(listen)
        sock.setblocking(False)
        self.selector.register(sock, selectors.EVENT_READ, (self._accept, port))
        logging.info(f"Subscribed to port {port}")

    def _start_listening(self, timeout=None) -> None:
        """Start listening for incoming requests and process them."""
        while True:
            events = self.selector.select(timeout)
            for key, mask in events:
                callback, port = key.data
                callback(key.fileobj, mask, port)

    def run(self) -> None:
        """Start the server threads."""
        logging.info("Server started and listening for requests...")
        self._start_listening()
