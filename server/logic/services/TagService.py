import logging
from typing import List
from ..dtos import TagInputDto, TagOutputDto
from ..business_data import Tag, Repository, file_tags
from sqlalchemy.exc import SQLAlchemyError

__all__ = ["TagService"]


class TagService:
    def __init__(self, repository: Repository[Tag]):
        self.repository = repository

    def get(self, input: TagInputDto) -> Tag | None:
        """Retrieve a tag based on the provided input DTO."""
        logging.info(f"Getting tag with input: {input}")
        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        query = self.repository.get_query().filter_by(**params)
        try:
            result = self.repository.first(query)
            logging.info(f"Tag retrieved: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving tag: {e}")
            return None

    def get_by_query(self, query: List[str]) -> List[Tag]:
        """Retrieve tags that match the given names."""
        query = self.repository.get_query().filter(Tag.name.in_(query))
        try:
            return self.repository.all(query)
        except SQLAlchemyError as e:
            print(f"Error retrieving tags by query: {e}")
            return []

    def create(self, input: TagInputDto) -> TagOutputDto | None:
        """Create a new tag."""
        logging.info(f"Creating tag with input: {input}")
        tag = Tag(
            name=input.name,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        try:
            result = self.repository.create(tag, TagOutputDto._to_dto)
            logging.info(f"Tag created: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error creating tag: {e}")
            return None

    def update(self, id: int, input: TagInputDto) -> TagOutputDto | None:
        """Update a tag by its ID."""
        logging.info(f"Updating tag with ID: {id} and input: {input}")
        tag = self.repository.get(id)
        if tag is None:
            return None

        tag.name = input.name
        tag.creation_date = input.creation_date
        tag.update_date = input.update_date
        try:
            self.repository.update(tag)
            result = TagOutputDto._to_dto(tag)
            logging.info(f"Tag updated: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error updating tag: {e}")
            return None

    def delete(self, id: int) -> None:
        """Delete a tag by its ID."""
        logging.info(f"Deleting tag with ID: {id}")
        tag = self.repository.get(id)
        if tag:
            try:
                self.repository.delete(tag)
                logging.info(f"Tag deleted: {id}")
            except SQLAlchemyError as e:
                logging.error(f"Error deleting tag: {e}")

    def delete_tags(self, file_id: int, tag_ids: List[int]) -> None:
        """Remove a tag from a specific file."""
        logging.info(f"Deleting tags from file ID: {file_id} with tag IDs: {tag_ids}")
        with self.repository.get_session() as session:
            try:
                query = file_tags.delete().where(
                    file_tags.c.file_id == file_id,
                    file_tags.c.tag_id.in_(tag_ids),
                )
                session.execute(query)
                session.commit()
                logging.info(f"Tags deleted from file ID: {file_id}")
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(f"Error deleting tags from file: {e}")

    def add_tag(self, file_id: int, tag_id: int) -> None:
        """Add a tag to a file if it doesn't already have it."""
        logging.info(f"Adding tag ID: {tag_id} to file ID: {file_id}")
        params = {"file_id": file_id, "tag_id": tag_id}
        with self.repository.get_session() as session:
            try:
                query = file_tags.select().filter_by(**params)
                result = session.execute(query)
                if result.one_or_none() is None:
                    query = file_tags.insert().values(**params)
                    session.execute(query)
                session.commit()
                logging.info(f"Tag ID: {tag_id} added to file ID: {file_id}")
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(f"Error adding tag to file: {e}")
