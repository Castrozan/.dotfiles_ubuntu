import importlib
import json
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest


@pytest.fixture
def sonar_api(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]))
    return importlib.import_module("sonar_api")


def test_query_values_cannot_become_flags_or_shell_commands(sonar_api, monkeypatch):
    captured = []

    def run(command, **options):
        captured.append(command)
        assert options == {
            "check": True,
            "capture_output": True,
            "text": True,
            "timeout": 60,
        }
        return subprocess.CompletedProcess(command, 0, '{"projects": []}')

    monkeypatch.setattr(sonar_api.subprocess, "run", run)
    value = "project with spaces;&parameter=value"
    assert sonar_api.request("get", "/api/projects/search", project=value) == {
        "projects": []
    }
    assert captured[0][:3] == ["sonar", "api", "get"]
    assert parse_qs(urlsplit(captured[0][3]).query) == {"project": [value]}


def test_posts_structured_data_and_accepts_empty_responses(sonar_api, monkeypatch):
    def run(command, **options):
        assert command[:4] == ["sonar", "api", "post", "/api/settings/set"]
        assert json.loads(command[5]) == {"key": "setting", "value": "first\nsecond"}
        return subprocess.CompletedProcess(command, 0, "\n")

    monkeypatch.setattr(sonar_api.subprocess, "run", run)
    assert (
        sonar_api.request(
            "post", "/api/settings/set", key="setting", value="first\nsecond"
        )
        == {}
    )


def test_api_failure_stops_configuration(sonar_api, monkeypatch):
    def run(command, **options):
        raise subprocess.CalledProcessError(1, command, stderr="Permission denied")

    monkeypatch.setattr(sonar_api.subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError, match="non-zero"):
        sonar_api.request("post", "/api/settings/set", key="setting", value="value")
