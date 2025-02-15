from typing import Any, Dict, Optional, Union, Tuple
from dotenv import load_dotenv
import os, time, zmq, json, logging
from .handlers import handle_request
from .chord import ChordNode

__all__ = ["start_server", "set_config"]

_socket_config: Dict[str, Optional[Union[str, int]]] = {}
_chord_node: Optional[ChordNode] = None


def _check_default(
    config: Dict[str, Optional[Union[str, int]]]
) -> Dict[str, Optional[Union[str, int]]]:
    """Check and set default values for the configuration."""
    load_dotenv()
    default_config: Dict[str, Optional[Union[str, int]]] = {
        "protocol": os.getenv("PROTOCOL", "tcp"),
        "host": os.getenv("HOST", "localhost"),
        "port": int(os.getenv("PORT", 5555)),
        "chord_port": int(os.getenv("CHORD_PORT", 5000)),
    }

    for key, value in default_config.items():
        config.setdefault(key, value)
    return config


def _parse_header(header_str: str) -> Tuple[str, str, Dict[str, Any]]:
    """Parse the header string and return the command name, function name, and dataset."""
    if not header_str:
        raise ValueError("Header is empty")

    header: Dict[str, Any] = json.loads(header_str)

    command_name = header.get("command_name")
    func_name = header.get("function")
    dataset = header.get("dataset")

    return command_name, func_name, dataset


def _start_listening(socket, poller) -> None:
    while True:
        time.sleep(0.01)
        socks: Dict[zmq.Socket, int] = dict(poller.poll())
        if socket in socks and socks[socket] != zmq.POLLIN:
            continue
        try:
            message = socket.recv_multipart(flags=zmq.NOBLOCK)
            decode = message[0].decode("utf-8")

            last_endpoint = socket.getsockopt(zmq.LAST_ENDPOINT).decode("utf-8")
            logging.info(f"Received a message from: {last_endpoint}")

            command_name, func_name, data = _parse_header(decode)
            result = handle_request(command_name, func_name, data)
            logging.info(f"Result: {result}")

            socket.send_multipart([result.encode("utf-8")])
            logging.info(f"Response sent to: {last_endpoint}")
        except ValueError as e:
            logging.error(f"Error processing message: {e}")

            socket.send_multipart([json.dumps({"error": str(e)}).encode("utf-8")])
            logging.info(f"Error sent to: {last_endpoint}")
        except zmq.Again:
            continue


def start_server() -> None:
    """Open a listening port to serve the request."""

    config = _check_default(_socket_config)
    logging.info("checked config")

    global _chord_node
    _chord_node = ChordNode(config["host"], config["chord_port"])
    _chord_node.join_network()

    context: zmq.Context = zmq.Context.instance()
    socket: zmq.Socket = context.socket(zmq.REP)

    url = f"{config['protocol']}://{config['host']}:{config['port']}"

    socket.bind(url)
    logging.info(f"Binding socket on {url}")

    poller: zmq.Poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    logging.info("Starting listening...")
    try:
        _start_listening(socket, poller)
    except KeyboardInterrupt:
        logging.info("Server shutting down.")
    finally:
        socket.close()


def set_config(config: Dict[str, Optional[Any]]) -> None:
    """Set the configuration for the server."""
    global _socket_config
    _socket_config.update(config)
