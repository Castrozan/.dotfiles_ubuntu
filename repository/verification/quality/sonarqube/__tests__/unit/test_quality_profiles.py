import importlib
from pathlib import Path

import pytest


@pytest.fixture
def quality_profiles(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]))
    return importlib.import_module("quality_profiles")


@pytest.mark.parametrize("existing", [True, False])
def test_inherits_built_in_rules_and_applies_owned_overrides(
    quality_profiles, monkeypatch, existing
):
    writes = []

    def request(method, endpoint, **parameters):
        if endpoint == "/api/qualityprofiles/search":
            profiles = [{"key": "parent", "name": "Sonar way"}]
            if existing:
                profiles.append(
                    {"key": "owned", "name": "Dotfiles", "parentKey": "parent"}
                )
            return {"profiles": profiles}
        if endpoint == "/api/rules/search":
            assert parameters["inheritance"] == "NONE,OVERRIDES"
            return {
                "rules": [{"key": "python:S104"}, {"key": "python:stale"}],
                "total": 2,
            }
        writes.append((endpoint, parameters))
        if endpoint == "/api/qualityprofiles/create":
            return {"profile": {"key": "owned", "name": "Dotfiles"}}
        if endpoint == "/api/qualityprofiles/add_project":
            assert "organization" not in parameters
        return {}

    monkeypatch.setattr(quality_profiles, "request", request)
    quality_profiles.configure_quality_profiles(
        {
            "organization": "organization",
            "project": "project",
            "qualityProfiles": [
                {
                    "name": "Dotfiles",
                    "language": "py",
                    "parent": "Sonar way",
                    "rules": [{"key": "python:S104", "parameters": {"maximum": "200"}}],
                }
            ],
        }
    )
    assert (
        "/api/qualityprofiles/deactivate_rule",
        {"key": "owned", "rule": "python:stale"},
    ) in writes
    assert (
        "/api/qualityprofiles/activate_rule",
        {
            "key": "owned",
            "rule": "python:S104",
            "params": "maximum=200",
        },
    ) in writes
    assert all(parameters.get("key") != "parent" for _, parameters in writes)
    assert any(endpoint.endswith("/create") for endpoint, _ in writes) is not existing


def test_collects_every_page_before_removing_rules(quality_profiles, monkeypatch):
    events = []

    def request(method, endpoint, **parameters):
        events.append((method, parameters))
        if method == "get":
            return {"rules": [{"key": f"rule{parameters['p']}"}], "total": 501}
        return {}

    monkeypatch.setattr(quality_profiles, "request", request)
    quality_profiles.remove_undeclared_rules({"key": "owned"}, [])
    assert [method for method, _ in events] == ["get", "get", "post", "post"]
    assert [
        parameters["rule"] for method, parameters in events if method == "post"
    ] == ["rule1", "rule2"]
