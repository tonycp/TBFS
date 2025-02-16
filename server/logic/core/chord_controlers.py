import logging

from typing import Optional, Dict, Any

from .const import ELECTION
from .chord import ChordNode
from .chord_reference import bully
from .handlers import Chord, Election

_chord_server: Optional[ChordNode] = None

@Chord()
def get_property_call(property: str) -> Dict[str, Any]:
    return {
        "message": "📖 Property retrieved",
        "value": _chord_server.__dict__.get(property),
    }

@Chord()
def set_property_call(property: str, value: Any) -> Dict[str, Any]:
    _chord_server.__dict__[property] = value
    return {"message": "📝 Property set"}

@Chord()
def finding_call(function_name: str, key: int) -> Dict[str, Any]:
    func = _chord_server.__dict__.get(function_name)
    result = func(key) if func else None
    return {
        "message": "🔍 Finding",
        "result": result,
    }

@Chord()
def notify_call(function_name: str, node: str) -> Dict[str, Any]:
    func = _chord_server.__dict__.get(function_name)
    result = func(node) if func else None
    return {
        "message": "📢 Notify",
        "result": result,
    }

@Election({"id": int})
def election_call(id: int) -> Dict[str, Any]:
    logging.warning(f"📜 Election message received form: {id}")

    if not _chord_server.in_election:
        _chord_server.in_election = True
        _chord_server.leader = None
        _chord_server.send_election_message(ELECTION.START)
        return {"message": "📢 Broadcast"}

    if bully(_chord_server.id, id):
        return {"message": "🖥️ Work Done"}

@Election({"id": int})
def winner_call(id: int) -> None:
    logging.warning(f"👑 Winner message received form: {id}")

    is_bully = bully(_chord_server.id, id)
    have_leader = _chord_server.leader and not bully(id, _chord_server.leader.id)
    if not is_bully and not have_leader:
        _chord_server.leader = id
        _chord_server.im_the_leader = _chord_server.id == id
        _chord_server.in_election = False

@Election({"id": int})
def ok_call(id: int) -> None:
    logging.warning(f"👍 OK message received form: {id}")

    if _chord_server.leader and bully(id, _chord_server.leader.id):
        _chord_server.leader = id
    _chord_server.im_the_leader = False
