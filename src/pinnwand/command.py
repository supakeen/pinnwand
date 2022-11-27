"""Collection of pinnwand's command line entry points that allow you to start
a HTTP server, add and remove paste, initialize the database and reap expired
pastes."""

import ast
import logging
import os
import sys
from datetime import timedelta
from typing import TYPE_CHECKING, Optional

import click
import tornado.ioloop

log = logging.getLogger(__name__)


@click.group()
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Verbosity, passing more heightens the verbosity.",
)
@click.option("--configuration-path", default=None, help="Configuration file.")
def main(verbose: int, configuration_path: Optional[str]) -> None:
    """Pinnwand pastebin software."""
    logging.basicConfig(level=10 + (logging.FATAL - verbose * 10))

    from pinnwand import configuration

    # First check if we have a configuration path
    if configuration_path:
        if (
            TYPE_CHECKING
        ):  # lie to mypy, see https://github.com/python/mypy/issues/1153
            import tomllib as toml
        else:
            try:
                import tomllib as toml
            except ImportError:
                import tomli as toml

        with open(configuration_path, "rb") as file:
            configuration_file = toml.load(file)

            for key, value in configuration_file.items():
                setattr(configuration, key, value)

    # Or perhaps we have configuration in the environment, these are prefixed
    # with PINNWAND_ and all upper case, remove the prefix, convert to
    # lowercase.
    for key, value in os.environ.items():
        if key.startswith("PINNWAND_"):
            key = key.removeprefix("PINNWAND_")
            key = key.lower()

            try:
                value = ast.literal_eval(value)
            except ValueError:
                # When `ast.literal_eval` can't parse the value into another
                # type we take it at string value
                pass

            setattr(configuration, key, value)

    from pinnwand import database

    database.Base.metadata.create_all(database._engine)


@main.command()
@click.option("--port", default=8000, help="Port to listen to.")
def http(port: int) -> None:
    """Run pinnwand's HTTP server."""
    from pinnwand import utility
    from pinnwand.http import make_application

    # Reap expired pastes on startup (we might've been shut down for a while)
    utility.reap()

    # Schedule reaping every 1800 seconds
    reap_task = tornado.ioloop.PeriodicCallback(utility.async_reap, 1_800_000)
    reap_task.start()

    application = make_application()
    application.listen(port, xheaders=True)

    tornado.ioloop.IOLoop.current().start()


@main.command()
@click.option("--lexer", default="text", help="Lexer to use.")
def add(lexer: str) -> None:
    """Add a paste to pinnwand's database from stdin."""
    from pinnwand import database, utility

    if lexer not in utility.list_languages():
        log.error("add: unknown lexer")
        return

    paste = database.Paste(
        utility.slug_create(), expiry=timedelta(days=1).seconds
    )
    file = database.File(paste.slug, sys.stdin.read(), lexer=lexer)
    paste.files.append(file)

    with database.session() as session:
        session.add(paste)
        session.commit()

        log.info("add: paste created: %s", paste.slug)


@main.command()
@click.option("--paste", help="database.Paste identifier.", required=True)
def delete(paste: str) -> None:
    """Delete a paste from pinnwand's database."""
    from pinnwand import database

    with database.session() as session:
        paste_object = (
            session.query(database.Paste)
            .filter(database.Paste.slug == paste)
            .first()
        )

        if not paste_object:
            log.error("delete: unknown paste")
            raise SystemExit(1)

        session.delete(paste_object)
        session.commit()

        log.info("delete: paste %s deleted", paste_object)


@main.command()
def reap() -> None:
    """Delete all pastes that are past their expiry date in pinnwand's
    database."""
    from pinnwand import utility

    log.warning("reap: this command is deprecated and will be removed in 1.6")

    utility.reap()


@main.command()
def resyntax() -> None:
    """Rerun `pygments` over all files in the database to update their formatted
    output."""
    import pygments.lexers
    from pygments_better_html import BetterHtmlFormatter

    from pinnwand import database, utility

    with database.session() as session:
        files = session.query(database.File).all()

        for file in files:
            if file.lexer == "autodetect":
                lexer = utility.guess_language(file.raw, file.filename)
                log.debug(f"resyntax: Language guessed as {lexer}")

            lexer = pygments.lexers.get_lexer_by_name(lexer)
            formatter = BetterHtmlFormatter(  # pylint: disable=no-member
                linenos="table", cssclass="source"
            )

            formatted = pygments.highlight(file.raw, lexer, formatter)

            file.fmt = formatted

        session.commit()

        log.info("resyntax: highlighted %d pastes", len(files))
