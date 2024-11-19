import time
import zmq
import json
from typing import Callable, Any, Dict, List, Optional

__all__ = [
    "create_decorator",
    "set_config",
    "Create",
    "Update",
    "Delete",
    "Get",
    "GetAll",
]

_socket_config: Dict[str, Optional[Any]] = {
    "protocol": "tcp",
    "host": "localhost",
    "port": 5555,
}


def _check_default(config: Dict[str, Optional[Any]]) -> Dict[str, Optional[Any]]:
    """Check and set default values for the configuration.

    Args:
        config: A dictionary containing the configuration.

    Returns:
        A dictionary with the default values set.
    """
    default_config = {
        "protocol": "tcp",
        "host": "localhost",
        "port": 5555,
        "dataset": None,
    }

    for key, value in default_config.items():
        config.setdefault(key, value)
    return config


def _check_header(header_str: str, config: Dict[str, Optional[Any]]) -> None:
    """Check the header of the message to ensure it matches the configuration.

    Args:
        header_str: The header of the message as a string.
        config: The configuration dictionary.

    Raises:
        ValueError: If the header does not match the configuration.
    """
    if not header_str:
        raise ValueError("Header is empty")
    header = json.loads(header_str)

    if config["command_name"] != header.get("command_name"):
        raise ValueError("Command name does not match")

    if config["dataset"] != header.get("dataset"):
        raise ValueError("Dataset does not match")


def _load_data(data: List[bytes], dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Load the data from the message into a dictionary.

    Args:
        data: The data from the message as a list of bytes.
        dataset: The dataset to use for the command.

    Returns:
        A dictionary containing the loaded data.
    """
    return json.loads(b"".join(data).decode("utf-8"), object_hook=lambda obj: dataset)


def _listening(
    func: Callable[..., Any],
    config: Dict[str, Optional[Any]],
    *args: Any,
    **kwargs: Any,
) -> None:
    """Open a listening port to serve the request.

    Args:
        func: The function to call when a request is received.
        config: A dictionary containing the configuration.
        args: The arguments to pass to the function.
        kwargs: The keyword arguments to pass to the function.
    """
    url = f"{config['protocol']}://{config['host']}:{config['port']}"

    context: zmq.Context = zmq.Context.instance()
    socket: zmq.Socket = context.socket(zmq.REP)
    socket.bind(url)
    print(f"Server listening on {url}")
    try:
        while True:
            try:
                message = socket.recv_multipart(flags=zmq.NOBLOCK)
                _check_header(message[0].decode("utf-8"), config)
                incoming_data = _load_data(message[1:], config["dataset"] or {})
                result = func(incoming_data, *args, **kwargs)
                socket.send_multipart([json.dumps(result).encode("utf-8")])
            except zmq.Again:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        socket.close()


def set_config(config: Dict[str, Optional[Any]]) -> None:
    """Set the configuration for the server.

    Args:
        config: A dictionary containing the configuration.
    """
    global _socket_config
    _socket_config.update(config)


def create_decorator(
    command_name: str, dataset: Dict[str, Any]
) -> Callable[[Callable[..., Any]], Callable[..., None]]:
    """Generic decorator factory for command handlers.

    Args:
        command_name: The name of the command.
        dataset: The dataset to use for the command.

    Returns:
        A decorator that can be used to wrap the command handler function.
    """
    global _socket_config
    config = _check_default(_socket_config)
    config["dataset"] = dataset
    config["command_name"] = command_name

    def decorator(func: Callable[..., Any]) -> Callable[..., None]:
        def wrapper(*args: Any, **kwargs: Any) -> None:
            _listening(func, config, *args, **kwargs)

        return wrapper

    return decorator


def Create(
    dataset: Dict[str, Optional[Any]]
) -> Callable[[Callable[..., Any]], Callable[..., None]]:
    return create_decorator("Create", dataset)


def Update(
    dataset: Dict[str, Optional[Any]]
) -> Callable[[Callable[..., Any]], Callable[..., None]]:
    return create_decorator("Update", dataset)


def Delete(
    dataset: Dict[str, Optional[Any]]
) -> Callable[[Callable[..., Any]], Callable[..., None]]:
    return create_decorator("Delete", dataset)


def Get(
    dataset: Dict[str, Optional[Any]]
) -> Callable[[Callable[..., Any]], Callable[..., None]]:
    return create_decorator("Get", dataset)


def GetAll(
    dataset: Dict[str, Optional[Any]]
) -> Callable[[Callable[..., Any]], Callable[..., None]]:
    return create_decorator("GetAll", dataset)
