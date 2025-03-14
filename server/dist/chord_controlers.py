from typing import List, Optional, Dict, Any
from datetime import datetime

import logging

from data.const import *
from logic.dtos import *
from logic.handlers import *
from logic import controlers
from logic.business_services import ServerService

from .chord import ChordNode
from .chord_service import ChordService
from .chord_reference import ChordReference

_chord_node: Optional[ChordNode] = None
_chord_service: Optional[ChordService] = None


@Chord({"property": str})
def get_chord_reference_call(property: str) -> Dict[str, Any]:
    logging.info(f"Getting chord reference {property}")

    value = getattr(_chord_node, property)

    if isinstance(value, ChordReference):
        value = value.ip

    return {
        "message": "Chord reference retrieved",
        "ip": value,
    }


@Chord({"property": str})
def get_property_call(property: str) -> Dict[str, Any]:
    logging.info(f"Getting property {property}")

    value = getattr(_chord_node, property)

    return {
        "message": "Property retrieved",
        "value": value,
    }


@Chord({"property": str, "ip": Any})
def set_chord_reference_call(property: str, ip: int) -> Dict[str, Any]:
    logging.info(f"Setting chord reference {property} to {ip}")

    updated_config = _chord_node._config.copy_with_updates({HOST_KEY: ip})
    ref = ChordReference(updated_config)

    if hasattr(_chord_node, property):
        setattr(_chord_node, property, ref)

    return {"message": "Chord reference set"}


@Chord({"property": str, "value": Any})
def set_property_call(property: str, value: Any) -> Dict[str, Any]:
    logging.info(f"Setting property {property} to {value}")

    if hasattr(_chord_node, property):
        setattr(_chord_node, property, value)

    return {"message": "Property set"}


@Chord({"func_name": str, "key": int})
def finding_call(func_name: str, key: int) -> Dict[str, Any]:
    logging.info(f"Finding message received for {func_name}, by id: {key}")

    result = None
    if hasattr(_chord_node, func_name):
        func = getattr(_chord_node, func_name)
        if callable(func):
            result: ChordNode = func(key)
            ip = result.ip if result else None

    return {
        "message": "Finding",
        "ip": ip,
    }


@Chord({"func_name": str, "node": str})
def notify_call(func_name: str, node: str) -> Dict[str, Any]:
    logging.info(f"Notify message received for {func_name}, by ip: {node}")
    updated_config = _chord_node._config.copy_with_updates({HOST_KEY: node})
    ref = ChordReference(updated_config)

    result = None
    if hasattr(_chord_node, func_name):
        func = getattr(_chord_node, func_name)
        if callable(func):
            result = func(ref)

    return {
        "message": "Notify",
        "result": result,
    }


@Chord({"message": str})
def pon_call(message: str) -> Dict[str, Any]:
    logging.info(f"Pong message received: {message}")

    return {"message": "Pong"}


@Chord({"key": Optional[str], "last_timestamp": Optional[datetime]})
def get_replication(
    key: Optional[str],
    last_timestamp: Optional[datetime],
) -> Dict[str, List[Dict[str, Any]]]:
    key = key or _chord_service._config[DB_NAME_KEY]
    db_url = _chord_service._config[DB_BASE_URL_KEY] + key
    _chord_service.change_engine(db_url)
    result = _chord_service.get_all_records(last_timestamp)
    return {
        "message": "Replication data retrieved",
        "data": result,
    }


@Chord({"key": str, "data": Dict[str, List[Dict[str, Any]]]})
def update_replication(key: str, data: Dict[str, List[Dict[str, Any]]]):
    logging.info(f"Updating replication data for key: {key}")
    db_url = _chord_service._config[DB_BASE_URL_KEY] + key
    _chord_service.change_engine(db_url)
    _chord_service.set_all_records(data)
    return {"message": "Replication data updated"}


@ChordCreate({"file": FileInputDto, "tags": list})
def chord_add(file: FileInputDto, tags: List[str]) -> str:
    try:
        logging.info(f"Chord adding file with tags: {tags}")
        last_timestamp = datetime.now()
        result = controlers.add(file, tags)
        _chord_service.replication(last_timestamp)
        return str(result)
    except Exception as e:
        logging.error(f"Error chord adding file: {e}")
        return str(e)


@ChordDelete({"tag_query": list})
def chord_delete(tag_query: List[str]) -> str:
    try:
        logging.info(f"Chord deleting files with tags: {tag_query}")
        last_timestamp = datetime.now()
        controlers.delete(tag_query)
        _chord_service.replication(last_timestamp)
        return "Files deleted"
    except Exception as e:
        logging.error(f"Error chord deleting files: {e}")
        return str(e)


@ChordGetAll({"tag_query": list})
def chord_list_files(tag_query: List[str]) -> list[str]:
    try:
        logging.info(f"Chord listing files with tags: {tag_query}")
        last_timestamp = datetime.now()
        files = controlers.list_files(tag_query)
        _chord_service.replication(last_timestamp)
        return [str(file) for file in files]
    except Exception as e:
        logging.error(f"Error chord listing files: {e}")
        return str(e)


@ChordCreate({"tag_query": list, "tags": list})
def chord_add_tags(tag_query: List[str], tags: List[str]) -> str:
    try:
        logging.info(f"Chord adding tags: {tags} to files with tags: {tag_query}")
        last_timestamp = datetime.now()
        controlers.add_tags(tag_query, tags)
        _chord_service.replication(last_timestamp)
        return "Tags added"
    except Exception as e:
        logging.error(f"Error chord adding tags: {e}")
        return str(e)


@ChordDelete({"tag_query": list, "tags": list})
def chord_delete_tags(tag_query: List[str], tags: List[str]) -> str:
    try:
        logging.info(f"Chord deleting tags: {tags} from files with tags: {tag_query}")
        last_timestamp = datetime.now()
        controlers.delete_tags(tag_query, tags)
        _chord_service.replication(last_timestamp)
        return "Tags deleted"
    except Exception as e:
        logging.error(f"Error chord deleting tags: {e}")
        return str(e)


@ChordGet({"user_name": str})
def chord_get_user_id(user_name: str) -> int:
    try:
        logging.info(f"Chord getting user ID for user: {user_name}")
        last_timestamp = datetime.now()
        result = controlers.get_user_id(user_name)
        _chord_service.replication(last_timestamp)
        return result
    except Exception as e:
        logging.error(f"Error chord getting user ID: {e}")
        return str(e)


def set_chord_node(chord_node: ChordNode) -> None:
    """Set the configuration for the server."""
    global _chord_node, _chord_service
    _chord_node = chord_node
    _chord_service = ChordService(_chord_node, _chord_node._config)
    _server_service = ServerService(_chord_node._config)
    controlers.set_server_service(_server_service)
