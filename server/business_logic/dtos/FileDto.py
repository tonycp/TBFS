from __future__ import annotations
from datetime import datetime

__all__ = ["FileDto"]


class FileDto:
    """
    Strongly typed class to represent file input data transfer object.

    Attributes:
        name (str): Name of the file.
        file_type (str): Type of the file.
        size (int): Size of the file in bytes.
        user_id (int): ID of the user who uploaded the file.
        creation_date (datetime): Creation date of the file.
        update_date (datetime): Update date of the file.
    """

    def __init__(
        self,
        name: str,
        file_type: str,
        size: int,
        user_id: int,
        creation_date: datetime,
        update_date: datetime,
    ) -> None:
        self.name = name
        self.file_type = file_type
        self.size = size
        self.user_id = user_id
        self.creation_date = creation_date
        self.update_date = update_date

    def __repr__(self) -> str:
        return f"FileInputDto(name={self.name!r}, file_type={self.file_type!r}, size={self.size!r}, user_id={self.user_id!r})"
