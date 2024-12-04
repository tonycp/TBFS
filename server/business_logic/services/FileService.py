from typing import List
from ..dtos import FileInputDto, FileOutputDto
from ..business_data import File, file_tags, Repository

__all__ = ["FileService"]


class FileService:
    def __init__(self, repository: Repository[File]):
        self.repository = repository

    def get(self, input: FileInputDto) -> FileOutputDto | None:
        """Retrieve a file based on the provided input DTO."""
        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        query = self.repository.get_query().filter_by(**params)
        file = self.repository.execute_one(query)
        return FileOutputDto._to_dto(file) if file else None

    def get_by_tags(self, ids: List[int]) -> List[FileOutputDto]:
        """Retrieve files associated with the given tag IDs."""
        query = self.repository.get_query().select_from(File).join(file_tags)
        if ids:
            query = query.filter(file_tags.c.tag_id.in_(ids))
        files = self.repository.execute_all(query)
        return list(map(FileOutputDto._to_dto, files))

    def create(self, input: FileInputDto) -> FileOutputDto:
        """Create a new file with the given input DTO."""
        file = File(
            name=input.name,
            file_type=input.file_type,
            size=input.size,
            user_id=input.user_id,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        self.repository.create(file)
        return FileOutputDto._to_dto(file)

    def update(self, id: int, input: FileInputDto) -> FileOutputDto:
        """Update an existing file by its ID."""
        file = self.repository.get(id)
        if file is None:
            return
        file.name = input.name
        file.file_type = input.file_type
        file.size = input.size
        file.user_id = input.user_id
        file.creation_date = input.creation_date
        file.update_date = input.update_date
        self.repository.update(file)
        return FileOutputDto._to_dto(file)

    def delete(self, id: int) -> None:
        """Delete a file by its ID."""
        self.repository.delete(id)

    def delete_by_tags(self, ids: List[int]) -> None:
        """Delete files associated with the given tag IDs."""
        files_to_delete = self.get_by_tags(ids)
        for file in files_to_delete:
            self.repository.delete(file)
