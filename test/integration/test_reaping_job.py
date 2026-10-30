import asyncio
import os
from pathlib import Path
import tomllib
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine


import pytest
from click.testing import CliRunner
import tomli_w

from pinnwand import command, utility
from pinnwand.database import utils, manager, models

config_path = os.path.join("test", "e2e", "pinnwand.toml")


@pytest.fixture(scope="function")
def temp_config(tmp_path):
    """Create a test configuration with its own temporary database."""
    props = tomllib.loads(Path(config_path).read_text())
    url = f"sqlite:///{tmp_path / 'pinnwand.db'}"
    props["database_uri"] = url
    path = tmp_path / "pinnwand.toml"
    with path.open("wb") as config_file:
        tomli_w.dump(props, config_file)
    return path, url


@patch("pinnwand.utility.reap")
@pytest.mark.asyncio
async def test_reaping_tasks_running_periodicity(
    reap_utility_mock: MagicMock, temp_config
):
    """Test that the reaping task gets executed every period T."""
    runner = CliRunner()

    runner.invoke(
        command.main, ["--configuration-path", str(temp_config[0]), "http"]
    )

    await asyncio.sleep(5)

    # 1 call when the http command starts
    # Since the periodicity is set to 2 seconds, the task will execute 2 times within 5 seconds
    # Making a total of 3
    assert reap_utility_mock.call_count == 3


@patch("pinnwand.database.manager.DatabaseManager.get_engine")
@pytest.mark.asyncio
async def test_pastes_reaped_on_startup(
    get_engine_patch: MagicMock, temp_config
):
    """Ensures that pastes are reaped correctly upon startup."""

    engine = create_engine(temp_config[1])
    get_engine_patch.return_value = engine

    engine = manager.DatabaseManager.get_engine()
    utils.create_tables(engine)

    slugs = [utility.slug_create() for _ in range(2)]

    for text in slugs:
        paste = models.Paste(text, expiry=1)
        file = models.File(paste.slug, text, lexer="text")
        paste.files.append(file)

        with manager.DatabaseManager.get_session() as session:
            session.add(paste)
            session.commit()

    # This does two things.
    # 1. Most importantly, yields control back to this control from tornado's started loop in the http command.
    # 2. Ensures that the pastes are given enough time to expire.
    await asyncio.sleep(2)

    runner = CliRunner()
    runner.invoke(
        command.main, ["--configuration-path", str(temp_config[0]), "http"]
    )

    with manager.DatabaseManager.get_session() as session:
        for slug in slugs:
            paste = (
                session.query(models.Paste)
                .filter(models.Paste.slug == slug)
                .first()
            )
            assert paste is None
