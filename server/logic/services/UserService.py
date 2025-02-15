from ..dtos import UserInputDto, UserOutputDto
from ..business_data import User, Repository
from .HashService import HashService
from sqlalchemy.exc import SQLAlchemyError

__all__ = ["UserService"]

class UserService:
    def __init__(self, repository: Repository[User], hash_service: HashService):
        self.repository = repository
        self.hash_service = hash_service

    def get(self, input: UserInputDto) -> User | None:
        """Retrieve a user based on the provided input DTO."""
        key = hash(input.name)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None:
            return None

        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        params['node_id'] = node_id
        query = self.repository.get_query().filter_by(**params)
        try:
            return self.repository.first(query)
        except SQLAlchemyError as e:
            print(f"Error retrieving user: {e}")
            return None

    def create(self, input: UserInputDto) -> UserOutputDto | None:
        """Create a new user."""
        key = hash(input.name)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None:
            return None

        user = User(
            name=input.name,
            creation_date=input.creation_date,
            update_date=input.update_date,
            node_id=node_id,
        )
        try:
            return self.repository.create(user, UserOutputDto._to_dto)
        except SQLAlchemyError as e:
            print(f"Error creating user: {e}")
            return None

    def update(self, id: int, input: UserInputDto) -> UserOutputDto | None:
        """Update a user by its ID."""
        user = self.repository.get(id)
        if user is None:
            return None

        key = hash(input.name)
        node_id = self.hash_service.get_node_id(key)
        if node_id is None or user.node_id != node_id:
            return None

        user.name = input.name
        user.creation_date = input.creation_date
        user.update_date = input.update_date
        try:
            self.repository.update(user)
            return UserOutputDto._to_dto(user)
        except SQLAlchemyError as e:
            print(f"Error updating user: {e}")
            return None

    def delete(self, id: int) -> None:
        """Delete a user by its ID."""
        user = self.repository.get(id)
        if user:
            key = hash(user.name)
            node_id = self.hash_service.get_node_id(key)
            if node_id is not None and user.node_id == node_id:
                try:
                    self.repository.delete(user)
                except SQLAlchemyError as e:
                    print(f"Error deleting user: {e}")
