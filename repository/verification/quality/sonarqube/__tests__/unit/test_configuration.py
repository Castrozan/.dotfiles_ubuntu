import importlib
import json
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def configuration_module(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]))
    return importlib.import_module("configure")


@pytest.mark.parametrize("linked", [True, False])
def test_provisions_only_the_requested_repository(
    configuration_module, monkeypatch, linked
):
    writes = []

    def request(method, endpoint, **parameters):
        if method == "get":
            return {
                "repositories": [
                    {
                        "slug": "owner/other",
                        "installationKey": "other",
                        "linkedProjects": [],
                    },
                    {
                        "slug": "owner/repository",
                        "installationKey": "selected",
                        "linkedProjects": ["project"] if linked else [],
                    },
                ]
            }
        writes.append((endpoint, parameters))
        return {"projects": [{"projectKey": "project"}], "failures": []}

    monkeypatch.setattr(configuration_module, "request", request)
    configuration_module.configure_project(
        {
            "organization": "organization",
            "repository": "owner/repository",
            "project": "project",
            "mainBranch": "main",
            "newCodeDays": 30,
            "settings": {"sonar.leak.period": "30"},
        }
    )
    provisions = [
        parameters
        for endpoint, parameters in writes
        if endpoint.endswith("/provision_projects")
    ]
    assert len(provisions) == (0 if linked else 1)
    if provisions:
        assert provisions[0]["installationKeys"] == "selected"
    assert (
        "/api/autoscan/activation",
        {"projectKey": "project", "enable": "false"},
    ) in writes


def test_provision_failure_does_not_configure_another_project(
    configuration_module, monkeypatch
):
    def request(method, endpoint, **parameters):
        if method == "get":
            return {
                "repositories": [
                    {
                        "slug": "repository",
                        "installationKey": "selected",
                        "linkedProjects": [],
                    }
                ]
            }
        assert endpoint.endswith("/provision_projects")
        return {"failures": ["Repository unavailable"]}

    monkeypatch.setattr(configuration_module, "request", request)
    with pytest.raises(RuntimeError, match="Repository unavailable"):
        configuration_module.configure_project(
            {
                "organization": "organization",
                "repository": "repository",
                "project": "project",
                "mainBranch": "main",
                "newCodeDays": 30,
                "settings": {},
            }
        )


@pytest.mark.parametrize("failure", [True, False])
def test_main_applies_policy_and_surfaces_api_failures(
    configuration_module, monkeypatch, tmp_path, capsys, failure
):
    configuration = {"project": "project"}
    (tmp_path / "cloud.json").write_text(json.dumps(configuration))
    monkeypatch.setattr(
        configuration_module, "__file__", str(tmp_path / "configure.py")
    )
    events = []

    def configure_project(actual):
        assert actual == configuration
        events.append("project")
        if failure:
            raise subprocess.CalledProcessError(
                1, ["sonar"], stderr="Permission denied"
            )

    monkeypatch.setattr(configuration_module, "configure_project", configure_project)
    monkeypatch.setattr(
        configuration_module,
        "configure_quality_gate",
        lambda actual: events.append("gate"),
    )
    monkeypatch.setattr(
        configuration_module,
        "configure_quality_profiles",
        lambda actual: events.append("profiles"),
    )
    if failure:
        with pytest.raises(SystemExit, match="Permission denied"):
            configuration_module.main()
        assert events == ["project"]
        return
    configuration_module.main()
    assert events == ["project", "gate", "profiles"]
    assert json.loads(capsys.readouterr().out) == {
        "project": "project",
        "configured": True,
    }
