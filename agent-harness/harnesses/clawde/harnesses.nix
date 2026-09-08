{ config, lib, ... }:
{
  clawde.harnesses =
    lib.optionalAttrs (config ? claude) {
      claude.package = config.claude.unwrappedPackage;
    }
    // lib.optionalAttrs (config ? codex) {
      codex.package = config.codex.unwrappedPackage;
    }
    // lib.optionalAttrs (config ? opencode) {
      opencode.package = config.opencode.unwrappedPackage;
    };

  home.file =
    lib.mkIf
      (
        config ? codex
        && lib.any (agent: agent.harness == "codex") (builtins.attrValues config.clawde.agents)
      )
      {
        "clawde/harness-home/codex/bin/codex-code-mode-host".source =
          "${config.clawde.harnesses.codex.package}/bin/codex-code-mode-host";
      };
}
