"""Collection of pinnwand's command line entry points that allow you to start
a HTTP server, add and remove paste, initialize the database and reap expired
pastes."""

import click
import sys
import logging

from datetime import datetime, timedelta

import tornado.ioloop

from pinnwand.database import Base, session_factory, Paste
from pinnwand.http import make_application


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@click.group()
def main() -> None:
    """Pinnwand pastebin software."""
    print("Running main")


@main.command()
def init() -> None:
    """Create pinnwand's database models."""
    Base.metadata.create_all(session_factory.engine)


@main.command()
def http() -> None:
    """Run pinnwand's HTTP server."""
    application = make_application()
    application.listen(8000)
    tornado.ioloop.IOLoop.current().start()


@main.command()
def add() -> None:
    """Add a paste to pinnwand's database from stdin."""
    paste = Paste(sys.stdin.read(), lexer="html", expiry=timedelta(days=1))

    with session_factory() as session:
        session.add(paste)
        session.commit()


@main.command()
def delete() -> None:
    """Delete a paste from pinnwand's database."""
    paste = session.query(Paste).filter(Paste.id == int(args[1])).first()

    with session_factory() as session:
        session.delete(paste)
        session.commit()


@main.command()
def reap() -> None:
    """Delete all pastes that are past their expiry date in pinnwand's
       database."""
    pastes = session.query(Paste).filter(Paste.exp_date < datetime.now()).all()

    with session_factory() as session:
        for paste in pastes:
            session.delete(paste)
        session.commit()
