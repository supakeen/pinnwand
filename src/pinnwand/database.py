import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from pinnwand import configuration, logger

log = logger.get_logger(__name__)

_engine = create_engine(configuration.database_uri)
_session = sessionmaker(bind=_engine)


@contextlib.contextmanager
def session() -> Session:
    a_session = _session()

    try:
        yield a_session
    except Exception:
        a_session.rollback()
        raise
    finally:
        a_session.close()
