from seed_codex_config_test_support import read_live_config, run_seed


def test_rebuild_preserves_hook_approvals_and_disabled_state_without_restoring_hooks(
    tmp_path,
):
    codex_directory = tmp_path / ".codex"
    codex_directory.mkdir()
    (codex_directory / "config.toml.nix-source").write_text(
        'approval_policy = "never"\n'
    )
    (codex_directory / "config.toml").write_text(
        '[hooks.state."/user/hooks.json:session_start:0:0"]\n'
        'trusted_hash = "sha256:approved"\n'
        "enabled = false\n"
        "[[hooks.SessionStart]]\n"
        'hooks = [{ type = "command", command = "stale-hook" }]\n'
    )

    for _ in range(2):
        result = run_seed(tmp_path)
        assert result.returncode == 0, result.stderr
        assert read_live_config(tmp_path)["hooks"] == {
            "state": {
                "/user/hooks.json:session_start:0:0": {
                    "trusted_hash": "sha256:approved",
                    "enabled": False,
                }
            }
        }


def test_declarative_hook_state_and_definitions_win_collisions(tmp_path):
    codex_directory = tmp_path / ".codex"
    codex_directory.mkdir()
    (codex_directory / "config.toml.nix-source").write_text(
        "[hooks.state.declared]\n"
        "enabled = false\n"
        "[[hooks.SessionStart]]\n"
        'hooks = [{ type = "command", command = "declared-hook" }]\n'
    )
    (codex_directory / "config.toml").write_text(
        "[hooks.state.declared]\n"
        "enabled = true\n"
        "[hooks.state.runtime]\n"
        'trusted_hash = "sha256:approved"\n'
    )

    result = run_seed(tmp_path)

    assert result.returncode == 0, result.stderr
    hooks = read_live_config(tmp_path)["hooks"]
    assert hooks["state"] == {
        "declared": {"enabled": False},
        "runtime": {"trusted_hash": "sha256:approved"},
    }
    assert hooks["SessionStart"][0]["hooks"][0]["command"] == "declared-hook"
