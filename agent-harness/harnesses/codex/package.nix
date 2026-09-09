{
  pkgs,
  lib,
  config,
  ...
}:
let
  fetchPrebuiltBinary = import ../../../repository/nix-library/fetch-prebuilt-binary.nix {
    inherit pkgs;
  };

  version = "0.153.4";

  codexUpstreamReleaseDescriptorBySystem = {
    "x86_64-linux" = {
      releaseTargetTriple = "x86_64-unknown-linux-musl";
      sha256 = "sha256-9HlCTsoJJITcQNh64oxE9MxAI0pgBF1hMeSTgA2BSjA=";
      codeModeHostSha256 = "sha256-+VgwqGlZCVdmS7/Ge8ywh3OAa2k2cLrxWQgXb4m0zTE=";
      buildInputs = with pkgs; [
        openssl
        libcap
        zlib
      ];
    };
    "aarch64-darwin" = {
      releaseTargetTriple = "aarch64-apple-darwin";
      sha256 = "sha256-jPkR6mdlI7+yEh7FYYSNKrpWSJCtU2202KM1PyuYULE=";
      codeModeHostSha256 = "sha256-Ramw/fU7mLhaa7keF13ZDpYTKKehT7UKQJAiBRmd8d8=";
      buildInputs = [ ];
    };
  };

  currentHostSystem = codexUpstreamReleaseDescriptorBySystem.${pkgs.stdenv.hostPlatform.system};

  codexReleaseAssetUrl =
    assetName:
    "https://github.com/openai/codex/releases/download/rust-v${version}/${assetName}-${currentHostSystem.releaseTargetTriple}.tar.gz";

  codex-binary = fetchPrebuiltBinary {
    pname = "codex";
    inherit version;
    url = codexReleaseAssetUrl "codex";
    inherit (currentHostSystem) sha256 buildInputs;
    binaryName = "codex";
    archiveBinaryPath = "codex-${currentHostSystem.releaseTargetTriple}";
  };

  codex-code-mode-host = fetchPrebuiltBinary {
    pname = "codex-code-mode-host";
    inherit version;
    url = codexReleaseAssetUrl "codex-code-mode-host";
    sha256 = currentHostSystem.codeModeHostSha256;
    inherit (currentHostSystem) buildInputs;
    binaryName = "codex-code-mode-host";
    archiveBinaryPath = "codex-code-mode-host-${currentHostSystem.releaseTargetTriple}";
  };

  codex-unwrapped = codex-binary.overrideAttrs (previousAttributes: {
    meta = (previousAttributes.meta or { }) // {
      mainProgram = "codex";
    };
    postFixup = (previousAttributes.postFixup or "") + ''
      ln -s ${codex-code-mode-host}/bin/codex-code-mode-host "$out/bin/codex-code-mode-host"
    '';
  });

  interactiveSessionDeveloperInstructionsText = lib.concatStringsSep "\n" [
    (builtins.readFile ../../../agent-harness/agent-instructions/skills/humanize/references/interactive-communication.md)
    (builtins.readFile ../../../agent-harness/agent-instructions/core-rules/servant-identity.md)
  ];

  interactivePreferencesFile = pkgs.writeText "codex-interactive-session-only-developer-instructions.md" interactiveSessionDeveloperInstructionsText;

  workspaceProfileActivation = import ./workspace-profile-activation.nix {
    inherit pkgs lib interactiveSessionDeveloperInstructionsText;
  };

  inherit (import ../../workspace-profiles/activation/harness-launch-dispatch.nix { inherit lib; })
    mkWorkspaceProfileLaunchDispatch
    ;

  workspaceProfileLaunchDispatch = mkWorkspaceProfileLaunchDispatch {
    inherit (config) agentWorkspaceProfiles;
    inherit (workspaceProfileActivation) activationShellStatementsForProfile;
  };

  workspaceProfileLaunchDispatchFile = pkgs.writeText "codex-workspace-profile-launch-dispatch" workspaceProfileLaunchDispatch;

  hookTrustExecutable = pkgs.writeShellScript "codex-approve-discovered-hooks" ''
    exec ${pkgs.python312}/bin/python3 ${./scripts/hook_trust}/approve.py "$@"
  '';

  codex = pkgs.writeShellApplication {
    name = "codex";
    bashOptions = [ ];
    excludeShellChecks = [ "SC1090" ];
    runtimeEnv = {
      NPM_CONFIG_PREFIX = "/nonexistent";
      CODEX_LAUNCHER_DEVELOPER_INSTRUCTIONS_FILE = "${interactivePreferencesFile}";
      CODEX_LAUNCHER_WORKSPACE_PROFILE_DISPATCH_FILE = "${workspaceProfileLaunchDispatchFile}";
      CODEX_LAUNCHER_BINARY = "${codex-unwrapped}/bin/codex";
      CODEX_LAUNCHER_HOOK_TRUST_EXECUTABLE = "${hookTrustExecutable}";
    };
    text = builtins.readFile ./scripts/codex;
  };
in
{
  options.codex.unwrappedPackage = lib.mkOption {
    type = lib.types.package;
    default = codex-unwrapped;
    readOnly = true;
    description = "The bare upstream codex binary, without the interactive wrapper that injects sandbox mode, approval policy and the human's own developer_instructions. An autonomous harness builds its own full argv and must launch this, because re-passing a flag the wrapper already injected makes codex exit 2.";
  };

  config.home = {
    packages = [ codex ];
    file.".local/bin/codex".source = "${codex}/bin/codex";
  };
}
