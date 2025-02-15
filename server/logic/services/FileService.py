from typing import List
from ..dtos import FileInputDto, FileOutputDto
from ..business_data import File, file_tags, Repository
from .HashService import HashService
from sqlalchemy.exc import SQLAlchemyError

__all__ = ["FileService"]

class FileService:
    def __init__(self, repository: Repository[File], hash_service: HashService):
        self.repository = repository
        self.hash_service = hash_service

    def get(self, input: FileInputDto) -> File | None:
        """Retrieve a file based on the provided input DTO."""
        key = hash(input.name)
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
            print(f"Error retrieving file: {e}")
            return None

    def get_by_tags(self, ids: List[int]) -> List[File]:
        """Retrieve files associated with the given tag IDs."""
        query = self.repository.get_query().select_from(File).join(file_tags)
        if ids:
            query = query.filter(file_tags.c.tag_id.in_(ids))
        try:
            return self.repository.all(query)
        except SQLAlchemyError as e:
            print(f"Error retrieving files by tags: {e}")
            return []

    def create(self, input: FileInputDto) -> FileOutputDto | None:
        """Create a new file with the given input DTO."""
        key = hash(input.name)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None:
            return None

        file = File(
            name=input.name,
            file_type=input.file_type,
            size=input.size,
            user_id=input.user_id,
            creation_date=input.creation_date,
            update_date=input.update_date,
            node_id=node_id,
        )
        try:
            file_dto = self.repository.create(file, FileOutputDto._to_dto)
            self.replicate_file(file)
            return file_dto
        except SQLAlchemyError as e:
            print(f"Error creating file: {e}")
            return None

    def update(self, id: int, input: FileInputDto) -> FileOutputDto | None:
        """Update an existing file by its ID."""
        file = self.repository.get(id)
        if file is None:
            return None

        key = hash(input.name)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None or file.node_id != node_id:
            return None

        file.name = input.name
        file.file_type = input.file_type
        file.size = input.size
        file.user_id = input.user_id
        file.creation_date = input.creation_date
        file.update_date = input.update_date
        try:
            self.repository.update(file)
            self.replicate_file(file)
            return FileOutputDto._to_dto(file)
        except SQLAlchemyError as e:
            print(f"Error updating file: {e}")
            return None

    def delete(self, id: int) -> None:
        """Delete a file by its ID."""
        file = self.repository.get(id)
        if file:
            key = hash(file.name)
            node_id = self.hash_service.get_node_id(key)
            if node_id is not None and file.node_id == node_id:
                try:
                    self.repository.delete(file)
                    self.remove_replication(file)
                except SQLAlchemyError as e:
                    print(f"Error deleting file: {e}")

    def replicate_file(self, file: File) -> None:
        """Replicate the file to other nodes."""
        # Implement replication logic here
        pass

    def remove_replication(self, file: File) -> None:
        """Remove the file replication from other nodes."""
        # Implement replication removal logic here
        pass

