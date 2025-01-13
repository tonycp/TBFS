from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session, Session as SessionType, Query
from typing import Callable, TypeVar, Generic, Type, List
from .models import Base

ModelType = TypeVar("ModelType", bound=Base)
ModelTypeDTO = TypeVar("ModelTypeDTO")


class Repository(Generic[ModelType]):
    """Generic repository for performing database operations on models of type ModelType."""

    def __init__(self, model: Type[ModelType], db_url: str) -> None:
        self.model: Type[ModelType] = model
        self.engine: Engine = create_engine(db_url)
        self.Session: scoped_session[SessionType] = scoped_session(
            sessionmaker(bind=self.engine)
        )
        Base.metadata.create_all(self.engine, checkfirst=True)

    def get_session(self) -> SessionType:
        """Get a new session from the session factory."""
        return self.Session()

    def get(self, id: int) -> ModelType | None:
        """Retrieve an object of type ModelType by its ID."""
        with self.get_session() as session:
            return session.query(self.model).filter_by(id=id).first()

    def get_all(self) -> List[ModelType]:
        """Retrieve all objects of type ModelType."""
        with self.get_session() as session:
            return session.query(self.model).all()

    def get_query(self) -> Query[ModelType]:
        """Retrieve a query of type ModelType."""
        return self.get_session().query(self.model)

    def execute_all(self, query: Query[ModelType]) -> List[ModelType]:
        """Execute a given query and return the results."""
        with self.get_session() as session:
            return query.with_session(session).all()

    def execute_one(self, query: Query[ModelType]) -> ModelType:
        """Execute a given query and return the first result."""
        with self.get_session() as session:
            return query.with_session(session).first()

    def create(
        self,
        obj: ModelType,
        to_dto: Callable[[ModelType], ModelTypeDTO] = lambda _: None,
    ) -> ModelTypeDTO:
        """Add a new object of type ModelType to the database."""
        with self.get_session() as session:
            self._modify_bd(obj, session, session.add)
            return to_dto(obj)

    def create_all(self, obj: List[ModelType]) -> None:
        """Add multiple new objects of type ModelType to the database."""
        with self.get_session() as session:
            self._modify_bd(obj, session, session.add_all)

    def update(self, obj: ModelType) -> None:
        """Update an existing object of type ModelType in the database."""
        with self.get_session() as session:
            self._modify_bd(obj, session, session.merge)

    def delete(self, obj: ModelType) -> None:
        """Delete an object of type ModelType from the database."""
        with self.get_session() as session:
            self._modify_bd(obj, session, session.delete)

    def _modify_bd(self, obj: ModelType, session: SessionType, func: Callable) -> None:
        try:
            func(obj)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e


def get_repository(model: Type[ModelType], db_url: str) -> Repository[ModelType]:
    return Repository(model, db_url)
