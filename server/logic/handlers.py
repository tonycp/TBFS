import json
import logging
from typing import Callable, Any, Dict, Optional, Tuple, List

handlers: Dict[
    str, Tuple[Callable[[Dict[str, Any]], str], Dict[str, Callable[[Any], bool]]]
] = {}


def _load_data(
    data: List[bytes], dataset: Dict[str, Callable[[Any], bool]]
) -> Dict[str, Any]:
    """Load the data from the message into a dictionary."""
    try:
        data_dict: Dict[str, Any] = json.loads(data[0].decode("utf-8"))
    except (IndexError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid data format: {e}")

    result = {}
    for key, value_type in dataset.items():
        value = data_dict.get(key)
        if value is None:
            raise ValueError(f"Missing required key: {key}")
        try:
            if isinstance(value, dict):
                result[key] = value_type(**value)
            else:
                result[key] = value_type(value)
        except Exception as e:
            raise ValueError(f"Error processing key '{key}': {e}")

    return result


def handle_request(header: Tuple[str, str, Dict[str, Any]]) -> Any:
    """Handle incoming requests and route them to the appropriate handler."""
    try:
        command_name, func_name, data = header
        if command_name is None or func_name is None:
            raise ValueError("Missing command_name or func_name in header")

        args = ":?".join(data.keys()) + ":?"
        handler_key = f"{command_name}//{func_name}//{args}"
        handler = handlers.get(handler_key)

        if not handler:
            raise ValueError("Unknown command name or dataset")

        handler_func, dataset = handler
        return handler_func(**_load_data(data, dataset))
    except Exception as e:
        logging.error(f"Error handling request: {e}")
        return {"error": str(e)}


def create_handler(
    command_name: str, dataset: Dict[str, Callable[[Any], bool]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    """Generic handler factory for commands."""
    global handlers

    def handler(func: Callable[..., Any]) -> Callable[..., str]:
        args = ":?".join(dataset.keys()) + ":?"
        index = f"{command_name}//{func.__name__}//{args}"
        handlers[index] = (func, dataset)

        def wrapper(data: Dict[str, Any]) -> str:
            try:
                validated_errors = [k for k, v in dataset.items() if not v(data[k])]
                if validated_errors:
                    raise ValueError(f"Invalid data: {validated_errors}")

                result = func(**data)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": str(e)})

        return wrapper

    return handler


def Create(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("Create", dataset)


def Update(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("Update", dataset)


def Delete(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("Delete", dataset)


def Get(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("Get", dataset)


def GetAll(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("GetAll", dataset)
