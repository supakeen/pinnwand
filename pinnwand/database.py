import datetime
import logging
import contextlib

from typing import Optional

import pygments.lexers

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

from pygments_better_html import BetterHtmlFormatter

from pinnwand import configuration, error, utility


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

    slug = Column(String(250), unique=True)
    removal = Column(String(250), unique=True)

    src = Column(String(250))

    exp_date = Column(DateTime)

    files = relationship("File", cascade="all,delete", backref="paste")

    def __init__(
        self,
        expiry: datetime.timedelta = datetime.timedelta(days=7),
        src: str = None,
        auto_scale: bool = True,
    ) -> None:
        # Generate a paste_id and a removal_id
        # Unless someone proves me wrong that I need to check for collisions
        # my famous last words will be that the odds are astronomically small
        self.slug = utility.slug_create(auto_scale=auto_scale)
        self.removal = utility.slug_create(auto_scale=False)

        self.pub_date = datetime.datetime.utcnow()
        self.chg_date = datetime.datetime.utcnow()

        self.src = src

        # The expires date is the pub_date with the delta of the expiry
        if expiry:
            self.exp_date = self.pub_date + expiry
        else:
            self.exp_date = None

    def __repr__(self) -> str:
        return f"<Paste(slug={self.slug})>"


class File(Base):  # type: ignore
    paste_id = Column(ForeignKey("paste.id"))
    slug = Column(String(255), unique=True)

    pub_date = Column(DateTime)
    chg_date = Column(DateTime)

    lexer = Column(String(250))

    raw = Column(Text(configuration.paste_size))
    fmt = Column(Text(configuration.paste_size))

    filename = Column(String(250))

    def __init__(
        self,
        raw: str,
        lexer: str = "text",
        filename: Optional[str] = None,
        auto_scale: bool = True,
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
        formatter = BetterHtmlFormatter(  # pylint: disable=no-member
            linenos="table", cssclass="source"
        )

        formatted = pygments.highlight(self.raw, lexer, formatter)

        if len(formatted) >= configuration.paste_size:
            raise error.ValidationError(
                f"Highlighted text exceeds size limit ({configuration.paste_size//1024} kB)"
            )

        self.fmt = formatted
        self.slug = utility.slug_create(auto_scale=auto_scale)

    @property
    def pretty_size(self) -> str:
        return utility.size_postfix(len(self.raw))
