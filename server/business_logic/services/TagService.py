from ..dtos import TagDto
from ..business_data import Tag, file_tags, Repository

__all__ = ["TagService"]


class TagService:
    def __init__(self, repository: Repository[Tag]):
        self.repository = repository

    def get_all_tags(self):
        """Get all tags."""
        return self.repository.get_all()

    def get_tag_by_id(self, tag_id: int):
        """Get a tag by its ID."""
        return self.repository.get(tag_id)

    def get_tag_by_name(self, name: str):
        """Get a tag by its name."""
        return self.repository.get_query().filter_by(name=name).first()

    def get_tags_by_names(self, names: list[str]):
        """Get tags by names."""
        return self.repository.get_query().filter_by(name=",".join(names)).all()

    def get_tags_by_file_id(self, file_id: int):
        """Get tags by file ID."""
        return (
            self.repository.get_query().join(file_tags).filter_by(file_id=file_id).all()
        )

    def create_tag(self, tag: TagDto):
        """Create a new tag."""
        new_tag = Tag(
            name=tag.name, creation_date=tag.creation_date, update_date=tag.update_date
        )
        self.repository.create(new_tag)
        return new_tag

    def update_tag(self, tag_id: int, tag: TagDto):
        """Update a tag by its ID."""
        tag = self.repository.get(Tag, tag_id)
        tag.name = (tag.name,)
        tag.creation_date = (tag.creation_date,)
        tag.update_date = (tag.update_date,)
        self.repository.update(tag)

    def delete_tag(self, tag_id: int):
        """Delete a tag by its ID."""
        self.repository.delete(tag_id)
