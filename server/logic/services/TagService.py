from typing import List
from ..dtos import TagInputDto, TagOutputDto
from ..business_data import Tag, Repository, file_tags
from .HashService import HashService
from sqlalchemy.exc import SQLAlchemyError

__all__ = ["TagService"]

class TagService:
    def __init__(self, repository: Repository[Tag], hash_service: HashService):
        self.repository = repository
        self.hash_service = hash_service

    def get(self, input: TagInputDto) -> Tag | None:
        """Retrieve a tag based on the provided input DTO."""
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
            print(f"Error retrieving tag: {e}")
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
        key = hash(input.name)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None:
            return None

        tag = Tag(
            name=input.name,
            creation_date=input.creation_date,
            update_date=input.update_date,
            node_id=node_id,
        )
        try:
            return self.repository.create(tag, TagOutputDto._to_dto)
        except SQLAlchemyError as e:
            print(f"Error creating tag: {e}")
            return None

    def update(self, id: int, input: TagInputDto) -> TagOutputDto | None:
        """Update a tag by its ID."""
        tag = self.repository.get(id)
        if tag is None:
            return None

        key = hash(input.name)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None or tag.node_id != node_id:
            return None

        tag.name = input.name
        tag.creation_date = input.creation_date
        tag.update_date = input.update_date
        try:
            self.repository.update(tag)
            return TagOutputDto._to_dto(tag)
        except SQLAlchemyError as e:
            print(f"Error updating tag: {e}")
            return None

    def delete(self, id: int) -> None:
        """Delete a tag by its ID."""
        tag = self.repository.get(id)
        if tag:
            key = hash(tag.name)
            node_id = self.hash_service.get_node_id(key)
            if node_id is not None and tag.node_id == node_id:
                try:
                    self.repository.delete(tag)
                except SQLAlchemyError as e:
                    print(f"Error deleting tag: {e}")

    def delete_tags(self, file_id: int, tag_ids: List[int]) -> None:
        """Remove a tag from a specific file."""
        with self.repository.get_session() as session:
            try:
                query = file_tags.delete().where(
                    file_tags.c.file_id == file_id,
                    file_tags.c.tag_id.in_(tag_ids),
                )
                session.execute(query)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                print(f"Error deleting tags from file: {e}")

    def add_tag(self, file_id: int, tag_id: int) -> None:
        """Add a tag to a file if it doesn't already have it."""
        params = {"file_id": file_id, "tag_id": tag_id}
        with self.repository.get_session() as session:
            try:
                query = file_tags.select().filter_by(**params)
                result = session.execute(query)
                if result.one_or_none() is None:
                    query = file_tags.insert().values(**params)
                    session.execute(query)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                print(f"Error adding tag to file: {e}")
