from __future__ import annotations
from datetime import datetime

__all__ = ["FileSourceInputDto"]


class FileSourceInputDto:
    def __init__(
        self,
        file_id: int,
        chunk_size: int,
        chunk_number: int,
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
        self.chunk_number = chunk_number
        self.url = url
        self.creation_date = creation_date
        self.update_date = update_date

    def to_dict(self) -> dict[str, str]:
        return {
            "file_id": self.file_id,
            "chunk_size": self.chunk_size,
            "chunk_number": self.chunk_number,
            "url": self.url,
            "creation_date": self.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "update_date": self.update_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __repr__(self) -> str:
        return f"FileSourceInputDto(file_id={self.file_id!r}, chunk_size={self.chunk_size!r}, chunk_number={self.chunk_number!r}, url={self.url!r})"
