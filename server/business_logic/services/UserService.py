from ..dtos import UserInputDto, UserOutputDto
from ..business_data import User, Repository

__all__ = ["UserService"]


class UserService:
    def __init__(self, repository: Repository[User]):
        self.repository = repository

    def get(self, input: UserInputDto) -> UserOutputDto | None:
        """Retrieve a user based on the provided input DTO."""
        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        query = self.repository.get_query().filter_by(**params)
        user = self.repository.execute_one(query)
        return UserOutputDto._to_dto(user) if user else None

    def create(self, input: UserInputDto) -> UserOutputDto:
        """Create a new user."""
        user = User(
            name=input.name,
            is_connected=input.is_connected,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        self.repository.create(user)
        return UserOutputDto._to_dto(user)

    def update(self, id: int, input: UserInputDto) -> UserOutputDto:
        """Update a user by its ID."""
        user = self.repository.get(id)
        if user is None:
            return None

        user.name = input.name
        user.is_connected = input.is_connected
        user.creation_date = input.creation_date
        user.update_date = input.update_date
        self.repository.update(user)
        return UserOutputDto._to_dto(user)

    def delete(self, id: int) -> None:
        """Delete a user by its ID."""
        self.repository.delete(id)
