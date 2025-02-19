from typing import Optional, Dict, Any

import logging

from data.const import ELECTION, HOST_KEY
from logic.handlers import Chord, Election

from .chord import ChordNode
from .chord_reference import ChordReference, bully

_chord_server: Optional[ChordNode] = None


@Chord({"property": str})
def get_property_call(property: str) -> Dict[str, Any]:
    logging.info(f"Getting property {property}")

    value = _chord_server.__dict__.get(property)

    return {
        "message": "Property retrieved",
        "value": value,
    }


@Chord({"property": str, "value": Any})
def set_property_call(property: str, value: Any) -> Dict[str, Any]:
    logging.info(f"Setting property {property} to {value}")

    if hasattr(_chord_server, property):
        _chord_server.__dict__[property] = value

    return {"message": "Property set"}


@Chord({"function_name": str, "key": int})
def finding_call(function_name: str, key: int) -> Dict[str, Any]:
    logging.info(f"Finding message received for {function_name}, by id: {key}")

    result = None
    if hasattr(_chord_server, function_name):
        func = getattr(_chord_server, function_name)
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
    updated_config = _chord_server._config.copy_with_updates({HOST_KEY: node})
    ref = ChordReference(updated_config, _chord_server.context)

    result = None
    if hasattr(_chord_server, function_name):
        func = getattr(_chord_server, function_name)
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


@Election({"id": int})
def election_call(id: int, ip: str) -> Dict[str, Any]:
    logging.warning(f"Election message received form: {ip}")

    if not _chord_server.in_election:
        _chord_server.in_election = True
        _chord_server.leader = None
        _chord_server.send_election_message(ELECTION.START)
        return {"message": "Broadcast"}

    if bully(_chord_server.id, id):
        return {"message": "Work Done"}

    return {"message": "Ok"}


@Election({"id": int, "ip": str})
def winner_call(id: int, ip: str) -> None:
    logging.info(f"Winner message received form: {ip}")

    is_bully = bully(_chord_server.id, id)
    have_leader = _chord_server.leader and not bully(id, _chord_server.leader.id)
    if not is_bully and not have_leader:
        updated_config = _chord_server._config.copy_with_updates({HOST_KEY: ip})
        _chord_server.leader = ChordReference(updated_config, _chord_server.context)
        _chord_server.im_the_leader = _chord_server.id == id
        _chord_server.in_election = False

    return {"message": "Ok"}


@Election({"id": int})
def ok_call(id: int, ip: str) -> None:
    logging.info(f"OK message received form: {ip}")

    if _chord_server.leader and bully(id, _chord_server.leader.id):
        _chord_server.leader = id
    _chord_server.im_the_leader = False

    return {"message": "Ok"}


def set_chord_node(chord_node: ChordNode) -> None:
    """Set the configuration for the server."""
    global _chord_server
    _chord_server = chord_node
