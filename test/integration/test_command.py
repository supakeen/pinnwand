import tempfile

from click.testing import CliRunner

import pinnwand.command as command


def test_main():
    runner = CliRunner()

    result = runner.invoke(command.main, [])
    assert result.exit_code == 0

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

        import pinnwand.configuration

        assert pinnwand.configuration.foo == 1


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
