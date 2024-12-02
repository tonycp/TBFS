from ..dtos import UserDto
from ..business_data import User, Repository

__all__ = ["UserService"]


class UserService:
    def __init__(self, repository: Repository[User]):
        self.repository = repository

    def get_user_by_id(self, user_id: int):
        """Get a user by its ID."""
        return self.repository.get(user_id)

    def get_all_users(self):
        """Get all users."""
        return self.repository.get_all()

    def get_user_by_name(self, name: str):
        """Get a user by its name."""
        return self.repository.get_query().filter_by(name=name).first()

    def get_all_connected_users(self, is_connected: bool):
        """Get a user by its is_connected."""
        return self.repository.get_query().filter_by(is_connected=is_connected).all()

    def get_user_by_name_and_is_connected(self, name: str, is_connected: bool):
        """Get a user by its name and is_connected."""
        return (
            self.repository.get_query()
            .filter_by(name=name, is_connected=is_connected)
            .first()
        )

    def create_user(self, input: UserDto):
        """Create a new user."""
        user = User(
            name=input.name,
            is_connected=input.is_connected,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        self.repository.create(user)
        return user

    def update_user(self, user_id: int, input: UserDto):
        """Update a user by its ID."""
        user = User(
            id=user_id,
            name=input.name,
            is_connected=input.is_connected,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        self.repository.update(user)
        return user

    def delete_user(self, user_id: int):
        """Delete a user by its ID."""
        self.repository.delete(user_id)
