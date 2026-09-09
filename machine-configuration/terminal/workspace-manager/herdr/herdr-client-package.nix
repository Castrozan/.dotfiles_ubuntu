{
  pkgs,
  herdrPackage,
}:
let
  selector = pkgs.writeShellApplication {
    name = "select-herdr-client";
    runtimeInputs = [
      pkgs.lsof
      pkgs.nix
      pkgs.python3
    ];
    text = ''
      exec python3 ${./scripts/select-herdr-client.py} "$@"
    '';
  };
  package = pkgs.writeShellApplication {
    name = "herdr";
    runtimeInputs = [ selector ];
    text = ''
      selected_executable="$(select-herdr-client select ${herdrPackage}/bin/herdr "$@")"
      exec "$selected_executable" "$@"
    '';
  };
in
{
  inherit package selector;
}
