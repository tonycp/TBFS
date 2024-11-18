from ..dtos import FileInputDto
from ..business_data import File, file_tags, Repository

__all__ = ["FileService"]


class FileService:
    def __init__(self, repository: Repository[File]):
        self.repository = repository

    def get_all_files(self):
        """Get all files."""
        return self.repository.get_all()

    def get_file_by_id(self, file_id: int):
        """Get a file by its ID."""
        return self.repository.get(file_id)

    def get_files_by_name(self, name: str):
        """Get files by name."""
        return self.repository.get_query().filter_by(name=name).all()

    def get_files_by_type(self, file_type: str):
        """Get files by type."""
        return self.repository.get_query().filter_by(file_type=file_type).all()

    def get_files_by_user_id(self, user_id: int):
        """Get files by user ID."""
        return self.repository.get_query().filter_by(user_id=user_id).all()

    def get_files_by_tag(self, tag_id: int):
        """Get files by tag ID."""
        return (
            self.repository.get_query().join(file_tags).filter_by(tag_id=tag_id).all()
        )

    def get_files_by_tags(self, tag_ids: list[int]):
        """Get files by tag IDs."""
        return (
            self.repository.get_query()
            .join(file_tags)
            .filter(file_tags.c.tag_id.in_(tag_ids))
            .all()
        )

    def get_files_by_name_and_type(self, name: str, file_type: str):
        """Get files by name and type."""
        return (
            self.repository.get_query().filter_by(name=name, file_type=file_type).all()
        )

    def get_file_by_name_and_type_and_user_id(
        self, name: str, file_type: str, user_id: int
    ):
        """Get files by name, type, and user ID."""
        return (
            self.repository.get_query()
            .filter_by(name=name, file_type=file_type, user_id=user_id)
            .first()
        )

    def create_file(self, file_input: FileInputDto):
        """Create a new file with the given name."""
        new_file = File(
            name=file_input.name,
            file_type=file_input.file_type,
            size=file_input.size,
            user_id=file_input.user_id,
            creation_date=file_input.creation_date,
            update_date=file_input.update_date,
        )
        self.repository.create(new_file)
        return new_file

    def update_file(self, file_id: int, file_input: FileInputDto):
        """Update the name of a file by its ID."""
        file = self.repository.get(File, file_id)
        file.name = (file_input.name,)
        file.file_type = (file_input.file_type,)
        file.size = (file_input.size,)
        file.user_id = (file_input.user_id,)
        file.creation_date = (file_input.creation_date,)
        file.update_date = (file_input.update_date,)
        self.repository.update(file)

    def delete_file(self, file_id: int):
        """Delete a file by its ID."""
        self.repository.delete(file_id)