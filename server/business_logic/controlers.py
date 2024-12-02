from typing import List

from .business_data import *
from .dtos import FileDto
from .business_services import ServerService
from .handlers import *

_server_service = ServerService()


@Create({"file": FileDto, "tags": list})
def add(file: FileDto, tags: List[str]) -> str:
    return str(_server_service.create_file(file, tags))


@Delete({"tag_query": list})
def delete(tag_query: List[str]) -> str:
    tag_ids = _server_service.get_tags_by_names(tag_query)
    _server_service.delete_files_by_tags(tag_ids)
    return "Files deleted"


@GetAll({"tag_query": list})
def list_files(tag_query: List[str]) -> list[str]:
    files = _server_service.get_files_by_tags(tag_query)
    return [str(file) for file in files]


@Create({"tag_query": list, "tags": list})
def add_tags(tag_query: List[str], tags: List[str]) -> str:
    _server_service._add_tags(tag_query, tags)
    return "Tags added"


@Delete({"tag_query": list, "tags": list})
def delete_tags(tag_query: List[str], tags: List[str]) -> str:
    _server_service.delete_tags(tag_query, tags)
    return "Tags deleted"

@Get({"user_name": str})
def get_user_id(user_name: str) -> int:
    return _server_service.get_user_id(user_name)
