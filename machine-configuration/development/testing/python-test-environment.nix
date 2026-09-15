{ pkgs }:
pkgs.python312.withPackages (
  pythonPackages:
  [
    pythonPackages.pytest
    pythonPackages.pytest-cov
    pythonPackages.numpy
    pythonPackages.tomli-w
  ]
  ++ import ../../../agent-harness/quality/evaluations/instructions/python-packages.nix pythonPackages
)
