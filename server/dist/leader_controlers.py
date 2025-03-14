from typing import List, Optional, Dict, Any, Tuple

import logging

from data.const import *
from logic.handlers import *
from logic.dtos.FileDto import *

from .leader import ChordLeader
from .chord_reference import ChordReference
from .chord_controlers import set_chord_node
from .utils import bully

_chord_server: Optional[ChordLeader] = None


@Election({"id": int, "ip": str})
def election_call(id: int, ip: str) -> Dict[str, Any]:
    logging.warning(f"Election message received form: {ip}")

    if not _chord_server.in_election:
        port, data = DEFAULT_ELECTION_PORT, {"id": id, "ip": ip}
        _chord_server.in_election = True
        _chord_server.leader = None
        _chord_server.send_election_message(ELECTION.START, port, data)
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
        _chord_server.leader = ChordReference(updated_config)
        _chord_server.im_the_leader = _chord_server.id == id
        _chord_server.in_election = False

    return {"message": "Ok"}


@Election({"id": int, "ip": str})
def ok_call(id: int, ip: str) -> None:
    logging.info(f"OK message received form: {ip}")

    if _chord_server.leader and bully(id, _chord_server.leader.id):
        _chord_server.leader = id
    _chord_server.im_the_leader = False

    return {"message": "Ok"}


def set_chord_server(chord_server: ChordLeader) -> None:
    """Set the configuration for the server."""
    global _chord_server
    _chord_server = chord_server
    set_chord_node(_chord_server)
