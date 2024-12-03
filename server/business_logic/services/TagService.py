from typing import List
from ..dtos import TagInputDto, TagOutputDto
from ..business_data import Tag, file_tags, Repository

__all__ = ["TagService"]


class TagService:
    def __init__(self, repository: Repository[Tag]):
        self.repository = repository

    def get_tag(self, file_input: TagInputDto) -> Tag:
        params = {}
        for key, value in file_input.to_dict():
            if value is not None:
                params[key] = value
        return self.repository.get_query().filter_by(**params).first()

    def get_tags_by_query(self, tags_query: List[str]) -> List[TagOutputDto]:
        return self.repository.get_query().filter(Tag.name.in_(tags_query)).all()

    def create_tag(self, tag: TagInputDto):
        """Create a new tag."""
        new_tag = Tag(
            name=tag.name,
            creation_date=tag.creation_date,
            update_date=tag.update_date,
        )
        self.repository.create(new_tag)
        return new_tag

    def update_tag(self, tag_id: int, tag: TagInputDto):
        """Update a tag by its ID."""
        tag = self.repository.get(tag_id)
        tag.name = tag.name
        tag.creation_date = tag.creation_date
        tag.update_date = tag.update_date
        self.repository.update(tag)

    def delete_tag(self, tag_id: int):
        """Delete a tag by its ID."""
        self.repository.delete(tag_id)
