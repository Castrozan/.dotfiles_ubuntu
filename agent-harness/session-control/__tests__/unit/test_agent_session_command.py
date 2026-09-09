import json
import os
import subprocess
from pathlib import Path

import pytest

COMMAND = Path(__file__).resolve().parents[2] / "agent-session"
PREFLIGHT_COMMAND = (
    Path(__file__).resolve().parents[2] / "agent-session-restart-preflight.py"
)
CONTINUATION_PROMPT = "This session was restarted. Continue from where you left off."
SESSION_IDENTIFIER = "01a08137-f15e-7680-8ff1-5b4fe898b515"


def saved_rollout(codex_home, session_identifier=SESSION_IDENTIFIER):
    rollout_directory = codex_home / "sessions" / "2026" / "09" / "09"
    rollout_directory.mkdir(parents=True)
    rollout_path = (
        rollout_directory / f"rollout-2026-09-09T00-00-00-{session_identifier}.jsonl"
    )
    rollout_path.write_text(
        json.dumps(
            {
                "type": "session_meta",
                "payload": {"id": session_identifier},
            }
        )
        + "\n",
        encoding="utf-8",
    )


def agent_response(agent_name="codex", session_identifier=SESSION_IDENTIFIER):
    return json.dumps(
        {
            "result": {
                "agent": {
                    "agent": agent_name,
                    "agent_session": {
                        "agent": agent_name,
                        "kind": "id",
                        "source": f"herdr:{agent_name}",
                        "value": session_identifier,
                    },
                }
            }
        }
    )


def run_command(tmp_path, arguments, environment=None, persist_session=True):
    herdr = tmp_path / "herdr"
    herdr.write_text(
        "#!/bin/sh\n"
        'printf \'%s\\n\' "$*" >> "$HERDR_CALLS"\n'
        "if [ \"${1:-} ${2:-}\" = 'agent get' ]; then\n"
        "  printf '%s\\n' \"$HERDR_AGENT_RESPONSE\"\n"
        "  exit 0\n"
        "fi\n"
        "printf '%s\\n' \"$@\"\n",
        encoding="utf-8",
    )
    herdr.chmod(0o755)
    preflight = tmp_path / "agent-session-restart-preflight"
    preflight.write_text(
        f'#!/bin/sh\nexec python3 {PREFLIGHT_COMMAND} "$@"\n',
        encoding="utf-8",
    )
    preflight.chmod(0o755)
    codex_home = tmp_path / "codex-home"
    if persist_session:
        saved_rollout(codex_home)
    command_environment = os.environ.copy()
    command_environment.pop("CLAWDE_AGENT_NAME", None)
    command_environment.update(
        {
            "CODEX_HOME": str(codex_home),
            "CODEX_THREAD_ID": SESSION_IDENTIFIER,
            "HERDR_AGENT_RESPONSE": agent_response(),
            "HERDR_CALLS": str(tmp_path / "herdr-calls"),
            "HERDR_PANE_ID": "w1:p2",
            "PATH": f"{tmp_path}:{command_environment['PATH']}",
        }
    )
    command_environment.update(environment or {})
    return subprocess.run(
        ["bash", str(COMMAND), *arguments],
        capture_output=True,
        text=True,
        check=False,
        env=command_environment,
    )


def test_restart_delegates_self_lifecycle_to_herdr(tmp_path):
    result = run_command(tmp_path, ["restart"])

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "agent",
        "restart",
        "--prompt",
        CONTINUATION_PROMPT,
    ]
    assert (tmp_path / "herdr-calls").read_text(encoding="utf-8").splitlines() == [
        "agent get w1:p2",
        f"agent restart --prompt {CONTINUATION_PROMPT}",
    ]


def test_restart_refuses_an_unsaved_codex_session_before_calling_herdr(tmp_path):
    result = run_command(tmp_path, ["restart"], persist_session=False)

    assert result.returncode == 1
    assert "has no saved rollout" in result.stderr
    assert "left untouched" in result.stderr
    assert (tmp_path / "herdr-calls").read_text(encoding="utf-8").splitlines() == [
        "agent get w1:p2"
    ]


def test_restart_refuses_a_target_that_differs_from_the_running_codex_session(
    tmp_path,
):
    result = run_command(
        tmp_path,
        ["restart"],
        {"CODEX_THREAD_ID": "01a0840b-752f-7d60-b58d-7fe21ffa3761"},
    )

    assert result.returncode == 1
    assert "but the running Codex session is" in result.stderr
    assert (tmp_path / "herdr-calls").read_text(encoding="utf-8").splitlines() == [
        "agent get w1:p2"
    ]


def test_restart_preserves_non_codex_lifecycle_behavior(tmp_path):
    result = run_command(
        tmp_path,
        ["restart"],
        {"HERDR_AGENT_RESPONSE": agent_response("claude", "claude-session")},
    )

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "agent",
        "restart",
        "--prompt",
        CONTINUATION_PROMPT,
    ]


def test_exit_delegates_self_lifecycle_to_herdr(tmp_path):
    result = run_command(tmp_path, ["exit"])

    assert result.returncode == 0
    assert result.stdout.splitlines() == ["agent", "exit"]


def test_print_target_resolves_the_callers_herdr_pane(tmp_path):
    result = run_command(tmp_path, ["exit", "--print-target"])

    assert result.returncode == 0
    assert json.loads(result.stdout)["result"]["agent"]["agent"] == "codex"


@pytest.mark.parametrize("operation", ["restart", "exit"])
def test_clawde_owned_sessions_refuse_direct_lifecycle(tmp_path, operation):
    result = run_command(
        tmp_path,
        [operation],
        {"CLAWDE_AGENT_NAME": "steward"},
    )

    assert result.returncode == 1
    assert "Clawde-managed" in result.stderr
    assert result.stdout == ""


def test_lifecycle_requires_the_callers_herdr_pane(tmp_path):
    result = run_command(tmp_path, ["restart"], {"HERDR_PANE_ID": ""})

    assert result.returncode == 1
    assert "Herdr pane" in result.stderr
    assert result.stdout == ""
