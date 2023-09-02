from sqlalchemy import delete, Table, MetaData
from sqlalchemy.pool import NullPool
import sqlalchemy as sql


class TestDb:
    def __init__(self, uri):
        self.uri = uri
        self._engine = sql.create_engine(uri, poolclass=NullPool)

    def clear_tables(self, *tables):
        with self._engine.connect() as connection:
            for table in tables:
                connection.execute(delete(Table(table, MetaData())))
                connection.commit()
