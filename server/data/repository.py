from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session, Session as SessionType, Query
from typing import Callable, TypeVar, Generic, Type, List, Optional
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

    def get(self, id: int) -> Optional[ModelType]:
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

    def all(self, query: Query[ModelType], session: Optional[SessionType] = None) -> List[ModelType]:
        """Execute a given query and return all results."""
        if session is None:
            with self.get_session() as session:
                return query.with_session(session).all()
        else:
            return query.with_session(session).all()

    def first(self, query: Query[ModelType], session: Optional[SessionType] = None) -> Optional[ModelType]:
        """Execute a given query and return the first result."""
        if session is None:
            with self.get_session() as session:
                return query.with_session(session).first()
        else:
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

    def create_all(self, objs: List[ModelType]) -> None:
        """Add multiple new objects of type ModelType to the database."""
        with self.get_session() as session:
            self._modify_bd(objs, session, session.add_all)

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
            print(f"Database error: {e}")
            raise e

    def transaction(self, operations: Callable[[SessionType], None]) -> None:
        """Execute multiple operations in a single transaction."""
        with self.get_session() as session:
            try:
                operations(session)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                print(f"Transaction error: {e}")
                raise e

    def filter_by(self, **kwargs) -> List[ModelType]:
        """Retrieve objects of type ModelType filtered by given criteria."""
        with self.get_session() as session:
            return session.query(self.model).filter_by(**kwargs).all()

    def order_by(self, *criteria) -> List[ModelType]:
        """Retrieve objects of type ModelType ordered by given criteria."""
        with self.get_session() as session:
            return session.query(self.model).order_by(*criteria).all()

def get_repository(model: Type[ModelType], db_url: str) -> Repository[ModelType]:
    return Repository(model, db_url)
