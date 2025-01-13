from typing import Callable, Any, Dict, List, Optional, Union
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


def _load_handler(header_str: str) -> Optional[Callable[[Dict[str, Any]], Any]]:
    """Load the appropriate handler based on the header."""
    if not header_str:
        raise ValueError("Header is empty")

    header: Dict[str, Any] = json.loads(header_str)

    # Verificar que las claves necesarias estén presentes
    command_name = header.get("command_name")
    func_name = header.get("function")
    dataset = header.get("dataset")

    if command_name is None or dataset is None:
        raise ValueError("Missing command_name or dataset in header")
    args = ":?".join(dataset) + ":?"
    handler_key = f"{command_name}//{func_name}//{args}"
    handler = handlers.get(handler_key)

    if not handler:
        raise ValueError("Unknown command name or dataset")

    return handler_key, handler[0], handler[1]  # Retornar solo la función y el dataset


def _load_data(data: List[bytes], dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Load the data from the message into a dictionary."""
    data_dict: Dict[str, Any] = json.loads(data[0].decode("utf-8"))
    result = {}
    for key, value_type in dataset.items():
        value = data_dict.get(key)
        if type(value) != dict:
            result[key] = value_type(value)
        else:
            result[key] = value_type(**value)

    return result


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

                    handler_name, handler_func, dataset = _load_handler(
                        message[0].decode("utf-8")
                    )
                    logging.info(f"Redirecting to handler: {handler_name}")

                    incoming_data = _load_data(message[1:], dataset)
                    logging.info(f"checked incoming data: {incoming_data}")

                    result = handler_func(**incoming_data)
                    logging.info(f"Result: {result}")

                    socket.send_multipart([json.dumps(result).encode("utf-8")])
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
