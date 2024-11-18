import zmq
import json
from typing import Callable, Any


def check_default(config: dict) -> dict:
    """Check and set default values for the configuration."""
    default_config = {"host": "localhost", "port": 5555, "dataset": None}
    # Update config with default values if they are not provided
    for key, value in default_config.items():
        config.setdefault(key, value)
    return config


def _listening(
    func: Callable[[Any], Any],
    command_name: str,
    config: dict,
    *args: Any,
    **kwargs: Any,
) -> Callable[[Any], Any]:
    """Open a listening port to serve the request."""
    handler = f"{config['dataset']}" if config["dataset"] else ""
    url = f"tcp://{config['host']}:{config['port']}//{command_name}//{handler}"

    context = zmq.Context()
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


def Create(config: dict) -> Callable[[Callable[[Any], Any]], Callable[[Any], Any]]:
    """Open a listening port to serve the add request."""
    config = check_default(config)
    name = "Create"

    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _listening(func, name, config, *args, **kwargs)

        return wrapper

    return decorator


def Update(config: dict) -> Callable[[Callable[[Any], Any]], Callable[[Any], Any]]:
    """Open a listening port to serve the update request."""
    config = check_default(config)
    name = "Update"

    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _listening(func, name, config, *args, **kwargs)

        return wrapper

    return decorator


def Delete(config: dict) -> Callable[[Callable[[Any], Any]], Callable[[Any], Any]]:
    """Open a listening port to serve the delete request."""
    config = check_default(config)
    name = "Delete"

    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _listening(func, name, config, *args, **kwargs)

        return wrapper

    return decorator


def Get(config: dict) -> Callable[[Callable[[Any], Any]], Callable[[Any], Any]]:
    """Open a listening port to serve the get request."""
    config = check_default(config)
    name = "Get"

    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _listening(func, name, config, *args, **kwargs)

        return wrapper

    return decorator


def GetAll(config: dict) -> Callable[[Callable[[Any], Any]], Callable[[Any], Any]]:
    """Open a listening port to serve the get all request."""
    config = check_default(config)
    name = "GetAll"

    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _listening(func, name, config, *args, **kwargs)

        return wrapper

    return decorator
