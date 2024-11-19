import time
import zmq
import json
from typing import Callable, Any, Dict, List, Optional, Union
from .handlers import handlers

_socket_config: Dict[str, Optional[Union[str, int]]] = {
    "protocol": "tcp",
    "host": "localhost",
    "port": 5555,
}


def _check_default(
    config: Dict[str, Optional[Union[str, int]]]
) -> Dict[str, Optional[Union[str, int]]]:
    """Check and set default values for the configuration."""
    default_config: Dict[str, Optional[Union[str, int]]] = {
        "protocol": "tcp",
        "host": "localhost",
        "port": 5555,
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
    dataset = header.get("dataset")

    if command_name is None or dataset is None:
        raise ValueError("Missing command_name or dataset in header")

    handler_key = f"{command_name}//{json.dumps(dataset)}"
    handler = handlers.get(handler_key)

    if not handler:
        raise ValueError("Unknown command name or dataset")

    return handler[0], handler[1]  # Retornar solo la función y el dataset


def _load_data(data: List[bytes], dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Load the data from the message into a dictionary."""
    return json.loads(b"".join(data).decode("utf-8"), object_hook=lambda obj: dataset)


def start_listening() -> None:
    """Open a listening port to serve the request."""
    config = _check_default(_socket_config)

    context: zmq.Context = zmq.Context.instance()
    socket: zmq.Socket = context.socket(zmq.REP)

    url = f"{config['protocol']}://{config['host']}:{config['port']}"

    socket.bind(url)
    print(f"Server listening on {url}")

    poller: zmq.Poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    try:
        while True:
            socks: Dict[zmq.Socket, int] = dict(poller.poll())
            if socket in socks and socks[socket] == zmq.POLLIN:
                try:
                    message = socket.recv_multipart(flags=zmq.NOBLOCK)
                    handler_func, dataset = _load_handler(message[0].decode("utf-8"))
                    incoming_data = _load_data(message[1:], dataset)
                    result = handler_func(incoming_data)
                    socket.send_multipart([json.dumps(result).encode("utf-8")])
                except ValueError as e:
                    print(f"Error processing message: {e}")
                    socket.send_multipart(
                        [json.dumps({"error": str(e)}).encode("utf-8")]
                    )
                except zmq.Again:
                    continue
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Server shutting down.")

    finally:
        socket.close()


def set_config(config: Dict[str, Optional[Any]]) -> None:
    """Set the configuration for the server."""
    global _socket_config
    _socket_config.update(config)
