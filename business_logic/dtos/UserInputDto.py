from __future__ import annotations
from datetime import datetime

__all__ = ["UserInputDto"]


class UserInputDto:
    def __init__(
        self,
        name: str,
        is_connected: bool,
        creation_date: datetime,
        update_date: datetime,
    ) -> None:
        self.name = name
        self.is_connected = is_connected
        self.creation_date = creation_date
        self.update_date = update_date

    def __repr__(self) -> str:
        return f"UserInputDto(name={self.name!r}, is_connected={self.is_connected!r})"
