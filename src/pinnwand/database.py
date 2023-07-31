import contextlib
import datetime
import logging
from datetime import timedelta
from typing import Optional

import pygments.lexers
from pygments_better_html import BetterHtmlFormatter
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
)
from sqlalchemy.orm.session import Session

from pinnwand import configuration, defensive, error, utility

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
        slug: str,
        expiry: int = 604800,
        src: Optional[str] = None,
    ) -> None:
        # Generate a paste_id and a removal_id
        # Unless someone proves me wrong that I need to check for collisions
        # my famous last words will be that the odds are astronomically small
        self.slug = slug
        self.removal = utility.slug_create(auto_scale=False)

        self.pub_date = datetime.datetime.utcnow()
        self.chg_date = datetime.datetime.utcnow()

        self.src = src

        # The expires date is the pub_date with the delta of the expiry
        self.exp_date = self.pub_date + timedelta(seconds=expiry)

    def __repr__(self) -> str:
        return f"<Paste(slug={self.slug})>"


class File(Base):  # type: ignore
    paste_id = Column(ForeignKey("paste.id"))
    slug = Column(String(255), unique=True)

    pub_date = Column(DateTime)
    chg_date = Column(DateTime)

    lexer = Column(String(250))

    raw = Column(Text)
    fmt = Column(Text)

    filename = Column(String(250))

    def __init__(
        self,
        slug: str,
        raw: str,
        lexer: str = "text",
        filename: Optional[str] = None,
    ) -> None:
        # Start with some basic housekeeping related to size
        if not len(raw):
            raise error.ValidationError("Empty pastes are not allowed")

        if len(raw) > configuration.paste_size:
            raise error.ValidationError(
                f"Text exceeds size limit {configuration.paste_size//1024} (kB)"
            )

        self.pub_date = datetime.datetime.utcnow()
        self.chg_date = datetime.datetime.utcnow()

        self.raw = raw

        if defensive.spamscore(raw) > configuration.spamscore:
            raise error.SpamError("Text exceeds spam score.")

        self.filename = filename

        self.lexer = lexer

        if lexer == "autodetect":
            lexer = utility.guess_language(raw, filename)
            log.debug(f"Language guessed as {lexer}")

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
        self.slug = slug

    @property
    def pretty_size(self) -> str:
        return utility.size_postfix(len(self.raw))
