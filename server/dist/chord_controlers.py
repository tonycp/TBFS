from typing import Optional, Dict, Any

import logging

from data.const import *
from logic.handlers import Chord

from .chord import ChordNode
from .chord_reference import ChordReference

_chord_node: Optional[ChordNode] = None


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


@Chord({"function_name": str, "key": int})
def finding_call(function_name: str, key: int) -> Dict[str, Any]:
    logging.info(f"Finding message received for {function_name}, by id: {key}")

    result = None
    if hasattr(_chord_node, function_name):
        func = getattr(_chord_node, function_name)
        if callable(func):
            result: ChordNode = func(key)
            ip = result.ip if result else None

    return {
        "message": "Finding",
        "ip": ip,
    }


@Chord({"function_name": str, "node": str})
def notify_call(function_name: str, node: str) -> Dict[str, Any]:
    logging.info(f"Notify message received for {function_name}, by ip: {node}")
    updated_config = _chord_node._config.copy_with_updates({HOST_KEY: node})
    ref = ChordReference(updated_config)

    result = None
    if hasattr(_chord_node, function_name):
        func = getattr(_chord_node, function_name)
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


def set_chord_node(chord_node: ChordNode) -> None:
    """Set the configuration for the server."""
    global _chord_node
    _chord_node = chord_node
