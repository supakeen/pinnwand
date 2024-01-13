from sqlalchemy import Engine
from .models import Base


def create_tables(engine: Engine):
    """Creates all the defined database tables."""

    Base.metadata.create_all(engine)
