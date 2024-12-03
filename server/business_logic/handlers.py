import json
from typing import Callable, Any, Dict, Optional

handlers = {}  # Dict[str, (Callable[[Dict[str, Any]], Any], Dict[str, Any])]


def create_decorator(
    command_name: str, dataset: Dict[str, Any]
) -> Callable[[Callable[..., Any]], Callable[..., None]]:
    """Generic decorator factory for command handlers."""
    global handlers

    def decorator(
        func: Callable[[Dict[str, Any], Any], Any]
    ) -> Callable[[Dict[str, Any], Any], None]:
        args = ":?".join(dataset.keys()) + ":?"
        index = f"{command_name}//{func.__name__}//{args}"
        handlers[index] = (func, dataset)
        return func

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
