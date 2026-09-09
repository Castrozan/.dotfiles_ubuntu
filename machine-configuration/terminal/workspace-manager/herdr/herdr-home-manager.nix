{
  pkgs,
  lib,
  inputs,
  ...
}:
let
  herdrPackage = inputs.herdr.packages.${pkgs.stdenv.hostPlatform.system}.default;
  herdrClientTools = import ./herdr-client-package.nix {
    inherit pkgs herdrPackage;
  };

  selectedTheme = import ../../../desktop/theming/selected-theme.nix;

  renderedHerdrConfig = pkgs.writeText "herdr-config.toml" (
    lib.replaceStrings [ "@herdr_accent@" ] [ selectedTheme.accentHex ] (
      builtins.readFile ./program-configuration/config.toml
    )
  );
in
{
  imports = [
    ./herdr-config-mutable-home-manager.nix
    ./herdr-service-home-manager.nix
  ];

  home = {
    packages = [ herdrClientTools.package ];

    file.".config/herdr/config.toml.nix-source".source = renderedHerdrConfig;

    activation.reloadHerdrAfterConfigSeed =
      lib.hm.dag.entryAfter
        [
          "seedHerdrConfigAsMutableFile"
        ]
        ''
          ${herdrClientTools.package}/bin/herdr server reload-config >/dev/null 2>&1 || true
        '';

    activation.refreshHerdrCodexIntegration = lib.hm.dag.entryAfter [ "writeBoundary" ] ''
      run ${herdrPackage}/bin/herdr integration install codex
    '';

    activation.retainRunningHerdrPackage = lib.hm.dag.entryAfter [ "writeBoundary" ] ''
      run ${herdrClientTools.selector}/bin/select-herdr-client retain-running ${herdrPackage}/bin/herdr
    '';
  };
}
