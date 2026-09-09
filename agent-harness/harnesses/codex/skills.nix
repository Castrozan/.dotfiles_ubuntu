{
  config,
  hostname,
  lib,
  pkgs,
  ...
}:
let
  projection = import ../../agent-instructions/instruction-projection.nix { inherit pkgs; };
  interactiveAgentSkills =
    import
      ../../../agent-harness/agent-instructions/interactive-skill-catalog/interactive-agent-skills.nix
      {
        inherit hostname;
        inherit pkgs;
      };

  codexInteractiveSkillNames = interactiveAgentSkills.effectiveInteractiveSkillNames { };

  codexSkillsPath = "${config.home.homeDirectory}/.codex/skills";

  coreAgentRules = builtins.readFile ../../../agent-harness/agent-instructions/core-rules/core.md;

  codexSkillLinks = interactiveAgentSkills.skillDirectorySymlinksAtPrefix ".codex/skills" codexInteractiveSkillNames;

  coreSkillFile = projection.instructionText {
    name = "codex-core-SKILL.md";
    deployed = "/.codex/skills/core/SKILL.md";
    destinations = { };
    text = ''
      ---
      name: core
      description: Display core agent behavior instructions. Use when user wants to see, review, or reference the core rules, or when injecting core instructions as context into subagents, oneshot sessions, or external tools.
      ---

      ${coreAgentRules}
    '';
  };
  coreSkillDirectory = pkgs.linkFarm "codex-core-skill" [
    {
      name = "SKILL.md";
      path = coreSkillFile;
    }
  ];

  coreSkillFromAgentInstructions = {
    ".codex/skills/core".source = coreSkillDirectory;
  };

  allSkillsIndexSkill = interactiveAgentSkills.renderAllSkillsIndexSkill codexInteractiveSkillNames;

  allSkillsIndexSkillFileContent = projection.instructionText {
    name = "codex-all-skills-SKILL.md";
    deployed = "/.codex/skills/all-skills/SKILL.md";
    destinations = interactiveAgentSkills.deploymentDestinations ".codex/skills" codexInteractiveSkillNames;
    text = ''
      ---
      name: all-skills
      description: ${builtins.toJSON allSkillsIndexSkill.description}
      ---

      ${allSkillsIndexSkill.body}
    '';
  };
  allSkillsIndexSkillDirectory = pkgs.linkFarm "codex-all-skills-skill" [
    {
      name = "SKILL.md";
      path = allSkillsIndexSkillFileContent;
    }
  ];

  allSkillsIndexSkillFile = {
    ".codex/skills/all-skills".source = allSkillsIndexSkillDirectory;
  };

in
{
  home.file = codexSkillLinks // coreSkillFromAgentInstructions // allSkillsIndexSkillFile;

  home.activation.removeLegacyCodexSkillDirectories = lib.hm.dag.entryBefore [ "checkLinkTargets" ] ''
    CODEX_SKILLS_PATH="${codexSkillsPath}" \
    COREUTILS_BIN="${pkgs.coreutils}/bin" \
    GREP_BIN="${pkgs.gnugrep}/bin/grep" \
    ${pkgs.bash}/bin/bash ${./scripts/replace-legacy-codex-skill-directories}
  '';
}
