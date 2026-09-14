{
  pkgs,
  lib,
  inputs,
  ...
}:
let
  speedReaderPackage = inputs.herdr-speed-read.packages.${pkgs.stdenv.hostPlatform.system}.default;
  herdrPackage = inputs.herdr.packages.${pkgs.stdenv.hostPlatform.system}.default;
in
{
  home.packages = [ speedReaderPackage ];
  home.activation.linkHerdrSpeedReader = lib.hm.dag.entryAfter [ "linkGeneration" ] ''
    run ${herdrPackage}/bin/herdr plugin link ${speedReaderPackage}/share/herdr-plugin --enabled
  '';
}
