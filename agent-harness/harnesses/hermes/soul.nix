{ pkgs }:
let
  hermesIdentity = "You are Hermes Agent, an intelligent AI assistant created by Nous Research.";
  canonicalCore = builtins.readFile ../../agent-instructions/core-rules/core.md;
in
pkgs.writeText "hermes-SOUL.md" "### Harness identity\n\n${hermesIdentity}\n\n${canonicalCore}"
