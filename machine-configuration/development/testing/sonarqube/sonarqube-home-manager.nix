{ pkgs, ... }:
let
  tools = import ./sonarqube-tools.nix { inherit pkgs; };
in
{
  home.packages = [
    tools.cli
    tools.configure
    tools.mcp
    tools.scanner
  ];
  codex.mcpServers.sonarqube = {
    command = "${tools.mcp}/bin/sonarqube-mcp";
    startupTimeoutSeconds = 60;
  };
}
