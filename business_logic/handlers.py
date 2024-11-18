import zmq
import json
from typing import Callable, Any, Dict

__all__ = ["create_decorator", "Create", "Update", "Delete", "Get", "GetAll"]


def check_default(config: Dict[str, Any]) -> Dict[str, Any]:
    """Check and set default values for the configuration.

    Args:
        config: A dictionary containing the configuration.

    Returns:
        A dictionary with the default values set.
    """
    default_config = {"host": "localhost", "port": 5555, "dataset": None}
    # Update config with default values if they are not provided
    for key, value in default_config.items():
        config.setdefault(key, value)
    return config


def _listening(
    func: Callable[[Dict[str, Any]], Any],
    config: Dict[str, Any],
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
    handler = f"{config['dataset']}" if config["dataset"] else ""
    url = (
        f"tcp://{config['host']}:{config['port']}//{config['command_name']}//{handler}"
    )

    context = zmq.Context.instance()
    socket = context.socket(zmq.REP)
    socket.bind(url)
    print(f"Server listening on {url}")
    try:
        while True:
            try:
                message = socket.recv(flags=zmq.NOBLOCK)  # Non-blocking receive
                incoming_data = json.loads(message.decode("utf-8"))
                result = func(incoming_data, *args, **kwargs)
                socket.send_string(json.dumps(result))
            except zmq.Again:
                continue  # Continue if no message is received
    except KeyboardInterrupt:
        print("Server shutting down.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        socket.close()
        context.term()


def create_decorator(
    command_name: str, dataset: Dict[str, Any]
) -> Callable[[Callable[[Dict[str, Any]], Any]], Callable[[Dict[str, Any]], None]]:
    """Generic decorator factory for command handlers.

    Args:
        command_name: The name of the command.
        dataset: The dataset to use for the command.

    Returns:
        A decorator that can be used to wrap the command handler function.
    """
    config = check_default({"command_name": command_name, "dataset": dataset})

    def decorator(
        func: Callable[[Dict[str, Any]], Any]
    ) -> Callable[[Dict[str, Any]], None]:
        def wrapper(*args: Any, **kwargs: Any) -> None:
            _listening(func, config, *args, **kwargs)

        return wrapper

    return decorator


def Create(
    dataset: Dict[str, Any]
) -> Callable[[Callable[[Dict[str, Any]], Any]], Callable[[Dict[str, Any]], None]]:
    return create_decorator("Create", dataset)


def Update(
    dataset: Dict[str, Any]
) -> Callable[[Callable[[Dict[str, Any]], Any]], Callable[[Dict[str, Any]], None]]:
    return create_decorator("Update", dataset)


def Delete(
    dataset: Dict[str, Any]
) -> Callable[[Callable[[Dict[str, Any]], Any]], Callable[[Dict[str, Any]], None]]:
    return create_decorator("Delete", dataset)


def Get(
    dataset: Dict[str, Any]
) -> Callable[[Callable[[Dict[str, Any]], Any]], Callable[[Dict[str, Any]], None]]:
    return create_decorator("Get", dataset)


def GetAll(
    dataset: Dict[str, Any]
) -> Callable[[Callable[[Dict[str, Any]], Any]], Callable[[Dict[str, Any]], None]]:
    return create_decorator("GetAll", dataset)
