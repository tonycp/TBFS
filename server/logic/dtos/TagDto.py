from __future__ import annotations
from datetime import datetime
from ..business_data import Tag

__all__ = ["TagInputDto", "TagOutputDto"]


class TagInputDto:
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
        return f"TagInputDto(name={self.name!r})"


class TagOutputDto(TagInputDto):
    def __init__(self, id: int, **kwargs) -> None:
        TagInputDto.__init__(self, **kwargs)
        self.id = id

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            **TagInputDto.to_dict(self),
        }

    def __repr__(self) -> str:
        return f"TagOutputDto(id={self.id!r}, name={self.name!r})"

    @staticmethod
    def _to_dto(tag: Tag) -> TagOutputDto:
        return TagOutputDto(
            id=tag.id,
            name=tag.name,
            creation_date=tag.creation_date,
            update_date=tag.update_date,
        )
