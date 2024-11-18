from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from models import Base


class Repository:
    """Repository class for managing database operations."""

    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        Base.metadata.create_all(self.engine, checkfirst=True)

    def get_session(self):
        return self.Session()

    def add(self, obj):
        """Add a new object to the database."""
        session = self.get_session()
        try:
            session.add(obj)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get(self, model, id):
        """Retrieve an object by its ID."""
        session = self.get_session()
        try:
            return session.query(model).filter_by(id=id).first()
        finally:
            session.close()

    def get_all(self, model):
        """Retrieve all objects of a given model."""
        session = self.get_session()
        try:
            return session.query(model).all()
        finally:
            session.close()

    def update(self, obj):
        """Update an existing object in the database."""
        session = self.get_session()
        try:
            session.merge(obj)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete(self, obj):
        """Delete an object from the database."""
        session = self.get_session()
        try:
            session.delete(obj)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
