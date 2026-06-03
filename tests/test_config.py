from pathlib import Path

from viola.config import load_settings


def test_load_settings_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("VIOLA_MODEL", "openai:test-model")
    monkeypatch.setenv("VIOLA_TEMPERATURE", "0.1")
    monkeypatch.setenv("VIOLA_DATA_DIR", "local-data")

    settings = load_settings(load_dotenv_file=False)

    assert settings.model == "openai:test-model"
    assert settings.temperature == 0.1
    assert settings.data_dir == Path("local-data")

