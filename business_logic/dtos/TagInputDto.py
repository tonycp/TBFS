from __future__ import annotations

from datetime import datetime


class TagInputDto:
    def __init__(self, name: str, creation_date: datetime, update_date: datetime) -> None:
        self.name = name
        self.creation_date = creation_date
        self.update_date = update_date

    def __repr__(self) -> str:
        return f"TagInputDto(name={self.name!r})"