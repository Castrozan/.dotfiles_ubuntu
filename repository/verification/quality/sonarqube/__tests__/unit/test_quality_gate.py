import importlib
from pathlib import Path

import pytest


@pytest.fixture
def quality_gate(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]))
    return importlib.import_module("quality_gate")


def test_reconciles_changed_missing_and_removed_conditions(quality_gate, monkeypatch):
    desired = {
        "organization": "owned-organization",
        "project": "owned-project",
        "qualityGate": {
            "name": "Owned gate",
            "conditions": [
                {"metric": "new_coverage", "op": "LT", "error": "80"},
                {"metric": "new_violations", "op": "GT", "error": "0"},
            ],
        },
    }
    writes = []

    def request(method, endpoint, **parameters):
        assert parameters["organization"] == "owned-organization"
        if endpoint.endswith("/get_by_project"):
            return {"qualityGate": {"id": 9}}
        if endpoint.endswith("/list"):
            return {"qualitygates": [{"id": 17, "name": "Owned gate"}]}
        if endpoint.endswith("/show"):
            return {
                "conditions": [
                    {"id": 2, "metric": "new_coverage", "op": "LT", "error": "20"},
                    {"id": 3, "metric": "coverage", "op": "LT", "error": "80"},
                ]
            }
        assert method == "post"
        writes.append((endpoint.rsplit("/", 1)[1], parameters))
        return {}

    monkeypatch.setattr(quality_gate, "request", request)
    quality_gate.configure_quality_gate(desired)
    assert writes == [
        (
            "update_condition",
            {
                "organization": "owned-organization",
                "id": 2,
                "metric": "new_coverage",
                "op": "LT",
                "error": "80",
            },
        ),
        (
            "create_condition",
            {
                "organization": "owned-organization",
                "gateId": 17,
                "metric": "new_violations",
                "op": "GT",
                "error": "0",
            },
        ),
        ("delete_condition", {"organization": "owned-organization", "id": 3}),
        (
            "select",
            {
                "organization": "owned-organization",
                "gateId": 17,
                "projectKey": "owned-project",
            },
        ),
    ]


def test_does_not_rewrite_matching_conditions(quality_gate, monkeypatch):
    condition = {"metric": "new_violations", "op": "GT", "error": "0"}
    writes = []

    def request(method, endpoint, **parameters):
        if endpoint.endswith("/get_by_project"):
            return {"qualityGate": {"id": 17}}
        if endpoint.endswith("/list"):
            return {"qualitygates": [{"id": 17, "name": "Owned gate"}]}
        if endpoint.endswith("/show"):
            return {"conditions": [{"id": 2, **condition}]}
        writes.append(endpoint)
        return {}

    monkeypatch.setattr(quality_gate, "request", request)
    quality_gate.configure_quality_gate(
        {
            "organization": "owned",
            "project": "project",
            "qualityGate": {"name": "Owned gate", "conditions": [condition]},
        }
    )
    assert writes == []


def test_creates_only_the_named_gate(quality_gate, monkeypatch):
    writes = []

    def request(method, endpoint, **parameters):
        if endpoint.endswith("/get_by_project"):
            return {"qualityGate": {"id": 9}}
        if endpoint.endswith("/list"):
            return {"qualitygates": [{"id": 9, "name": "Sonar way"}]}
        if endpoint.endswith("/show"):
            assert parameters["id"] == 17
            return {"conditions": []}
        writes.append((endpoint, parameters))
        return {"id": 17}

    monkeypatch.setattr(quality_gate, "request", request)
    quality_gate.configure_quality_gate(
        {
            "organization": "owned",
            "project": "project",
            "qualityGate": {"name": "Owned gate", "conditions": []},
        }
    )
    assert writes[0] == (
        "/api/qualitygates/create",
        {"organization": "owned", "name": "Owned gate"},
    )
    assert all(parameters.get("gateId") != 9 for _, parameters in writes)
