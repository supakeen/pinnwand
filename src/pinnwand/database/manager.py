import contextlib

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


from pinnwand.configuration import Configuration, ConfigurationProvider


class DatabaseManager:
    """An entity responsible for managing database-related resources."""

    _engine: Engine = None
    _session_maker = None

    @classmethod
    def get_engine(cls):
        """Return an engine for the currently configured connection string."""
        configuration: Configuration = ConfigurationProvider.get_config()
        if not cls._engine:
            cls._engine = create_engine(configuration.database_uri)

        return cls._engine

    @classmethod
    @contextlib.contextmanager
    def get_session(cls) -> Session:
        """Create a self-disposable database session."""
        if not cls._session_maker:
            cls._session_maker = sessionmaker(bind=cls.get_engine())

        new_session = cls._session_maker()
        try:
            yield new_session
        except Exception:
            new_session.rollback()
            raise
        finally:
            new_session.close()
