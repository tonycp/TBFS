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
        creation_date: datetime,
        update_date: datetime,
    ) -> None:
        self.file_id = file_id
        self.chunk_size = chunk_size
        self.chunk_number = chunk_number
        self.url = url
        self.creation_date = creation_date
        self.update_date = update_date

    def __repr__(self) -> str:
        return f"FileSourceInputDto(file_id={self.file_id!r}, chunk_size={self.chunk_size!r}, chunk_number={self.chunk_number!r}, url={self.url!r})"