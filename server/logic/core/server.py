import os, time, zmq, json, logging, threading
from typing import Any, Dict, Optional, Union, Tuple
from dotenv import load_dotenv

from .handlers import handle_request

__all__ = ["Server"]


class Server:
    def __init__(self, config: Optional[Dict[str, Optional[Union[str, int]]]] = None):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self._config = self._check_default(config or {})
        self._bind_socket()
        threading.Thread(target=self._run).start()

    @staticmethod
    def _check_default(
        config: Dict[str, Optional[Union[str, int]]]
    ) -> Dict[str, Optional[Union[str, int]]]:
        """Check and set default values for the configuration."""
        load_dotenv()
        default_config: Dict[str, Optional[Union[str, int]]] = {
            "protocol": os.getenv("PROTOCOL", "tcp"),
            "host": os.getenv("HOST", "localhost"),
            "port": int(os.getenv("PORT", 5555)),
        }

        for key, value in default_config.items():
            config.setdefault(key, value)
        return config

    def _bind_socket(self):
        url = f"{self._config['protocol']}://{self._config['host']}:{self._config['port']}"
        self.socket.bind(url)
        logging.info(f"Binding socket on {url}")

    def _run(self):
        while True:
            try:
                self._start_listening()
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error in _run: {e}")

    def _start_listening(self):
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        while True:
            time.sleep(0.01)
            events = poller.poll()
            for socket_event, event in events:
                if event == zmq.POLLIN:
                    self._process_request(socket_event)

    def _process_request(self, socket: zmq.Socket) -> None:
        try:
            message = socket.recv_multipart(flags=zmq.NOBLOCK)
            decode = message[0].decode("utf-8")

            last_endpoint = socket.getsockopt(zmq.LAST_ENDPOINT).decode("utf-8")
            logging.info(f"Received a message from: {last_endpoint}")

            result = self._solver_request(decode)
            logging.info(f"Result: {result}")

            socket.send_multipart([result.encode("utf-8")])
            logging.info(f"Response sent to: {last_endpoint}")
        except ValueError as e:
            logging.error(f"Error processing message: {e}")

            socket.send_multipart([json.dumps({"error": str(e)}).encode("utf-8")])
            logging.info(f"Error sent to: {last_endpoint}")
        except zmq.Again:
            pass

    def _solver_request(self, header_str: str) -> str:
        """Solve the request and return the result."""
        command_name, func_name, dataset = self._parse_header(header_str)
        return handle_request((command_name, func_name, dataset))

    def _parse_header(self, header_str: str) -> Tuple[str, str, Dict[str, Any]]:
        """Parse the header string and return the command name, function name, and dataset."""
        if not header_str:
            raise ValueError("Header is empty")

        header: Dict[str, Any] = json.loads(header_str)

        command_name = header.get("command_name")
        func_name = header.get("function")
        dataset = header.get("dataset")

        return command_name, func_name, dataset
