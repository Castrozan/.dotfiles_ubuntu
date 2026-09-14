{ pkgs, ... }:
{
  home.packages = [
    (pkgs.writeShellScriptBin "on" (builtins.readFile ./obsidian/scripts/open-new-note))
    (pkgs.writeShellScriptBin "pdf-edit" (
      builtins.readFile ./pdf-editing/scripts/start-bentopdf-pdf-editor
    ))
  ];
}
