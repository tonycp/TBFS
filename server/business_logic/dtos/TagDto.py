from __future__ import annotations
from datetime import datetime

__all__ = ["TagDto"]


class TagDto:
    def __init__(
        self,
        name: str,
        creation_date: datetime | str = datetime.now(),
        update_date: datetime | str = datetime.now(),
    ) -> None:
        if isinstance(creation_date, str):
            creation_date = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S")
        if isinstance(update_date, str):
            update_date = datetime.strptime(update_date, "%Y-%m-%d %H:%M:%S")

        self.name = name
        self.creation_date = creation_date
        self.update_date = update_date

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "creation_date": self.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "update_date": self.update_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __repr__(self) -> str:
        return f"TagInputDto(name={self.name!r})"
