from typing import Callable, Any, Dict, List, Optional, Tuple

import json, logging

__all__ = [
    "handlers",
    "handle_request",
    "header_data",
    "parse_header",
    "handlers_lider_conv",
    "Create",
    "Update",
    "Delete",
    "Get",
    "GetAll",
    "Chord",
    "Election",
    "LiderCreate",
    "LiderUpdate",
    "LiderDelete",
    "LiderGet",
    "LiderGetAll",
]

handlers: Dict[
    str, Tuple[Callable[[Dict[str, Any]], str], Dict[str, Callable[[Any], bool]]]
] = {}


def header_data(command_name: str, function: str, dataset: Dict[str, Any]) -> str:
    """Create a header string from the command name, function name, and dataset."""
    return json.dumps(
        {
            "command_name": command_name,
            "function": function,
            "dataset": dataset,
        }
    )


def parse_header(header_str: str) -> Tuple[str, str, List[str]]:
    """Parse the header string and return the command name, function name, and dataset."""
    if not header_str:
        raise ValueError("Header is empty")

    header: Dict[str, Any] = json.loads(header_str)
    return (
        header.get("command_name"),
        header.get("function"),
        header.get("dataset"),
    )


def _load_data(
    data: Dict[str, Any], dataset: Dict[str, Callable[[Any], bool]]
) -> Dict[str, Any]:
    """Load and validate the data from the message into a dictionary."""
    validated_errors = [k for k, v in dataset.items() if not v(data.get(k))]
    if validated_errors:
        raise ValueError(f"Invalid data: {validated_errors}")

    result = {}
    for key, value_type in dataset.items():
        value = data.get(key)
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


def handle_request(header: Tuple[str, str, List[str]], data: Dict[str, Any]) -> str:
    """Handle incoming requests and route them to the appropriate handler."""
    try:
        command_name, func_name, data_header = header
        if command_name is None or func_name is None:
            raise ValueError("Missing command_name or func_name in header")

        args = ":?".join(data_header) + ":?"
        handler_key = f"{command_name}//{func_name}//{args}"
        handler = handlers.get(handler_key)

        if not handler:
            raise ValueError("Unknown command name or dataset")

        handler_func, dataset = handler
        return handler_func(_load_data(data, dataset))
    except Exception as e:
        logging.error(f"Error handling request: {e}")
        return json.dumps({"error": str(e)})


def create_handler(
    command_name: str, dataset: Dict[str, Callable[[Any], bool]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    """Generic handler factory for commands."""
    global handlers

    def handler(func: Callable[..., Any]) -> Callable[..., str]:
        args = ":?".join(dataset.keys()) + ":?"
        index = f"{command_name}//{func.__name__}//{args}"

        def wrapper(data: Dict[str, Any]) -> str:
            return json.dumps(func(**data))

        handlers[index] = (wrapper, dataset)

        return wrapper

    return handler


def handlers_lider_conv(func_name: str):
    return f"Lider{func_name}"


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


def Chord(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("Chord", dataset)


def Election(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("Election", dataset)


def LiderCreate(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("LiderCreate", dataset)


def LiderUpdate(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("LiderUpdate", dataset)


def LiderDelete(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("LiderDelete", dataset)


def LiderGet(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("LiderGet", dataset)


def LiderGetAll(
    dataset: Dict[str, Optional[Callable[[Any], bool]]]
) -> Callable[[Callable[..., Any]], Callable[..., str]]:
    return create_handler("LiderGetAll", dataset)
