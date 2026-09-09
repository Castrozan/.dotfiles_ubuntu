{
  pkgs,
  inputs,
  ...
}:
let
  herdrPackage = inputs.herdr.packages.${pkgs.stdenv.hostPlatform.system}.default;
  agentSessionRestartPreflight = pkgs.writeShellApplication {
    name = "agent-session-restart-preflight";
    runtimeInputs = [ pkgs.python3 ];
    text = ''
      exec python3 ${./agent-session-restart-preflight.py}
    '';
  };
in
{
  home.packages = [
    (pkgs.writeShellApplication {
      name = "agent-session";
      runtimeInputs = [
        agentSessionRestartPreflight
        herdrPackage
      ];
      text = builtins.readFile ./agent-session;
    })
  ];
}
