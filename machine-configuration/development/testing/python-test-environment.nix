{ pkgs }:
pkgs.python312.withPackages (
  pythonPackages:
  [
    pythonPackages.pytest
    pythonPackages.numpy
    pythonPackages.tomli-w
  ]
  ++ import ../../../agent-harness/quality/evaluations/instruction-python-packages.nix pythonPackages
)
