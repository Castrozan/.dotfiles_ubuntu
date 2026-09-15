{ pkgs }:
let
  version = "1.7.0.4638";
  distributions = {
    aarch64-darwin = {
      platform = "macos/macos-arm64";
      hash = "sha256-ikYRsomdr+7yvmwtggs9LABKAqzQEr97Dx/QjKkZNlk=";
    };
    x86_64-linux = {
      platform = "linux/linux-x86-64";
      hash = "sha256-QrndYxEguHds1j2q/Rjbji0SKf3N4qPObvJYWA62Oow=";
    };
    aarch64-linux = {
      platform = "linux/linux-arm64";
      hash = "sha256-9Kacx/nBMSVnVy9nTkNDCU5jJeHBQtBdPkkUgtiXkyk=";
    };
  };
  distribution = distributions.${pkgs.stdenv.hostPlatform.system};
  platform = pkgs.lib.splitString "/" distribution.platform;
  executable = pkgs.stdenvNoCC.mkDerivation {
    pname = "sonarqube-cli";
    inherit version;
    src = pkgs.fetchurl {
      url = "https://binaries.sonarsource.com/Distribution/sonarqube-cli/${version}/${builtins.head platform}/sonarqube-cli-${version}-${builtins.elemAt platform 1}.bin";
      inherit (distribution) hash;
    };
    dontUnpack = true;
    nativeBuildInputs = pkgs.lib.optionals pkgs.stdenv.isLinux [ pkgs.autoPatchelfHook ];
    buildInputs = pkgs.lib.optionals pkgs.stdenv.isLinux [ pkgs.stdenv.cc.cc.lib ];
    installPhase = ''
      install -Dm755 "$src" "$out/bin/sonar"
    '';
  };
in
pkgs.writeShellApplication {
  name = "sonar";
  runtimeInputs = [ pkgs.coreutils ];
  text = ''
    export SONARQUBE_CLI_SERVER="''${SONARQUBE_CLI_SERVER:-https://sonarcloud.io}"
    export SONARQUBE_CLI_ORG="''${SONARQUBE_CLI_ORG:-castrozan-oss}"
    if [[ -z "''${SONARQUBE_CLI_TOKEN:-}" ]]; then
      SONARQUBE_CLI_TOKEN="$(cat "$HOME/.secrets/sonarqube-token")"
      export SONARQUBE_CLI_TOKEN
    fi
    exec ${executable}/bin/sonar "$@"
  '';
}
