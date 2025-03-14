from typing import List, Optional, Dict, Any, Tuple

import logging

from data.const import *
from logic.handlers import *
from logic.dtos.FileDto import *

from .leader import ChordLeader
from .chord_reference import ChordReference
from .chord_controlers import set_chord_node
from .leader_service import LeaderService
from .utils import bully

_chord_server: Optional[ChordLeader] = None
_leader_service: LeaderService = None


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


@LiderCreate({"file": FileInputDto, "tags": list, "header": Tuple[str, str, List[str]]})
def lider_add(
    file: FileInputDto,
    tags: List[str],
    header: Tuple[str, str, List[str]],
) -> str:
    try:
        logging.info(f"Lider adding file with tags: {tags}")
        result = _leader_service.create_update_file(header, file, tags)
        return str(result)
    except Exception as e:
        logging.error(f"Error lider adding file: {e}")
        return str(e)


@LiderDelete({"tag_query": list, "header": Tuple[str, str, List[str]]})
def lider_delete(
    tag_query: List[str],
    header: Tuple[str, str, List[str]],
) -> str:
    try:
        logging.info(f"Lider deleting files with tags: {tag_query}")
        _leader_service.delete_file_by_tags(header, tag_query)
        return "Files deleted"
    except Exception as e:
        logging.error(f"Error lider deleting files: {e}")
        return str(e)


@LiderGetAll({"tag_query": list, "header": Tuple[str, str, List[str]]})
def lider_list_files(
    tag_query: List[str],
    header: Tuple[str, str, List[str]],
) -> list[str]:
    try:
        logging.info(f"Lider listing files with tags: {tag_query}")
        files = _leader_service.get_files_by_tags(header, tag_query)
        return [str(file) for file in files]
    except Exception as e:
        logging.error(f"Error lider listing files: {e}")
        return str(e)


@LiderCreate({"tag_query": list, "tags": list, "header": Tuple[str, str, List[str]]})
def lider_add_tags(
    tag_query: List[str],
    tags: List[str],
    header: Tuple[str, str, List[str]],
) -> str:
    try:
        logging.info(f"Lider adding tags: {tags} to files with tags: {tag_query}")
        _leader_service.add_tags_to_files(header, tag_query, tags)
        return "Tags added"
    except Exception as e:
        logging.error(f"Error lider adding tags: {e}")
        return str(e)


@LiderDelete({"tag_query": list, "tags": list, "header": Tuple[str, str, List[str]]})
def lider_delete_tags(
    tag_query: List[str],
    tags: List[str],
    header: Tuple[str, str, List[str]],
) -> str:
    try:
        logging.info(f"Lider deleting tags: {tags} from files with tags: {tag_query}")
        _leader_service.delete_tags_from_files(header, tag_query, tags)
        return "Tags deleted"
    except Exception as e:
        logging.error(f"Error lider deleting tags: {e}")
        return str(e)


@LiderGet({"user_name": str, "header": Tuple[str, str, List[str]]})
def lider_get_user_id(
    user_name: str,
    header: Tuple[str, str, List[str]],
) -> int:
    try:
        logging.info(f"Lider getting user ID for user: {user_name}")
        result = _leader_service.get_user_id(header, user_name)
        return result
    except Exception as e:
        logging.error(f"Error lider getting user ID: {e}")
        return str(e)


def set_chord_server(chord_server: ChordLeader) -> None:
    """Set the configuration for the server."""
    global _chord_server, _leader_service
    _chord_server = chord_server
    _leader_service = LeaderService(chord_server)
    set_chord_node(_chord_server)
