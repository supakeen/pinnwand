import asyncio
import os
import tempfile
import toml
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, insert


import pytest
from click.testing import CliRunner

from pinnwand import command, utility
from pinnwand.database import utils, manager, models

config_path = os.path.join("test", "e2e", "pinnwand.toml")


@pytest.fixture(scope="function")
def temp_database_url() -> str:
    """Override the config's database_url with a temporary one."""
    with tempfile.NamedTemporaryFile(suffix="", delete=False) as temp:
        props = toml.load(config_path)
        url = f"sqlite:///{temp.name}"
        props["database_uri"] = url
        with open(config_path, "w") as config_file:
            toml.dump(props, config_file)

        yield url


@patch("pinnwand.utility.reap")
@pytest.mark.asyncio
async def test_reaping_tasks_running_periodicity(
    reap_utility_mock: MagicMock, temp_database_url
):
    """Test that the reaping task gets executed every period T."""
    runner = CliRunner()

    runner.invoke(command.main, ["--configuration-path", config_path, "http"])

    await asyncio.sleep(5)

    # 1 call when the http command starts
    # Since the periodicity is set to 2 seconds, the task will execute 2 times within 5 seconds
    # Making a total of 3
    assert reap_utility_mock.call_count == 3


@patch("pinnwand.database.manager.DatabaseManager.get_engine")
@pytest.mark.asyncio
async def test_pastes_reaped_on_startup(
    get_engine_patch: MagicMock, temp_database_url
):
    """Ensures that pastes are reaped correctly upon startup."""

    engine = create_engine(temp_database_url)
    get_engine_patch.return_value = engine

    engine = manager.DatabaseManager.get_engine()
    utils.create_tables(engine)

    slugs = [utility.slug_create() for _ in range(8)]
    persistent_paste_slug = utility.slug_create()
    pastes = []
    for text in slugs:
        paste = models.Paste(text, expiry=1)
        file = models.File(paste.slug, text, lexer="text")
        paste.files.append(file)
        pastes.append(paste)

    persistent_paste_text = "I will survive!"
    persistent_paste = models.Paste(persistent_paste_slug, expiry=30)
    file = models.File(persistent_paste.slug, persistent_paste_text, lexer="text")
    persistent_paste.files.append(file)
    pastes.append(persistent_paste)

    with manager.DatabaseManager.get_session() as session:
        session.add_all(pastes)
        session.commit()

    # This does two things.
    # 1. Most importantly, yields control back to this control from tornado's started loop in the http command.
    # 2. Ensures that the pastes are given enough time to expire.
    await asyncio.sleep(2)

    runner = CliRunner()
    runner.invoke(command.main, ["--configuration-path", config_path, "http"])

    with manager.DatabaseManager.get_session() as session:
        paste = (
            session.query(models.Paste)
            .filter(models.Paste.slug == persistent_paste_slug)
            .first()
        )
        assert paste is not None
        assert persistent_paste_text == paste.files[0].raw

        for slug in slugs:
            paste = (
                session.query(models.Paste)
                .filter(models.Paste.slug == slug)
                .first()
            )
            assert paste is None
