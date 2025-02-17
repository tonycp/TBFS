from sqlalchemy.exc import SQLAlchemyError
from typing import List

import logging

from logic.dtos import FileInputDto, FileOutputDto
from data import File, file_tags, Repository

__all__ = ["FileService"]


class FileService:
    def __init__(self, repository: Repository[File]):
        self.repository = repository

    def get(self, input: FileInputDto) -> File | None:
        """Retrieve a file based on the provided input DTO."""
        logging.info(f"Getting file with input: {input}")
        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        query = self.repository.get_query().filter_by(**params)
        try:
            result = self.repository.first(query)
            logging.info(f"File retrieved: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving file: {e}")
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
        logging.info(f"Creating file with input: {input}")
        file = File(
            name=input.name,
            file_type=input.file_type,
            size=input.size,
            user_id=input.user_id,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        try:
            result = self.repository.create(file, FileOutputDto._to_dto)
            logging.info(f"File created: {result}")
            self.replicate_file(file)
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error creating file: {e}")
            return None

    def update(self, id: int, input: FileInputDto) -> FileOutputDto | None:
        """Update an existing file by its ID."""
        logging.info(f"Updating file with ID: {id} and input: {input}")
        file = self.repository.get(id)
        if file is None:
            return None

        file.name = input.name
        file.file_type = input.file_type
        file.size = input.size
        file.user_id = input.user_id
        file.creation_date = input.creation_date
        file.update_date = input.update_date
        try:
            self.repository.update(file)
            result = FileOutputDto._to_dto(file)
            logging.info(f"File updated: {result}")
            self.replicate_file(file)
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error updating file: {e}")
            return None

    def delete(self, id: int) -> None:
        """Delete a file by its ID."""
        logging.info(f"Deleting file with ID: {id}")
        file = self.repository.get(id)
        if file:
            try:
                self.repository.delete(file)
                logging.info(f"File deleted: {id}")
                self.remove_replication(file)
            except SQLAlchemyError as e:
                logging.error(f"Error deleting file: {e}")

    def replicate_file(self, file: File) -> None:
        """Replicate the file to other nodes."""
        logging.info(f"Replicating file: {file}")
        # Implement replication logic here
        pass

    def remove_replication(self, file: File) -> None:
        """Remove the file replication from other nodes."""
        logging.info(f"Removing replication for file: {file}")
        # Implement replication removal logic here
        pass
