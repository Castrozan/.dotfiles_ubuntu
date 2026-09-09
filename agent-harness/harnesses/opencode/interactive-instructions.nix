{ pkgs, homeDirectory }:
let
  projection = import ../../agent-instructions/instruction-projection.nix { inherit pkgs; };
in
projection.instructionFile {
  name = "opencode-interactive-session-only-instructions.md";
  sources = [
    ../../../agent-harness/agent-instructions/skills/humanize/references/interactive-communication.md
    ../../../agent-harness/agent-instructions/core-rules/servant-identity.md
  ];
  destinations = projection.interactiveDestinations {
    coreInstructionFile = "${homeDirectory}/.config/opencode/AGENTS.md";
    humanizeSkillDirectory = "${homeDirectory}/.config/opencode/skills/humanize";
  };
}
