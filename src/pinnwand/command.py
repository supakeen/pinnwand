"""Collection of pinnwand's command line entry points that allow you to start
a HTTP server, add and remove paste, initialize the database and reap expired
pastes."""

import logging
import sys
from datetime import timedelta
from typing import Optional

import click
import tornado.ioloop

from pinnwand import logger
from pinnwand.configuration import Configuration, ConfigurationProvider
from pinnwand.database import models, manager, utils

log = logger.get_logger(__name__)


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

    configuration: Configuration = ConfigurationProvider.get_config()
    # First check if we have a configuration path
    if configuration_path:
        configuration.load_config_file(configuration_path)

    configuration.load_environment()

    engine = manager.DatabaseManager.get_engine()
    utils.create_tables(engine)


@main.command()
@click.option("--port", default=8000, help="Port to listen to.")
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="To start tornado server in debug mode or not",
)
def http(port: int, debug: bool) -> None:
    """Run pinnwand's HTTP server."""
    from pinnwand import utility
    from pinnwand.app import make_application

    configuration: Configuration = ConfigurationProvider.get_config()

    # Reap expired pastes on startup (we might've been shut down for a while)
    utility.reap()

    # Schedule reaping every 1800 seconds
    reap_task = tornado.ioloop.PeriodicCallback(
        utility.async_reap, configuration.reaping_periodicity
    )
    reap_task.start()

    application = make_application(debug)
    application.listen(port, xheaders=True)

    tornado.ioloop.IOLoop.current().start()


@main.command()
@click.option("--lexer", default="text", help="Lexer to use.")
def add(lexer: str) -> None:
    """Add a paste to pinnwand's database from stdin."""
    from pinnwand import utility

    if lexer not in utility.list_languages():
        log.error("add: unknown lexer")
        return

    paste = models.Paste(
        utility.slug_create(), expiry=timedelta(days=1).seconds
    )
    file = models.File(paste.slug, sys.stdin.read(), lexer=lexer)
    paste.files.append(file)

    with manager.DatabaseManager.get_session() as session:
        session.add(paste)
        session.commit()

        log.info("add: paste created: %s", paste.slug)


@main.command()
@click.option("--paste", help="database.Paste identifier.", required=True)
def delete(paste: str) -> None:
    """Delete a paste from pinnwand's database."""

    with manager.DatabaseManager.get_session() as session:
        paste_object = (
            session.query(models.Paste)
            .filter(models.Paste.slug == paste)
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

    from pinnwand import utility

    with manager.DatabaseManager.get_session() as session:
        files = session.query(models.File).all()

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
