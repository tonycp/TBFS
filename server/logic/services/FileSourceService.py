import logging
from typing import List
from ..dtos import FileSourceInputDto, FileSourceOutputDto
from ..business_data import FileSource, file_tags, Repository
from sqlalchemy.exc import SQLAlchemyError

__all__ = ["FileSourceService"]


class FileSourceService:
    def __init__(
        self, repository: Repository[FileSource]
    ) -> None:
        self.repository = repository

    def get(self, input: FileSourceInputDto) -> FileSource | None:
        """Retrieve a file source based on the provided input DTO."""
        logging.info(f"Getting file source with input: {input}")
        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        query = self.repository.get_query().filter_by(**params)
        try:
            result = self.repository.first(query)
            logging.info(f"File source retrieved: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving file source: {e}")
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
        logging.info(f"Creating file source with input: {input}")
        file_source = FileSource(
            file_id=input.file_id,
            chunk_size=input.chunk_size,
            url=input.url,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        try:
            result = self.repository.create(file_source, FileSourceOutputDto._to_dto)
            logging.info(f"File source created: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error creating file source: {e}")
            return None

    def update(self, id: int, input: FileSourceInputDto) -> FileSourceOutputDto | None:
        """Update an existing file source by its ID."""
        logging.info(f"Updating file source with ID: {id} and input: {input}")
        source = self.repository.get(id)
        if source is None:
            return None

        source.file_id = input.file_id
        source.chunk_size = input.chunk_size
        source.url = input.url
        source.creation_date = input.creation_date
        source.update_date = input.update_date
        try:
            self.repository.update(source)
            result = FileSourceOutputDto._to_dto(source)
            logging.info(f"File source updated: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error updating file source: {e}")
            return None

    def delete(self, id: int) -> None:
        """Delete a file source by its ID."""
        logging.info(f"Deleting file source with ID: {id}")
        source = self.repository.get(id)
        if source:
            try:
                self.repository.delete(source)
                logging.info(f"File source deleted: {id}")
            except SQLAlchemyError as e:
                logging.error(f"Error deleting file source: {e}")
