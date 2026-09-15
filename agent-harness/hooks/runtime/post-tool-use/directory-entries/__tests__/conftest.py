import sys
from pathlib import Path

POLICY_DIRECTORY = Path(__file__).resolve().parents[1]
HOOKS_DIRECTORY = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(POLICY_DIRECTORY))
sys.path.insert(0, str(HOOKS_DIRECTORY / "common"))
