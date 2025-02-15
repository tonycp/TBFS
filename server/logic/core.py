from typing import Any, Dict, Optional, Union, Tuple
from dotenv import load_dotenv
import os, time, zmq, json, logging
from .handlers import handle_request
from .chord import ChordNode

__all__ = ["start_server", "set_config"]

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


def _solver_request(header_str: str) -> str:
    """Solve the request and return the result."""
    command_name, func_name, dataset = _parse_header(header_str)
    return handle_request((command_name, func_name, dataset))


def _start_listening(poller: zmq.Poller) -> None:
    while True:
        time.sleep(0.01)
        events = poller.poll()
        for socket_event, event in events:
            if event != zmq.POLLIN:
                continue

            socket_event: zmq.Socket
            try:
                message = socket_event.recv_multipart(flags=zmq.NOBLOCK)
                decode = message[0].decode("utf-8")

                last_endpoint = socket_event.getsockopt(zmq.LAST_ENDPOINT).decode(
                    "utf-8"
                )
                logging.info(f"Received a message from: {last_endpoint}")

                result = _solver_request(decode)
                logging.info(f"Result: {result}")

                socket_event.send_multipart([result.encode("utf-8")])
                logging.info(f"Response sent to: {last_endpoint}")
            except ValueError as e:
                logging.error(f"Error processing message: {e}")

                socket_event.send_multipart(
                    [json.dumps({"error": str(e)}).encode("utf-8")]
                )
                logging.info(f"Error sent to: {last_endpoint}")
            except zmq.Again:
                continue


def start_server() -> None:
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
        _start_listening(poller)
    except KeyboardInterrupt:
        logging.info("Server shutting down.")
    finally:
        socket.close()


def set_config(config: Dict[str, Optional[Any]]) -> None:
    """Set the configuration for the server."""
    global _socket_config
    _socket_config.update(config)
