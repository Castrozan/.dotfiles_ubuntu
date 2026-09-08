from pathlib import Path
import shlex

import skill_loaded_marker

AUTHORING_SKILL_NAMES = ("instructions", "docs")
MAXIMUM_SKILL_BYTES = 65536
MAXIMUM_COMMAND_CHARACTERS = 16384
MAXIMUM_READ_PATHS = 16


def standalone_cat_paths(tool_input, working_directory):
    command = tool_input.get("command")
    if not isinstance(command, str) or len(command) > MAXIMUM_COMMAND_CHARACTERS:
        return set()
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        tokens = list(lexer)
    except ValueError:
        return set()
    if not tokens or Path(tokens[0]).name != "cat":
        return set()
    arguments = tokens[1:]
    if arguments[:1] == ["--"]:
        arguments = arguments[1:]
    if not arguments or len(arguments) > MAXIMUM_READ_PATHS:
        return set()
    if any(
        argument.startswith("-")
        or any(character in argument for character in "|&;()<>`$")
        for argument in arguments
    ):
        return set()
    return {
        (Path(working_directory) / Path(argument).expanduser()).resolve()
        for argument in arguments
    }


def handle(hook_input):
    session_id = hook_input.get("session_id")
    tool_input = hook_input.get("tool_input")
    response = hook_input.get("tool_response")
    if (
        not isinstance(session_id, str)
        or not session_id.strip()
        or not isinstance(tool_input, dict)
        or not isinstance(response, str)
    ):
        return None
    working_directory = tool_input.get("cwd") or hook_input.get("cwd")
    if (
        not isinstance(working_directory, str)
        or not Path(working_directory).is_absolute()
    ):
        return None
    read_paths = standalone_cat_paths(tool_input, working_directory)
    if not read_paths:
        return None
    for skill_name in AUTHORING_SKILL_NAMES:
        skill_path = Path.home() / ".codex" / "skills" / skill_name / "SKILL.md"
        if skill_path.resolve() not in read_paths:
            continue
        try:
            with skill_path.open("rb") as skill_file:
                content = skill_file.read(MAXIMUM_SKILL_BYTES + 1)
            if len(content) > MAXIMUM_SKILL_BYTES:
                continue
            skill_text = content.decode("utf-8").strip()
        except (OSError, UnicodeError):
            continue
        if skill_text and skill_text in response:
            skill_loaded_marker.record_skill_loaded(skill_name, session_id)
    return None
