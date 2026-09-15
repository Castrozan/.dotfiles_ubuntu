import json
import subprocess
from urllib.parse import urlencode


def request(method, endpoint, **parameters):
    command = ["sonar", "api", method, endpoint]
    if method == "get" and parameters:
        command[-1] += "?" + urlencode(parameters)
    elif parameters:
        command.extend(["--data", json.dumps(parameters)])
    response = subprocess.run(
        command, check=True, capture_output=True, text=True, timeout=60
    )
    return json.loads(response.stdout) if response.stdout.strip() else {}
