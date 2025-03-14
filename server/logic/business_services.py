from typing import Any, Dict, List, Optional, Type
from dotenv import load_dotenv

import os

from data import *
from logic.configurable import Configurable

from .dtos import *
from .services import *
from .business_data import *

__all__ = ["ServerService", "set_config"]


class ServerService:
    def __init__(self, config: Optional[Configurable]):
        self._config = config or Configurable()
        get_service = self._instance_service
        self.Files: FileService = get_service(FileService, File)
        self.Users: UserService = get_service(UserService, User)
        self.Tags: TagService = get_service(TagService, Tag)
        self.FileSources: FileSourceService = get_service(FileSourceService, FileSource)

    def _instance_service(self, service, model: Type[ModelType]):
        return service(get_repository(model, self._config[DB_URL_KEY]))

    def get_user_id(self, name: str) -> int:
        user = self.Users.get(UserInputDto(name, None, None, None))
        if user is None or user.is_deleted:
            user = self.Users.create(UserInputDto(name, True))
        return user.id

    def get_tags_id(self, tags: List[str]) -> List[int]:
        tag_ids = self.Tags.get_by_query(tags)
        tag_ids = [tag.id for tag in tag_ids if not tag.is_deleted]
        return tag_ids

    def get_files_by_tags(self, tags: List[str]) -> List[FileOutputDto]:
        tag_ids = self.get_tags_id(tags)
        files = self.Files.get_by_tags(tag_ids)
        files = [file for file in files if not file.is_deleted]
        return list(map(FileOutputDto._to_dto, files))

    def create_update_file(self, input: FileInputDto, tags: List[str]) -> FileOutputDto:
        file = self.Files.get(input)
        if file is None or file.is_deleted:
            dto = self.Files.create(input)
        else:
            dto = self.Files.update(file.id, input)

        source_input = self.copy_file(input, dto.id)
        self.create_update_source(source_input)
        self._add_tags(dto.id, tags)
        return dto.to_dict()

    def create_update_source(self, input: FileSourceInputDto) -> FileSourceOutputDto:
        source = self.FileSources.get(input)
        if source is None or source.is_deleted:
            dto = self.FileSources.create(input)
        else:
            dto = self.FileSources.update(source.id, input)
        return dto

    def add_tags_to_files(self, tag_query: List[str], tags: List[str]):
        files = self.get_files_by_tags(tag_query)
        for file in files:
            if not file.is_deleted:
                self._add_tags(file.id, tags)

    def delete_file_by_tags(self, tags_query: List[str]) -> None:
        tag_ids = self.Tags.get_by_query(tags_query)
        tag_ids = [tag.id for tag in tag_ids if not tag.is_deleted]
        self.Files.delete_by_tags(tag_ids)

    def delete_tags_from_files(self, tag_query: List[str], tags: List[str]) -> None:
        tag_ids = self.Tags.get_by_query(tag_query)
        tag_ids = [tag.id for tag in tag_ids if not tag.is_deleted]
        files = self.Files.get_by_tags(tag_ids)
        for file in files:
            if not file.is_deleted:
                self._delete_tags(file.id, tags)

    def copy_file(self, file: FileInputDto, file_id: int) -> FileSourceInputDto:
        file_name = f"{file.name}.{file.file_type}"
        dest_path = os.path.join(self._config[CONTENT_PATH_KEY], file_name)
        file_loader = file.content
        with open(dest_path, "wb") as f:
            f.write(file_loader)
        return FileSourceInputDto(file_id, file.size, 1, dest_path)

    def _add_tags(self, file_id: int, tag_list: List[str]):
        for tag_name in tag_list:
            tag = self.Tags.get(TagInputDto(tag_name, None, None))
            if tag is None or tag.is_deleted:
                tag = self.Tags.create(TagInputDto(tag_name))
            self.Tags.add_tag(file_id, tag.id)

    def _delete_tags(self, file_id: int, tag_list: List[str]):
        tag_ids = self.get_tags_id(tag_list)
        self.Tags.delete_tags(file_id, tag_ids)
