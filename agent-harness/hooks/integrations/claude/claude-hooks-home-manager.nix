{
  pkgs,
  lib,
  inputs,
  ...
}:
let
  agentHookScripts = import ../../flat-hook-scripts-directory.nix {
    inherit pkgs lib;
  };
  herdrClaudeHook = pkgs.writeTextFile {
    name = "herdr-claude-hook";
    destination = "/herdr-agent-state.sh";
    executable = true;
    text = builtins.readFile (inputs.herdr + "/src/integration/assets/claude/herdr-agent-state.sh");
  };
in
{
  home.file.".claude/hooks".source = pkgs.symlinkJoin {
    name = "claude-hook-scripts";
    paths = [
      agentHookScripts
      herdrClaudeHook
    ];
  };
}
