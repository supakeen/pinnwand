import tempfile

from click.testing import CliRunner
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pinnwand.command as command
from pinnwand.configuration import Configuration, ConfigurationProvider
from pinnwand.database import manager, models, utils


def test_main():
    runner = CliRunner()

    result = runner.invoke(command.main, [])
    assert result.exit_code == 2

    result = runner.invoke(command.main, ["unknown"])
    assert result.exit_code == 2

    result = runner.invoke(command.main, ["--configuration-path"])
    assert result.exit_code == 2

    result = runner.invoke(
        command.main, ["--configuration-path", "/spam/eggs/ham"]
    )
    assert result.exit_code == 2

    result = runner.invoke(
        command.main, ["--configuration-path", "/spam/eggs/ham", "reap"]
    )
    assert result.exit_code == 1

    with tempfile.NamedTemporaryFile() as f:
        result = runner.invoke(
            command.main, ["--configuration-path", f.name, "reap"]
        )
        assert result.exit_code == 0

    with tempfile.NamedTemporaryFile() as f:
        f.write(b"foo=1")
        f.flush()

        result = runner.invoke(
            command.main, ["--configuration-path", f.name, "reap"]
        )
        assert result.exit_code == 0

        configuration: Configuration = ConfigurationProvider.get_config()
        assert configuration._foo == 1


def test_reap():
    runner = CliRunner()

    result = runner.invoke(command.main, ["reap"])
    assert result.exit_code == 0

    result = runner.invoke(command.main, ["reap", "unknown"])
    assert result.exit_code == 2


def test_add():
    runner = CliRunner()

    result = runner.invoke(command.main, ["add"])
    assert result.exit_code == 1

    result = runner.invoke(command.main, ["add", "--lexer"])
    assert result.exit_code == 2

    result = runner.invoke(command.main, ["add", "--lexer", "python"])
    assert result.exit_code == 1

    result = runner.invoke(command.main, ["add", "--lexer", "cheese-is-nice"])
    assert result.exit_code == 0  # XXX bug, unknown lexer


def test_delete():
    runner = CliRunner()

    result = runner.invoke(command.main, ["delete"])
    assert result.exit_code == 2

    result = runner.invoke(command.main, ["delete", "unknown"])
    assert result.exit_code == 2

    result = runner.invoke(command.main, ["delete", "--paste"])
    assert result.exit_code == 2

    result = runner.invoke(command.main, ["delete", "--paste", "unknown"])
    assert result.exit_code == 1


def test_resyntax_uses_each_files_lexer(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    utils.create_tables(engine)
    monkeypatch.setattr(manager.DatabaseManager, "_engine", engine)
    monkeypatch.setattr(
        manager.DatabaseManager, "_session_maker", sessionmaker(bind=engine)
    )
    monkeypatch.setattr(
        "pinnwand.utility.guess_language", lambda *args: "python"
    )

    paste = models.Paste("PASTE")
    paste.files = [
        models.File("FIRST", "print(123)", "text"),
        models.File("SECOND", "print(123)", "autodetect"),
        models.File("THIRD", "print(123)", "text"),
    ]
    expected = [file.fmt for file in paste.files]
    with manager.DatabaseManager.get_session() as session:
        for file in paste.files:
            file.fmt = "outdated"
        session.add(paste)
        session.commit()

    result = CliRunner().invoke(command.main, ["resyntax"])
    assert result.exit_code == 0, result.output
    with manager.DatabaseManager.get_session() as session:
        files = session.query(models.File).order_by(models.File.id).all()
        assert [file.fmt for file in files] == expected
    engine.dispose()
