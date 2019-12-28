import datetime
import logging
import os
import base64
import contextlib
import math

from typing import Optional

import pygments.lexers
import pygments.formatters

from sqlalchemy import (
    Integer,
    Column,
    String,
    DateTime,
    Text,
    ForeignKey,
    create_engine,
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from pinnwand import configuration, error


log = logging.getLogger(__name__)

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


class _Base(object):
    """Base class which provides automated table names
    and a primary key column."""

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return str(cls.__name__.lower())  # type: ignore

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=_Base)


class Paste(Base):  # type: ignore
    """The Paste model represents a single Paste."""

    pub_date = Column(DateTime)
    chg_date = Column(DateTime)

    paste_id = Column(String(250), unique=True)
    removal_id = Column(String(250), unique=True)

    src = Column(String(250))

    exp_date = Column(DateTime)

    files = relationship("File", cascade="all,delete", backref="paste")

    def create_hash(self, length: int = 3) -> str:
        return (
            base64.b32encode(os.urandom(length))
            .decode("ascii")
            .replace("=", "")
        )

    def create_paste_id(self) -> str:
        """Auto lengthening and collision checking way to create paste ids."""

        with session() as database:
            # We count our new paste as well
            count = database.query(Paste).count() + 1

            # The amount of bits necessary to store that count times two, then
            # converted to bytes with a minimum of 1.

            # We double the count so that we always keep half of the space
            # available (e.g we increase the number of bytes at 127 instead of
            # 255). This ensures that the probing below can find an empty space
            # fast in case of collision.
            necessary = math.ceil(math.log2(count * 2)) // 8 + 1

            # Now generate random ids in the range with a maximum amount of
            # retries, continuing until an empty slot is found
            tries = 0
            paste_id = self.create_hash(necessary)

            while (
                database.query(Paste).filter_by(paste_id=paste_id).one_or_none()
            ):
                log.debug("Paste.create_paste_id triggered a collision")
                if tries > 10:
                    raise RuntimeError(
                        "We exceeded our retry quota on a collision."
                    )
                tries += 1
                paste_id = self.create_hash(necessary)

            return paste_id

    def create_removal_id(self) -> str:
        """Static lengths removal id."""
        return self.create_hash(8)

    def __init__(
        self,
        expiry: datetime.timedelta = datetime.timedelta(days=7),
        src: str = None,
    ) -> None:
        # Generate a paste_id and a removal_id
        # Unless someone proves me wrong that I need to check for collisions
        # my famous last words will be that the odds are astronomically small
        self.paste_id = self.create_paste_id()
        self.removal_id = self.create_removal_id()

        self.pub_date = datetime.datetime.utcnow()
        self.chg_date = datetime.datetime.utcnow()

        self.src = src

        # The expires date is the pub_date with the delta of the expiry
        if expiry:
            self.exp_date = self.pub_date + expiry
        else:
            self.exp_date = None

    def __repr__(self) -> str:
        return f"<Paste(paste_id={self.paste.id})>"


class File(Base):  # type: ignore
    paste_id = Column(ForeignKey("paste.id"))

    pub_date = Column(DateTime)
    chg_date = Column(DateTime)

    lexer = Column(String(250))

    raw = Column(Text(configuration.paste_size))
    fmt = Column(Text(configuration.paste_size))

    filename = Column(String(250))

    def __init__(
        self, raw: str, lexer: str = "text", filename: Optional[str] = None,
    ) -> None:
        # Start with some basic housekeeping related to size
        if len(raw) > configuration.paste_size:
            raise error.ValidationError(
                f"Text exceeds size limit {configuration.paste_size//1024} (kB)"
            )

        self.pub_date = datetime.datetime.utcnow()
        self.chg_date = datetime.datetime.utcnow()

        self.raw = raw

        self.filename = filename

        self.lexer = lexer

        lexer = pygments.lexers.get_lexer_by_name(lexer)
        formatter = pygments.formatters.HtmlFormatter(  # pylint: disable=no-member
            linenos=True, cssclass="source"
        )

        formatted = pygments.highlight(self.raw, lexer, formatter)

        if len(formatted) >= configuration.paste_size:
            raise error.ValidationError(
                f"Highlighted text exceeds size limit ({configuration.paste_size//1024} kB)"
            )

        self.fmt = formatted
