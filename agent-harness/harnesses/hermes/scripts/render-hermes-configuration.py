import argparse
from pathlib import Path

import yaml


def render_configuration(template: Path, instructions: Path, output: Path) -> None:
    configuration = yaml.safe_load(template.read_text())
    configuration["agent"]["system_prompt"] = instructions.read_text()
    output.write_text(
        yaml.safe_dump(configuration, allow_unicode=True, sort_keys=False)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("template", type=Path)
    parser.add_argument("instructions", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    render_configuration(arguments.template, arguments.instructions, arguments.output)


if __name__ == "__main__":
    main()
