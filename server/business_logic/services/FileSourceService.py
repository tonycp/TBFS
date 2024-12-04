from typing import List
from ..dtos import FileSourceInputDto, FileSourceOutputDto
from ..business_data import FileSource, file_tags, Repository

__all__ = ["FileSourceService"]


class FileSourceService:
    def __init__(self, repository: Repository[FileSource]) -> None:
        self.repository = repository

    def get(self, input: FileSourceInputDto) -> FileSourceOutputDto | None:
        """Retrieve a file source based on the provided input DTO."""
        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        query = self.repository.get_query().filter_by(**params)
        source = self.repository.execute_one(query)
        return FileSourceOutputDto._to_dto(source) if source else None

    def get_all(self) -> List[FileSourceOutputDto]:
        """Retrieve all file sources."""
        sources = self.repository.get_all()
        return list(map(FileSourceOutputDto._to_dto, sources))

    def get_by_file_id(self, id: int) -> List[FileSourceOutputDto]:
        """Retrieve file sources associated with the given file ID."""
        query = self.repository.get_query().join(FileSource.file).filter_by(file_id=id)
        sources = self.repository.execute_all(query)
        return list(map(FileSourceOutputDto._to_dto, sources))

    def get_by_tag_id(self, id: int) -> List[FileSourceOutputDto]:
        """Retrieve file sources associated with the given tag ID."""
        query = self.repository.get_query().join(file_tags).filter_by(tag_id=id)
        sources = self.repository.execute_all(query)
        return list(map(FileSourceOutputDto._to_dto, sources))

    def create(self, input: FileSourceInputDto) -> FileSourceOutputDto:
        """Create a new file source with the given input DTO."""
        source = FileSource(
            file_id=input.file_id,
            chunk_size=input.chunk_size,
            chunk_number=input.chunk_number,
            url=input.url,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        self.repository.create(source)
        return FileSourceOutputDto._to_dto(source)

    def update(self, id: int, input: FileSourceInputDto) -> FileSourceOutputDto:
        """Update an existing file source by its ID."""
        source = self.repository.get(id)
        if source is None:
            return
        source.file_id = input.file_id
        source.chunk_size = input.chunk_size
        source.chunk_number = input.chunk_number
        source.url = input.url
        source.creation_date = input.creation_date
        source.update_date = input.update_date
        self.repository.update(source)
        return FileSourceOutputDto._to_dto(source)

    def delete(self, id: int) -> None:
        """Delete a file source by its ID."""
        self.repository.delete(id)
