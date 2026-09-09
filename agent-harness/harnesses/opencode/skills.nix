{
  pkgs,
  config,
  hostname,
  lib,
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

  opencodeInteractiveSkillNames = interactiveAgentSkills.effectiveInteractiveSkillNames { };

  opencodeSkillsPath = "${config.home.homeDirectory}/.config/opencode/skills";

  globalOpencodeSkills = builtins.listToAttrs (
    map (dirname: {
      name = ".config/opencode/skills/${dirname}";
      value = {
        source =
          interactiveAgentSkills.deployedSkillDirectory ".config/opencode/skills"
            opencodeInteractiveSkillNames
            dirname;
        recursive = true;
      };
    }) opencodeInteractiveSkillNames
  );

  coreAgentRules = builtins.readFile ../../../agent-harness/agent-instructions/core-rules/core.md;

  coreSkillFromAgentInstructions = {
    ".config/opencode/skills/core/SKILL.md".source = projection.instructionText {
      name = "opencode-core-SKILL.md";
      deployed = "/.config/opencode/skills/core/SKILL.md";
      destinations = { };
      text = ''
        ---
        name: core
        description: Display core agent behavior instructions. Use when user wants to see, review, or reference the core rules, or when injecting core instructions as context into subagents, oneshot sessions, or external tools.
        ---

        ${coreAgentRules}
      '';
    };
  };

  allSkillsIndexSkill = interactiveAgentSkills.renderAllSkillsIndexSkill opencodeInteractiveSkillNames;

  allSkillsIndexSkillFile = {
    ".config/opencode/skills/all-skills/SKILL.md".source = projection.instructionText {
      name = "opencode-all-skills-SKILL.md";
      deployed = "/.config/opencode/skills/all-skills/SKILL.md";
      destinations = interactiveAgentSkills.deploymentDestinations ".config/opencode/skills" opencodeInteractiveSkillNames;
      text = ''
        ---
        name: all-skills
        description: ${builtins.toJSON allSkillsIndexSkill.description}
        ---

        ${allSkillsIndexSkill.body}
      '';
    };
  };
in
{
  home.file = globalOpencodeSkills // coreSkillFromAgentInstructions // allSkillsIndexSkillFile;

  home.activation.removeExternalSymlinksCollidingWithOpencodeSkills =
    lib.hm.dag.entryBefore
      [
        "checkLinkTargets"
      ]
      ''
        if [ -d "${opencodeSkillsPath}" ]; then
          for skillName in ${builtins.concatStringsSep " " opencodeInteractiveSkillNames}; do
            skillPath="${opencodeSkillsPath}/$skillName"
            if [ -L "$skillPath" ]; then
              linkTarget=$(readlink "$skillPath")
              if [ "''${linkTarget#${config.home.homeDirectory}/.nix-profile}" = "$linkTarget" ] && \
                 [ "''${linkTarget#/nix/store}" = "$linkTarget" ]; then
                rm "$skillPath"
              fi
            fi
          done
        fi
      '';
}
