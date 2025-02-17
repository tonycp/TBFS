from __future__ import annotations
from datetime import datetime

from data import FileSource

__all__ = ["FileSourceInputDto", "FileSourceOutputDto"]


class FileSourceInputDto:
    def __init__(
        self,
        file_id: int,
        chunk_size: int,
        url: str,
        creation_date: datetime | str = datetime.now(),
        update_date: datetime | str = datetime.now(),
    ) -> None:
        if isinstance(creation_date, str):
            creation_date = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S")
        if isinstance(update_date, str):
            update_date = datetime.strptime(update_date, "%Y-%m-%d %H:%M:%S")

        self.file_id = file_id
        self.chunk_size = chunk_size
        self.url = url
        self.creation_date = creation_date
        self.update_date = update_date

    def to_dict(self) -> dict[str, str]:
        return {
            "file_id": self.file_id,
            "chunk_size": self.chunk_size,
            "url": self.url,
            "creation_date": (
                self.creation_date.strftime("%Y-%m-%d %H:%M:%S")
                if self.creation_date
                else None
            ),
            "update_date": (
                self.update_date.strftime("%Y-%m-%d %H:%M:%S")
                if self.update_date
                else None
            ),
        }

    def __repr__(self) -> str:
        return f"FileSourceInputDto(file_id={self.file_id!r}, chunk_size={self.chunk_size!r}, url={self.url!r})"


class FileSourceOutputDto(FileSourceInputDto):
    def __init__(self, id: int, **kwargs) -> None:
        FileSourceInputDto.__init__(self, **kwargs)
        self.id = id

    def to_dict(self) -> dict[str, str]:
        return {**FileSourceInputDto.to_dict(self), "id": self.id}

    def __repr__(self) -> str:
        return f"FileSourceOutputDto(id={self.id!r}, file_id={self.file_id!r}, chunk_size={self.chunk_size!r}, url={self.url!r})"

    @staticmethod
    def _to_dto(source: FileSource) -> FileSourceOutputDto:
        return FileSourceOutputDto(
            id=source.id,
            file_id=source.file_id,
            chunk_size=source.chunk_size,
            url=source.url,
            creation_date=source.creation_date,
            update_date=source.update_date,
        )
