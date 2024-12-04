from typing import List
from ..dtos import TagInputDto, TagOutputDto
from ..business_data import Tag, Repository, file_tags

__all__ = ["TagService"]


class TagService:
    def __init__(self, repository: Repository[Tag]):
        self.repository = repository

    def get(self, input: TagInputDto) -> TagOutputDto | None:
        """Retrieve a tag based on the provided input DTO."""
        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        query = self.repository.get_query().filter_by(**params)
        tag = self.repository.execute_one(query)
        return TagOutputDto._to_dto(tag) if tag else None

    def get_by_query(self, query: List[str]) -> List[TagOutputDto]:
        """Retrieve tags that match the given names."""
        query = self.repository.get_query().filter(Tag.name.in_(query))
        tags = self.repository.execute_all(query)
        return list(map(TagOutputDto._to_dto, tags))

    def create(self, input: TagInputDto) -> TagOutputDto:
        """Create a new tag."""
        tag = Tag(
            name=input.name,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        self.repository.create(tag)
        return TagOutputDto._to_dto(tag)

    def update(self, id: int, input: TagInputDto) -> TagOutputDto:
        """Update a tag by its ID."""
        tag = self.repository.get(id)
        if tag is None:
            return

        tag.name = input.name
        tag.creation_date = input.creation_date
        tag.update_date = input.update_date
        self.repository.update(tag)
        return TagOutputDto._to_dto(tag)

    def delete(self, id: int) -> None:
        """Delete a tag by its ID."""
        self.repository.delete(id)

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
            except Exception as e:
                session.rollback()

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
            except Exception as e:
                session.rollback()
