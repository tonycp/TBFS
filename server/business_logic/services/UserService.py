from ..dtos import UserInputDto, UserOutputDto
from ..business_data import User, Repository

__all__ = ["UserService"]


class UserService:
    def __init__(self, repository: Repository[User]):
        self.repository = repository

    def get_user(self, file_input: UserInputDto) -> User:
        params = {}
        for key, value in file_input.to_dict():
            if value is not None:
                params[key] = value
        return self.repository.get_query().filter_by(**params).first()

    def create_user(self, input: UserInputDto):
        """Create a new user."""
        user = User(
            name=input.name,
            is_connected=input.is_connected,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        self.repository.create(user)
        return user

    def update_user(self, user_id: int, input: UserInputDto):
        """Update a user by its ID."""
        user = self.repository.get(user_id)
        user.name = input.name
        user.is_connected = input.is_connected
        user.creation_date = input.creation_date
        user.update_date = input.update_date
        self.repository.update(user)
        return user

    def delete_user(self, user_id: int):
        """Delete a user by its ID."""
        self.repository.delete(user_id)
