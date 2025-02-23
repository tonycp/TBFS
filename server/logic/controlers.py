from typing import List

import logging

from .business_data import *
from .dtos import FileInputDto
from .business_services import ServerService
from .handlers import *

_server_service = ServerService()


@Create({"file": FileInputDto, "tags": list})
def add(file: FileInputDto, tags: List[str]) -> str:
    try:
        logging.info(f"Adding file with tags: {tags}")
        result = _server_service.create_update_file(file, tags)
        return str(result)
    except Exception as e:
        logging.error(f"Error adding file: {e}")
        return str(e)


@Delete({"tag_query": list})
def delete(tag_query: List[str]) -> str:
    try:
        logging.info(f"Deleting files with tags: {tag_query}")
        _server_service.delete_file_by_tags(tag_query)
        return "Files deleted"
    except Exception as e:
        logging.error(f"Error deleting files: {e}")
        return str(e)


@GetAll({"tag_query": list})
def list_files(tag_query: List[str]) -> list[str]:
    try:
        logging.info(f"Listing files with tags: {tag_query}")
        files = _server_service.get_files_by_tags(tag_query)
        return [str(file) for file in files]
    except Exception as e:
        logging.error(f"Error listing files: {e}")
        return str(e)


@Create({"tag_query": list, "tags": list})
def add_tags(tag_query: List[str], tags: List[str]) -> str:
    try:
        logging.info(f"Adding tags: {tags} to files with tags: {tag_query}")
        _server_service.add_tags_to_files(tag_query, tags)
        return "Tags added"
    except Exception as e:
        logging.error(f"Error adding tags: {e}")
        return str(e)


@Delete({"tag_query": list, "tags": list})
def delete_tags(tag_query: List[str], tags: List[str]) -> str:
    try:
        logging.info(f"Deleting tags: {tags} from files with tags: {tag_query}")
        _server_service.delete_tags_from_files(tag_query, tags)
        return "Tags deleted"
    except Exception as e:
        logging.error(f"Error deleting tags: {e}")
        return str(e)


@Get({"user_name": str})
def get_user_id(user_name: str) -> int:
    try:
        logging.info(f"Getting user ID for user: {user_name}")
        result = _server_service.get_user_id(user_name)
        return result
    except Exception as e:
        logging.error(f"Error getting user ID: {e}")
        return str(e)
