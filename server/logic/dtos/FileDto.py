from __future__ import annotations
from datetime import datetime
from ..business_data import File

__all__ = ["FileInputDto", "FileOutputDto"]


class FileBaseDto:
    def __init__(
        self,
        name: str,
        file_type: str,
        size: int,
        user_id: int,
        creation_date: datetime | str,
        update_date: datetime | str,
    ):
        if isinstance(creation_date, str):
            creation_date = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S")
        if isinstance(update_date, str):
            update_date = datetime.strptime(update_date, "%Y-%m-%d %H:%M:%S")

        self.name = name
        self.file_type = file_type
        self.size = size
        self.user_id = user_id
        self.creation_date = creation_date
        self.update_date = update_date

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "file_type": self.file_type,
            "size": self.size,
            "user_id": self.user_id,
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
        return f"FileBaseDto(name={self.name!r}, file_type={self.file_type!r}, size={self.size!r}, user_id={self.user_id!r})"


class FileInputDto(FileBaseDto):
    """
    Strongly typed class to represent file input data transfer object.

    Attributes:
        name (str): Name of the file.
        file_type (str): Type of the file.
        size (int): Size of the file in bytes.
        user_id (int): ID of the user who uploaded the file.
        creation_date (datetime): Creation date of the file.
        update_date (datetime): Update date of the file.
        content (str): Content of the file.
    """

    def __init__(self, content: str, **kwargs) -> None:
        FileBaseDto.__init__(self, **kwargs)
        self.content = content.encode("utf-8")

    def to_dict(self, with_content: bool = False) -> dict[str, str]:
        result = FileBaseDto.to_dict(self)
        if with_content:
            result["content"] = self.content.decode("utf-8")
        return result


class FileOutputDto(FileBaseDto):
    """
    Strongly typed class to represent file output data transfer object.

    Attributes:
        id (int): Id of the file.
        name (str): Name of the file.
        file_type (str): Type of the file.
        size (int): Size of the file in bytes.
        user_id (int): ID of the user who uploaded the file.
        creation_date (datetime): Creation date of the file.
        update_date (datetime): Update date of the file.
    """

    def __init__(self, id: str, **kwargs) -> None:
        FileBaseDto.__init__(self, **kwargs)
        self.id = id

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            **FileBaseDto.to_dict(self),
        }

    def __repr__(self) -> str:
        return f"FileInputDto(id={self.id}, name={self.name!r}, file_type={self.file_type!r}, size={self.size!r})"

    @staticmethod
    def _to_dto(file: File) -> FileOutputDto:
        return FileOutputDto(
            id=file.id,
            name=file.name,
            file_type=file.file_type,
            size=file.size,
            user_id=file.user_id,
            creation_date=file.creation_date,
            update_date=file.update_date,
        )
