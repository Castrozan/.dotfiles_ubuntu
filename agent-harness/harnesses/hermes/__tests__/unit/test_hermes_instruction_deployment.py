import os
import subprocess
import sys
from pathlib import Path

import yaml


HERMES_DIRECTORY = Path(__file__).resolve().parents[2]


def test_configuration_keeps_prompt_literals_and_existing_settings(tmp_path):
    template = tmp_path / "template.yaml"
    template.write_text("agent:\n  reasoning_effort: xhigh\nhooks_auto_accept: true\n")
    instructions = tmp_path / "instructions.md"
    text = "### Response shape\n\nUse `**Done:**` and [evidence](SOUL.md#evidence).\n"
    instructions.write_text(text)
    output = tmp_path / "config.yaml"
    subprocess.run(
        [
            sys.executable,
            str(HERMES_DIRECTORY / "scripts/render-hermes-configuration.py"),
            str(template),
            str(instructions),
            str(output),
        ],
        check=True,
    )
    assert yaml.safe_load(output.read_text()) == {
        "agent": {"reasoning_effort": "xhigh", "system_prompt": text},
        "hooks_auto_accept": True,
    }


def test_fresh_launch_and_relaunch_install_the_routed_humanize_reference(tmp_path):
    home = tmp_path / "custom-hermes-home"
    binary = home / ".venv/bin/hermes"
    binary.parent.mkdir(parents=True)
    binary.write_text("#!/usr/bin/env bash\nexit 0\n")
    binary.chmod(0o755)
    (home / ".venv/.hermes-installed-version-test").touch()
    skill = tmp_path / "source-humanize"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "### Scope\n\nRead [reference](references/interactive-communication.md).\n"
    )
    reference = skill / "references/interactive-communication.md"
    reference.write_text("### Response shape\n\nPreserve the reply contract.\n")
    source = tmp_path / "source.md"
    source.write_text("### Evidence\n\nRead.\n")
    memory = tmp_path / "memory.md"
    memory.write_text("Identity: Test user.\n")
    prefixes = tmp_path / "prefixes.txt"
    prefixes.write_text("")
    environment = {
        **os.environ,
        "HERMES_HOME": str(home),
        "HERMES_AGENT_VERSION": "test",
        "HERMES_AGENT_RUNTIME_PATH": os.environ["PATH"],
        "HERMES_AGENT_CONFIG_TEMPLATE": str(source),
        "HERMES_AGENT_SOUL": str(source),
        "HERMES_AGENT_HUMANIZE_SKILL": str(skill / "SKILL.md"),
        "HERMES_AGENT_DOCS_SKILL": str(source),
        "HERMES_AGENT_USER_MEMORY": str(memory),
        "HERMES_AGENT_AGENT_MEMORY": str(memory),
        "HERMES_AGENT_RETIRED_USER_MEMORY_ENTRY_PREFIXES": str(prefixes),
        "HERMES_AGENT_RETIRED_AGENT_MEMORY_ENTRY_PREFIXES": str(prefixes),
        "HERMES_AGENT_MEMORY_SYNCHRONIZER_PYTHON": sys.executable,
        "HERMES_AGENT_MEMORY_SYNCHRONIZER": str(
            HERMES_DIRECTORY / "scripts/synchronize-hermes-memory.py"
        ),
    }
    environment.pop("HERMES_AGENT_LAUNCH_SEEDED", None)
    installed = home / "skills/humanize/references/interactive-communication.md"
    for content in (reference.read_text(), "### Response shape\n\nUpdated contract.\n"):
        reference.write_text(content)
        subprocess.run(
            ["bash", str(HERMES_DIRECTORY / "scripts/hermes-launch")],
            env=environment,
            check=True,
        )
        assert installed.read_text() == content
        assert (home / "skills/humanize/SKILL.md").read_text() == (
            skill / "SKILL.md"
        ).read_text()
