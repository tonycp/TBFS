from typing import List
from ..dtos import FileSourceInputDto, FileSourceOutputDto
from ..business_data import FileSource, file_tags, Repository
from .HashService import HashService
from sqlalchemy.exc import SQLAlchemyError

__all__ = ["FileSourceService"]

class FileSourceService:
    def __init__(self, repository: Repository[FileSource], hash_service: HashService) -> None:
        self.repository = repository
        self.hash_service = hash_service

    def get(self, input: FileSourceInputDto) -> FileSource | None:
        """Retrieve a file source based on the provided input DTO."""
        key = hash(input.url)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None:
            return None

        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        params['node_id'] = node_id
        query = self.repository.get_query().filter_by(**params)
        try:
            return self.repository.first(query)
        except SQLAlchemyError as e:
            print(f"Error retrieving file source: {e}")
            return None

    def get_all(self) -> List[FileSource]:
        """Retrieve all file sources."""
        try:
            return self.repository.get_all()
        except SQLAlchemyError as e:
            print(f"Error retrieving all file sources: {e}")
            return []

    def get_by_file_id(self, id: int) -> List[FileSource]:
        """Retrieve file sources associated with the given file ID."""
        query = self.repository.get_query().join(FileSource.file).filter_by(file_id=id)
        try:
            return self.repository.all(query)
        except SQLAlchemyError as e:
            print(f"Error retrieving file sources by file ID: {e}")
            return []

    def get_by_tag_id(self, id: int) -> List[FileSource]:
        """Retrieve file sources associated with the given tag ID."""
        query = self.repository.get_query().join(file_tags).filter_by(tag_id=id)
        try:
            return self.repository.all(query)
        except SQLAlchemyError as e:
            print(f"Error retrieving file sources by tag ID: {e}")
            return []

    def create(self, input: FileSourceInputDto) -> FileSourceOutputDto | None:
        """Create a new file source with the given input DTO."""
        key = hash(input.url)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None:
            return None

        file_source = FileSource(
            file_id=input.file_id,
            chunk_size=input.chunk_size,
            url=input.url,
            creation_date=input.creation_date,
            update_date=input.update_date,
            node_id=node_id,
        )
        try:
            return self.repository.create(file_source, FileSourceOutputDto._to_dto)
        except SQLAlchemyError as e:
            print(f"Error creating file source: {e}")
            return None

    def update(self, id: int, input: FileSourceInputDto) -> FileSourceOutputDto | None:
        """Update an existing file source by its ID."""
        source = self.repository.get(id)
        if source is None:
            return None

        key = hash(input.url)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None or source.node_id != node_id:
            return None

        source.file_id = input.file_id
        source.chunk_size = input.chunk_size
        source.url = input.url
        source.creation_date = input.creation_date
        source.update_date = input.update_date
        try:
            self.repository.update(source)
            return FileSourceOutputDto._to_dto(source)
        except SQLAlchemyError as e:
            print(f"Error updating file source: {e}")
            return None

    def delete(self, id: int) -> None:
        """Delete a file source by its ID."""
        source = self.repository.get(id)
        if source:
            key = hash(source.url)
            node_id = self.hash_service.get_node_id(key)
            if node_id is not None and source.node_id == node_id:
                try:
                    self.repository.delete(source)
                except SQLAlchemyError as e:
                    print(f"Error deleting file source: {e}")
