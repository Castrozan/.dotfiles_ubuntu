from sonar_api import request


def configure_quality_gate(configuration):
    organization = configuration["organization"]
    desired_gate = configuration["qualityGate"]
    gates = request("get", "/api/qualitygates/list", organization=organization)[
        "qualitygates"
    ]
    gate = next((gate for gate in gates if gate["name"] == desired_gate["name"]), None)
    if gate is None:
        gate = request(
            "post",
            "/api/qualitygates/create",
            organization=organization,
            name=desired_gate["name"],
        )
    actual_gate = request(
        "get", "/api/qualitygates/show", organization=organization, id=gate["id"]
    )
    actual_conditions = {
        condition["metric"]: condition for condition in actual_gate["conditions"]
    }
    desired_conditions = {
        condition["metric"]: condition for condition in desired_gate["conditions"]
    }
    for metric, condition in desired_conditions.items():
        actual = actual_conditions.get(metric)
        if actual is None:
            request(
                "post",
                "/api/qualitygates/create_condition",
                organization=organization,
                gateId=gate["id"],
                **condition,
            )
        elif any(str(actual[key]) != value for key, value in condition.items()):
            request(
                "post",
                "/api/qualitygates/update_condition",
                organization=organization,
                id=actual["id"],
                **condition,
            )
    for metric, condition in actual_conditions.items():
        if metric not in desired_conditions:
            request(
                "post",
                "/api/qualitygates/delete_condition",
                organization=organization,
                id=condition["id"],
            )
    association = request(
        "get",
        "/api/qualitygates/get_by_project",
        organization=organization,
        project=configuration["project"],
    )
    if str(association["qualityGate"]["id"]) != str(gate["id"]):
        request(
            "post",
            "/api/qualitygates/select",
            organization=organization,
            gateId=gate["id"],
            projectKey=configuration["project"],
        )
