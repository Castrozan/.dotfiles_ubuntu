{ pkgs }:
let
  fetchPrebuiltBinary = import ../../../../repository/nix-library/fetch-prebuilt-binary.nix {
    inherit pkgs;
  };
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
  executable =
    (fetchPrebuiltBinary {
      pname = "sonarqube-cli";
      inherit version;
      url = "https://binaries.sonarsource.com/Distribution/sonarqube-cli/${version}/${builtins.head platform}/sonarqube-cli-${version}-${builtins.elemAt platform 1}.bin";
      sha256 = distribution.hash;
      binaryName = "sonar";
    }).overrideAttrs
      {
        doInstallCheck = true;
        installCheckPhase = ''
          "$out/bin/sonar" api --help > /dev/null
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
