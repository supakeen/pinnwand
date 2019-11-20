import datetime
import logging
import os
import base64
import contextlib
from typing import Optional

import pygments.lexers
import pygments.formatters

from sqlalchemy import Integer, Column, String, DateTime, Text, create_engine
from sqlalchemy.orm import sessionmaker
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

    lexer = Column(String(250))

    raw = Column(Text(configuration.paste_size))
    fmt = Column(Text(configuration.paste_size))
    src = Column(String(250))

    exp_date = Column(DateTime)

    filename = Column(String(250))

    def create_hash(self) -> str:
        # This should organically grow as more is used, probably depending
        # on how often collissions occur.
        # Aside from that we should never repeat hashes which have been used before
        # without keeping the pastes in the database.
        # this does expose urandom directly ..., is that bad?
        return base64.b32encode(os.urandom(3)).decode("ascii").replace("=", "")

    def __init__(
        self,
        raw: str,
        lexer: str = "text",
        expiry: datetime.timedelta = datetime.timedelta(days=7),
        src: str = None,
        filename: Optional[str] = None,
    ) -> None:
        # Start with some basic housekeeping related to size
        if len(raw) > configuration.paste_size:
            raise error.ValidationError(
                f"Text exceeds size limit {configuration.paste_size//1024} (kB)"
            )

        self.pub_date = datetime.datetime.utcnow()
        self.chg_date = datetime.datetime.utcnow()

        # Generate a paste_id and a removal_id
        # Unless someone proves me wrong that I need to check for collisions
        # my famous last words will be that the odds are astronomically small
        self.paste_id = self.create_hash()
        self.removal_id = self.create_hash()

        self.raw = raw

        self.src = src

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

        # The expires date is the pub_date with the delta of the expiry
        if expiry:
            self.exp_date = self.pub_date + expiry
        else:
            self.exp_date = None

    def __repr__(self) -> str:
        return f"<Paste(paste_id={self.paste.id})>"
