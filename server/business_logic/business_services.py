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

    def _add_tags(self, file_id: int, tag_list: List[str]):
        for tag_name in tag_list:
            tag = self.Tags.get_tag(TagInputDto(tag_name, None, None))
            if tag is None:
                tag = self.Tags.create_tag(TagInputDto(tag_name))
            self.Files.add_tag(file_id, tag.id)

    def add_tags_to_files(self, tag_query: List[str], tags: List[str]):
        files = self.Files.get_files_by_tags(tag_query)
        for file in files:
            self._add_tags(file.id, tags)

    def get_user_id(self, user_name: str) -> int:
        user = self.Users.get_user(UserInputDto(user_name, None, None, None))
        if user is None:
            return self.Users.create_user(
                UserInputDto(name=user_name, is_connected=True)
            ).id
        return user.id

    def get_files_by_tags(self, tags_query: List[str]) -> List[FileOutputDto]:
        tag_ids = self.Tags.get_tags_by_query(tags_query)
        files = self.Files.get_files_by_tags(tag_ids)
        return list(map(FileOutputDto._file_to_dto, files))

    def create_file(self, file: FileInputDto, tag_list: List[str]) -> FileOutputDto:
        new_file = self.Files.get_file(file)
        if new_file is None:
            new_file = self.Files.create_file(file)
        else:
            self.Files.update_file(new_file.id, file)
        self._add_tags(new_file.id, tag_list)
        return FileOutputDto._file_to_dto(new_file)

    def delete_file_by_tags(self, tags_query: List[str]) -> None:
        tag_ids = self.Tags.get_tags_by_query(tags_query)
        self.Files.delete_file_by_tags(tag_ids)

    def delete_tags_from_files(self, tag_query: List[str], tags: List[str]) -> None:
        files = self.Files.get_files_by_tags(tag_query)
        for file in files:
            self.Files.delete_tags(file.id, tags)


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
