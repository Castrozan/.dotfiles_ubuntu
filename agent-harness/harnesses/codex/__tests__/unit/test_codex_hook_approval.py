import asyncio
from unittest.mock import AsyncMock

from approve import approve_discovered_hooks, session_directories
from launch_arguments import discover_launch_request
import pytest


@pytest.mark.parametrize("status", ["untrusted", "modified"])
def test_approves_native_hashes_without_changing_enablement(tmp_path, status):
    client = AsyncMock()
    hook = {
        "key": "native-key",
        "currentHash": "native-hash",
        "trustStatus": status,
        "enabled": False,
    }
    client.request.side_effect = [{"data": [{"hooks": [hook, hook]}]}, {}]

    asyncio.run(approve_discovered_hooks(client, [tmp_path]))

    assert client.request.await_args_list[1].args == (
        "config/batchWrite",
        {
            "edits": [
                {
                    "keyPath": "hooks.state",
                    "value": {"native-key": {"trusted_hash": "native-hash"}},
                    "mergeStrategy": "upsert",
                }
            ],
            "reloadUserConfig": True,
        },
    )


def test_already_trusted_and_managed_hooks_do_not_write_configuration(tmp_path):
    client = AsyncMock()
    client.request.return_value = {
        "data": [
            {"hooks": [{"trustStatus": status} for status in ("trusted", "managed")]}
        ]
    }

    asyncio.run(approve_discovered_hooks(client, [tmp_path]))

    client.request.assert_awaited_once_with("hooks/list", {"cwds": [str(tmp_path)]})


def test_resume_directories_are_paginated_and_deduplicated_without_rollout_scans(
    tmp_path,
):
    client = AsyncMock()
    client.request.side_effect = [
        {"data": [{"cwd": str(tmp_path)}], "nextCursor": "next-page"},
        {
            "data": [{"cwd": str(tmp_path)}, {"cwd": str(tmp_path / "deleted")}],
            "nextCursor": None,
        },
    ]

    assert asyncio.run(session_directories(client)) == {tmp_path}
    assert client.request.await_args_list[1].args[1]["cursor"] == "next-page"
    assert all(
        call.args[1]["useStateDbOnly"] for call in client.request.await_args_list
    )


@pytest.mark.parametrize(
    "arguments",
    [
        ["--help"],
        ["--version"],
        ["plugin", "list"],
        ["-c", "model='mcp'", "app-server"],
        ["--remote", "unix://"],
    ],
)
def test_configuration_and_remote_commands_skip_local_approval(arguments):
    assert discover_launch_request(arguments) is None


@pytest.mark.parametrize("command", ["resume", "fork", "agents"])
def test_session_launches_include_candidate_working_directories(command):
    assert discover_launch_request([command, "--last"]).include_session_directories


def test_explicit_directory_and_workspace_overrides_match_actual_launch(tmp_path):
    request = discover_launch_request(
        [
            "-c",
            'model_reasoning_effort="high"',
            "-C",
            str(tmp_path),
            "resume",
            "--last",
            "--enable",
            "hooks",
        ]
    )

    assert request.working_directory == tmp_path
    assert request.configuration_arguments == (
        "-c",
        'model_reasoning_effort="high"',
        "--enable",
        "hooks",
    )
    assert not request.include_session_directories


def test_prompt_words_and_option_values_do_not_turn_into_management_commands():
    assert discover_launch_request(["-m", "mcp", "explain mcp"]) is not None
    assert discover_launch_request(["exec", "help"]) is not None
