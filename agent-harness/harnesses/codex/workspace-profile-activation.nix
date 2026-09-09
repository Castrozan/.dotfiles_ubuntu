{
  pkgs,
  lib,
  interactivePreferencesFile,
}:
let
  developerInstructionsFile =
    workspaceProfile:
    pkgs.runCommand "codex-workspace-profile-${workspaceProfile.name}-developer-instructions.md" { } ''
      for fragment in ${interactivePreferencesFile} ${lib.escapeShellArgs (map toString workspaceProfile.instructionFiles)}; do
        cat "$fragment"
        printf '\n'
      done > "$out"
    '';

  configOverrideArguments =
    workspaceProfile:
    lib.concatStringsSep " " (
      lib.mapAttrsToList (
        overrideKey: overrideValue: "-c ${lib.escapeShellArg "${overrideKey}=${toString overrideValue}"}"
      ) (workspaceProfile.codex.configOverrides or { })
    );
in
{
  activationShellStatementsForProfile =
    workspaceProfile:
    lib.concatStrings [
      (lib.optionalString (workspaceProfile.instructionFiles != [ ]) ''
        codexDeveloperInstructionsFile=${developerInstructionsFile workspaceProfile}
      '')
      (lib.optionalString (workspaceProfile.codex.configOverrides or { } != { }) ''
        workspaceProfileArguments+=(${configOverrideArguments workspaceProfile})
      '')
    ];
}
