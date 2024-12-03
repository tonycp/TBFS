from __future__ import annotations
from datetime import datetime

__all__ = ["UserInputDto", "UserOutputDto"]


class UserInputDto:
    def __init__(
        self,
        name: str,
        is_connected: bool,
        creation_date: datetime | str = datetime.now(),
        update_date: datetime | str = datetime.now(),
    ) -> None:
        if isinstance(creation_date, str):
            creation_date = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S")
        if isinstance(update_date, str):
            update_date = datetime.strptime(update_date, "%Y-%m-%d %H:%M:%S")

        self.name = name
        self.is_connected = is_connected
        self.creation_date = creation_date
        self.update_date = update_date

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "is_connected": self.is_connected,
            "creation_date": self.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "update_date": self.update_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __repr__(self) -> str:
        return f"UserInputDto(name={self.name!r}, is_connected={self.is_connected!r})"


class UserOutputDto(UserInputDto):
    def __init__(self, id: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.id = id

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            **UserInputDto.to_dict(self),
        }

    def __repr__(self) -> str:
        return f"UserOutputDto(id={self.id!r}, name={self.name!r}, is_connected={self.is_connected!r})"
