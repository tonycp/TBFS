from sqlalchemy.exc import SQLAlchemyError

import logging

from logic.dtos import UserInputDto, UserOutputDto
from data import User, Repository

__all__ = ["UserService"]


class UserService:
    def __init__(self, repository: Repository[User]):
        self.repository = repository

    def get(self, input: UserInputDto) -> User | None:
        """Retrieve a user based on the provided input DTO."""
        logging.info(f"Getting user with input: {input}")
        params = {
            key: value for key, value in input.to_dict().items() if value is not None
        }
        query = self.repository.get_query().filter_by(**params)
        try:
            result = self.repository.first(query)
            logging.info(f"User retrieved: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user: {e}")
            return None

    def create(self, input: UserInputDto) -> UserOutputDto | None:
        """Create a new user."""
        logging.info(f"Creating user with input: {input}")
        user = User(
            name=input.name,
            creation_date=input.creation_date,
            update_date=input.update_date,
        )
        try:
            result = self.repository.create(user, UserOutputDto._to_dto)
            logging.info(f"User created: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error creating user: {e}")
            return None

    def update(self, id: int, input: UserInputDto) -> UserOutputDto | None:
        """Update a user by its ID."""
        logging.info(f"Updating user with ID: {id} and input: {input}")
        user = self.repository.get(id)
        if user is None:
            return None

        user.name = input.name
        user.creation_date = input.creation_date
        user.update_date = input.update_date
        try:
            self.repository.update(user)
            result = UserOutputDto._to_dto(user)
            logging.info(f"User updated: {result}")
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error updating user: {e}")
            return None

    def delete(self, id: int) -> None:
        """Delete a user by its ID."""
        logging.info(f"Deleting user with ID: {id}")
        user = self.repository.get(id)
        if user:
            try:
                self.repository.delete(user)
                logging.info(f"User deleted: {id}")
            except SQLAlchemyError as e:
                logging.error(f"Error deleting user: {e}")
