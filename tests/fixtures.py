""" Test fixtures """
import pytest

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

@pytest.fixture
def mock_env_access_key(monkeypatch):
    """ mock environment access key """
    monkeypatch.setenv("ACCESS_KEY", CLIENT_HEADERS["ACCESS_KEY"])
    monkeypatch.setenv("BAN_API_AUTH_API_KEY", "12345ABCDEF")
    monkeypatch.setenv("BAN_API_APP_TOKEN", "secret_token")
    monkeypatch.setenv("BAN_API_URL", "https://api.url.com/ban")

@pytest.fixture
def mock_env_no_access_key(monkeypatch):
    """ mock environment with no access key """
    monkeypatch.delenv("ACCESS_KEY", raising=False)
