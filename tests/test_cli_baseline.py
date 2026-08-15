from unittest.mock import Mock

from typer.testing import CliRunner

from gpt4free_tui_cli import __version__
from gpt4free_tui_cli.presentation.cli import app


def test_help_and_version_do_not_construct_database(monkeypatch) -> None:
    from gpt4free_tui_cli import bootstrap

    monkeypatch.setattr(
        bootstrap,
        "DatabaseManager",
        Mock(side_effect=AssertionError("database must stay lazy")),
    )
    runner = CliRunner()

    help_result = runner.invoke(app, ["--help"])
    version_result = runner.invoke(app, ["--version"])

    assert help_result.exit_code == 0
    assert version_result.exit_code == 0
    assert __version__ in version_result.output


def test_models_does_not_construct_database(monkeypatch) -> None:
    from gpt4free_tui_cli import bootstrap
    from gpt4free_tui_cli.presentation import cli

    fake_engine = Mock()
    fake_engine.get_all_models.return_value = ["offline-model"]
    monkeypatch.setattr(cli, "create_engine", lambda: fake_engine)
    monkeypatch.setattr(
        bootstrap,
        "DatabaseManager",
        Mock(side_effect=AssertionError("models must not need a database")),
    )

    result = CliRunner().invoke(app, ["models"])

    assert result.exit_code == 0
    assert "offline-model" in result.output
