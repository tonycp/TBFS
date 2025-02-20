from typing import List, Optional

import time, zmq, json, logging, threading, socket

from data.const import *
from logic.handlers import *
from logic.configurable import Configurable


__all__ = ["Server"]


class Server:
    def __init__(self, config: Optional[Configurable] = None):
        self._config = config or Configurable()

    def _solver_request(self, header: dict, data: dict, addr) -> str:
        """Solve the request and return the result."""
        logging.info(f"Received a message from: {addr}")
        return handle_request(header, data)

    def _process_request(self, conn: socket.socket, addr) -> None:
        """Process incoming requests and send responses."""
        try:
            message = conn.recv(1024)
            header_str, data_str = message.split(b"\n", 1)
            header = json.loads(header_str.decode("utf-8"))
            data = json.loads(data_str.decode("utf-8"))
            result = self._solver_request(header, data, addr)
            logging.info(f"Result: {result}")
            conn.sendall(result.encode("utf-8"))
            logging.info(f"Response sent to: {addr}")
        except ValueError as e:
            logging.error(f"Error processing message: {e}")
            conn.sendall(json.dumps({"error": str(e)}).encode("utf-8"))
            logging.info(f"Error sent to: {addr}")
        finally:
            conn.close()

    def _start_listening(self) -> None:
        """Start listening for incoming requests and process them."""
        url = (self._config[HOST_KEY], int(self._config[PORT_KEY]))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(url)
        sock.listen(5)
        logging.info(f"Binding socket on {url}")

        while True:
            conn, addr = sock.accept()
            threading.Thread(target=self._process_request, args=(conn, addr)).start()
            time.sleep(WAIT_CHECK * STABLE_MOD)

    def run(self) -> None:
        """Start the server threads."""
        logging.info("Server started and listening for requests...")
        self._start_listening()
