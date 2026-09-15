import subprocess

import pytest

from directory_entry_guard_handler import handle
from hook_dispatch import EVERY_SURFACE, HookHandler, run_handlers


@pytest.fixture
def repository(tmp_path):
    repository_root = tmp_path / "repository"
    repository_root.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repository_root)], check=True)
    source = repository_root / "source"
    source.mkdir()
    for index in range(16):
        (source / f"file{index}.py").touch()
    return repository_root


@pytest.mark.parametrize("surface", EVERY_SURFACE)
def test_all_harness_surfaces_block_sixteenth_entry(repository, surface):
    result = run_handlers(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": str(repository / "source/file15.py")},
        },
        [HookHandler(handle=handle, tool_matcher="Edit|Write")],
        surface,
    )
    assert result.decision == "block"
    assert "source has 16 immediate files/folders combined (limit 15)" in result.reason


def test_patch_nested_creation_checks_ancestors(repository):
    result = handle(
        {
            "tool_name": "apply_patch",
            "cwd": str(repository),
            "tool_input": "*** Add File: source/file15.py\n+pass\n",
        }
    )
    assert result.decision == "block"


def test_symlinked_repository_path_cannot_bypass_limit(repository, tmp_path):
    alias = tmp_path / "alias"
    alias.symlink_to(repository, target_is_directory=True)
    result = handle(
        {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(alias / "source/file15.py")},
        }
    )
    assert result.decision == "block"


def test_unrelated_directory_violation_does_not_block_edit(repository):
    target = repository / "other.py"
    target.touch()
    assert (
        handle({"tool_name": "Edit", "tool_input": {"file_path": str(target)}}) is None
    )


def test_deletion_to_fifteen_unblocks_directory(repository):
    target = repository / "source/file15.py"
    target.unlink()
    assert (
        handle({"tool_name": "Edit", "tool_input": {"file_path": str(target)}}) is None
    )


def test_read_does_not_enumerate_repository(repository, monkeypatch):
    def fail_if_called(*arguments):
        raise AssertionError("Read must not scan the repository")

    monkeypatch.setattr(
        "directory_entry_guard_handler.repository_root_for_path", fail_if_called
    )
    assert (
        handle(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": str(repository / "source/file15.py")},
            }
        )
        is None
    )


def test_git_timeout_blocks_with_actionable_failure(repository, monkeypatch):
    def time_out(*arguments):
        raise subprocess.TimeoutExpired("git", 5)

    monkeypatch.setattr(
        "directory_entry_guard_handler.repository_entry_counts", time_out
    )
    result = handle(
        {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(repository / "source/file15.py")},
        }
    )
    assert result.decision == "block"
    assert "could not complete" in result.reason
