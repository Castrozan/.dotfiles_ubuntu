{ pkgs, hostname, ... }:
let
  interactiveAgentSkills = import ./interactive-agent-skills.nix {
    inherit hostname;
    inherit pkgs;
  };

  reachableSkillDirectorySymlinks = interactiveAgentSkills.skillDirectorySymlinksAtPrefix ".local/share/agent-skill-index" interactiveAgentSkills.reachableSkillNames;
in
{
  home.file = reachableSkillDirectorySymlinks;
}
