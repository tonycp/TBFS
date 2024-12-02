from typing import List

from .business_data import *
from .dtos import FileDto
from .business_services import ServerService
from .handlers import *

_server_service = ServerService()


@Create({"file": FileDto, "tag_list": List[str]})
def add(file: FileDto, tag_list: List[str]) -> str:
    return _server_service.create_file(file, tag_list)


@Delete({"tag_query": List[str]})
def delete(tag_query: List[str]) -> str:
    tag_ids = _server_service.get_tags_by_names(tag_query)
    _server_service.delete_files_by_tags(tag_ids)
    return "Files deleted"


@GetAll({"tag_query": List[str]})
def list(tag_query: List[str]) -> list[FileDto]:
    return _server_service.get_files_by_tags(tag_query)


@Create({"tag_query": List[str], "tag_list": List[str]})
def add_tags(tag_query: List[str], tag_list: List[str]) -> str:
    _server_service._add_tags(tag_query, tag_list)
    return "Tags added"


@Delete({"tag_query": List[str], "tag_list": List[str]})
def delete_tags(tag_query: List[str], tag_list: List[str]) -> str:
    _server_service.delete_tags(tag_query, tag_list)
    return "Tags deleted"
