import os
from typing import Any, Dict, List, Optional, Type
from dotenv import load_dotenv

from .dtos import *
from .services import *
from .business_data import *

__all__ = ["ServerService", "set_config"]

_service_config = {}


class ServerService:
    def __init__(self):
        _check_default(_service_config)
        get_service = _instance_service
        self.Files: FileService = get_service(FileService, File)
        self.Users: UserService = get_service(UserService, User)
        self.Tags: TagService = get_service(TagService, Tag)
        self.FileSources: FileSourceService = get_service(FileSourceService, FileSource)

    def get_user_id(self, user_name: str) -> int:
        user = self.Users.get_user_by_name(user_name)
        if user is None:
            return self.Users.create_user(UserDto(name=user_name, is_connected=True)).id
        return user.id

    def get_files_by_tags(self, tag_names: List[str]):
        tags_ids = self.get_tags_by_names(tag_names)
        return self.Files.get_files_by_tags(tags_ids)

    def get_tags_by_names(self, names: list[str]):
        return [tag.id for tag in self.Tags.get_tags_by_names(names)]

    def _add_tags(self, file_id: int, tag_list: List[str]):
        tag_ids = [tag.id for tag in self.Tags.get_tags_by_names(tag_list)]
        self.Files.add_tags_to_file(file_id, tag_ids)

    def add_tags(self, tag_query: List[str], tag_list: List[str]) -> None:
        files = self.Files.get_files_by_tags(tag_query)
        for file in files:
            self._add_tags(file.id, tag_list)

    def create_file(self, file: FileDto, tag_list: List[str]) -> File:
        new_file = self.Files.get_file_by_name(file.name)
        if new_file is None:
            new_file = self.Files.create_file(file)
        self._add_tags(new_file.id, tag_list)
        return new_file

    def delete_file(self, file_id: int) -> bool:
        file = self.Files.get_file_by_id(file_id)
        if file is None:
            return False
        self.Files.delete_file(file_id)
        return True

    def delete_files_by_tags(self, tag_ids: List[int]) -> None:
        files = self.Files.get_files_by_tags(tag_ids)
        for file in files:
            self.Files.delete_file(file.id)

    def delete_tags(self, tag_query: List[str], tag_list: List[str]) -> None:
        files = self.Files.get_files_by_tags(tag_query)
        for file in files:
            for tag in tag_list:
                file_tags.delete().where(file_tags.c.tag_id == tag).where(
                    file_tags.c.file_id == file.id
                )


def _instance_service(service, model: Type[ModelType]):
    return service(get_repository(model, _service_config["database"]))


def _check_default(config: Dict[str, Optional[Any]]):
    """Check and set default values for the configuration."""
    load_dotenv()
    default_config = {
        "database": os.getenv(
            "DATABASE_URL", "postgresql://postgres:ranvedi@localhost/SDDB"
        ),
    }

    for key, value in default_config.items():
        config.setdefault(key, value)
    return config


def set_config(config: Dict[str, Optional[Any]]) -> None:
    """Set the configuration for the server."""
    global _service_config
    _service_config.update(config)
