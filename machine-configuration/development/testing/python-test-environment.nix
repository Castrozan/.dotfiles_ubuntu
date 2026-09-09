{ pkgs }:
pkgs.python312.withPackages (pythonPackages: [
  pythonPackages.pytest
  pythonPackages.numpy
  pythonPackages.tomli-w
  pythonPackages.pyyaml
  pythonPackages.markdown-it-py
  (pythonPackages.callPackage
    ../../../agent-harness/quality/evaluations/github-slugger-python-package.nix
    { }
  )
])
