from typing import Mapping
from ..dtos import FileInputDto, FileOutputDto
from ..business_data import File, file_tags, Repository

__all__ = ["FileService"]


class FileService:
    def __init__(self, repository: Repository[File]):
        self.repository = repository

    def add_tag(self, file_id, tag_id):
        try:
            with self.repository.get_session() as session:
                result = session.execute(
                    file_tags.select().filter_by(file_id=file_id, tag_id=tag_id)
                )
                if result.one_or_none() is None:
                    session.execute(
                        file_tags.insert().values(file_id=file_id, tag_id=tag_id)
                    )
                session.commit()
        except Exception as e:
            pass

    def get_file(self, file_input: FileInputDto) -> File:
        params = {}
        for key, value in file_input.to_dict().items():
            if value is not None:
                params[key] = value
        return self.repository.get_query().filter_by(**params).first()

    def get_files_by_tags(self, tag_ids: list[int]):
        query = self.repository.get_query().select_from(File).join(file_tags)
        if len(tag_ids) != 0:
            query = query.filter(file_tags.c.tag_id.in_(tag_ids))
        return query.all()

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
        file = self.repository.get(file_id)
        file.name = file_input.name
        file.file_type = file_input.file_type
        file.size = file_input.size
        file.user_id = file_input.user_id
        file.creation_date = file_input.creation_date
        file.update_date = file_input.update_date
        self.repository.update(file)

    def delete_file(self, file_id: int):
        """Delete a file by its ID."""
        self.repository.delete(file_id)

    def delete_file_by_tags(self, tag_ids: list[int]):
        files_ids = self.get_files_by_tags(tag_ids)
        for file in files_ids:
            self.repository.delete(file)

    def delete_tag(self, file_id: int, tag_id: int):
        try:
            with self.repository.get_session() as session:
                query = file_tags.delete().where(
                    file_tags.c.file_id == file_id,
                    file_tags.c.tag_id == tag_id,
                )
                session.execute(query)
                session.commit()
        except Exception as e:
            pass
