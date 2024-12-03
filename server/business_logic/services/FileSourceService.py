from ..dtos import FileSourceInputDto
from ..business_data import FileSource, file_tags, Repository

__all__ = ["FileSourceService"]


class FileSourceService:
    def __init__(self, repository: Repository[FileSource]) -> None:
        self.repository = repository

    def get_file_source(self, file_input: FileSourceInputDto) -> FileSource:
        params = {}
        for key, value in file_input.to_dict():
            if value is not None:
                params[key] = value
        return self.repository.get_query().filter_by(**params).first()

    def get_all_file_sources(self) -> list[FileSource]:
        return self.repository.get_all()

    def get_file_sources_by_file_id(self, file_id: int) -> list[FileSource]:
        return (
            self.repository.get_query()
            .join(FileSource.file)
            .filter_by(file_id=file_id)
            .all()
        )

    def get_file_sources_by_tag_id(self, tag_id: int) -> list[FileSource]:
        return (
            self.repository.get_query().join(file_tags).filter_by(tag_id=tag_id).all()
        )

    def create_file_source(self, file_source: FileSourceInputDto) -> FileSource:
        new_file_source = FileSource(
            file_id=file_source.file_id,
            chunk_size=file_source.chunk_size,
            chunk_number=file_source.chunk_number,
            url=file_source.url,
            creation_date=file_source.creation_date,
            update_date=file_source.update_date,
        )
        self.repository.create(new_file_source)
        return new_file_source

    def update_file_source(
        self, file_source_id: int, file_source: FileSourceInputDto
    ) -> FileSource:
        file_source = self.repository.get(file_source_id)
        file_source.file_id = file_source.file_id
        file_source.chunk_size = file_source.chunk_size
        file_source.chunk_number = file_source.chunk_number
        file_source.url = file_source.url
        file_source.creation_date = file_source.creation_date
        file_source.update_date = file_source.update_date
        self.repository.update(file_source)
        return file_source

    def delete_file_source(self, file_source_id: int) -> None:
        self.repository.delete(file_source_id)
