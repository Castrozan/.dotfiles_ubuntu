{ pkgs, hostname, ... }:
let
  interactiveAgentSkills = import ../interactive-skill-catalog/interactive-agent-skills.nix {
    inherit hostname;
    inherit pkgs;
  };

  harnessProjectSkillDirectories = [
    {
      pathInRepository = ".claude/skills";
      deploysEachSkillFileSeparately = false;
    }
    {
      pathInRepository = ".opencode/skills";
      deploysEachSkillFileSeparately = true;
    }
  ];

  repositorySkillSymlinksIn =
    {
      pathInRepository,
      deploysEachSkillFileSeparately,
    }:
    builtins.listToAttrs (
      map (skillName: {
        name = ".dotfiles/${pathInRepository}/${skillName}";
        value = {
          source =
            interactiveAgentSkills.deployedSkillDirectory ".dotfiles/${pathInRepository}"
              interactiveAgentSkills.dotfilesRepoSkillNames
              skillName;
          recursive = deploysEachSkillFileSeparately;
        };
      }) interactiveAgentSkills.dotfilesRepoSkillNames
    );
in
{
  home.file = builtins.foldl' (
    accumulated: harnessProjectSkillDirectory:
    accumulated // repositorySkillSymlinksIn harnessProjectSkillDirectory
  ) { } harnessProjectSkillDirectories;
}
