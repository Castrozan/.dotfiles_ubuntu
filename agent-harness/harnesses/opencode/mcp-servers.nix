{
  pkgs,
  latest,
  homeDir,
}:
let
  browserMcp = import ../../../agent-harness/agent-instructions/skills/browser/install {
    inherit pkgs homeDir;
    nodejs = pkgs.nodejs_22;
    chromePackage = latest.google-chrome;
  };

  chromeDevtoolsStdioInvocation = [
    "${browserMcp.chromeDevtoolsMcpStdioCommand}"
  ]
  ++ browserMcp.chromeDevtoolsMcpStdioArgs;
in
{
  sonarqube = {
    type = "local";
    command = [
      "${
        (import ../../../machine-configuration/development/testing/sonarqube/sonarqube-tools.nix {
          inherit pkgs;
        }).mcp
      }/bin/sonarqube-mcp"
    ];
    enabled = true;
    timeout = 60000;
  };
  chrome-devtools = {
    type = "local";
    command = chromeDevtoolsStdioInvocation;
    enabled = true;
    timeout = 120000;
  };
}
