import json
import subprocess
from pathlib import Path

from quality_gate import configure_quality_gate
from quality_profiles import configure_quality_profiles
from sonar_api import request


def configure_project(configuration):
    repositories = request(
        "get",
        "/api/alm_integration/list_repositories",
        organization=configuration["organization"],
    )["repositories"]
    repository = next(
        repository
        for repository in repositories
        if repository["slug"] == configuration["repository"]
    )
    if not repository["linkedProjects"]:
        result = request(
            "post",
            "/api/alm_integration/provision_projects",
            organization=configuration["organization"],
            installationKeys=repository["installationKey"],
            newCodeDefinitionType="days",
            newCodeDefinitionValue=str(configuration["newCodeDays"]),
        )
        if result.get("failures"):
            raise RuntimeError(json.dumps(result["failures"]))
    request(
        "post",
        "/api/project_branches/rename",
        project=configuration["project"],
        name=configuration["mainBranch"],
    )
    request(
        "post",
        "/api/autoscan/activation",
        projectKey=configuration["project"],
        enable="false",
    )
    for key, value in configuration["settings"].items():
        request(
            "post",
            "/api/settings/set",
            component=configuration["project"],
            key=key,
            value=value,
        )


def main():
    configuration = json.loads(Path(__file__).with_name("cloud.json").read_text())
    try:
        configure_project(configuration)
        configure_quality_gate(configuration)
        configure_quality_profiles(configuration)
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.stderr.strip()) from error
    print(json.dumps({"project": configuration["project"], "configured": True}))


if __name__ == "__main__":
    main()
