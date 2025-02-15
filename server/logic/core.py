from typing import Callable, Any, Dict, List, Optional, Union, Tuple
from dotenv import load_dotenv
import os, time, zmq, json, logging
from .handlers import handlers
from .controlers import *

_socket_config: Dict[str, Optional[Union[str, int]]] = {}


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


# Parse the header string and return the command name, function name, and dataset.
def parse_header(header_str: str) -> None:
    """Parse the header string and return the command name, function name, and dataset."""
    if not header_str:
        raise ValueError("Header is empty")

    header: Dict[str, Any] = json.loads(header_str)

    command_name = header.get("command_name")
    func_name = header.get("function")
    dataset = header.get("dataset")

    return command_name, func_name, dataset


def start_listening() -> None:
    """Open a listening port to serve the request."""

    config = _check_default(_socket_config)
    logging.info("checked config")

    context: zmq.Context = zmq.Context.instance()
    socket: zmq.Socket = context.socket(zmq.REP)

    url = f"{config['protocol']}://{config['host']}:{config['port']}"

    socket.bind(url)
    logging.info(f"Binding socket on {url}")

    poller: zmq.Poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    logging.info("Starting listening...")
    try:
        while True:
            socks: Dict[zmq.Socket, int] = dict(poller.poll())
            if socket in socks and socks[socket] == zmq.POLLIN:
                try:
                    message = socket.recv_multipart(flags=zmq.NOBLOCK)

                    last_endpoint = socket.getsockopt(zmq.LAST_ENDPOINT).decode("utf-8")
                    logging.info(f"Received a message from: {last_endpoint}")

                    result = handle_request(parse_header(message[0].decode("utf-8")))
                    logging.info(f"Result: {result}")

                    socket.send_multipart([result.encode("utf-8")])
                    logging.info(f"Response sent to: {last_endpoint}")
                except ValueError as e:
                    logging.error(f"Error processing message: {e}")

                    socket.send_multipart(
                        [json.dumps({"error": str(e)}).encode("utf-8")]
                    )
                    logging.info(f"Error sent to: {last_endpoint}")
                except zmq.Again:
                    continue
            time.sleep(0.01)

    except KeyboardInterrupt:
        logging.info("Server shutting down.")

    finally:
        socket.close()


def set_config(config: Dict[str, Optional[Any]]) -> None:
    """Set the configuration for the server."""
    global _socket_config
    _socket_config.update(config)
