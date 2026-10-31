"""Episode 002 facts = REAL output recorded by verify_git_undo.py (facts.json). Scenes import these; never hand-type terminal output."""
import json, pathlib
F = json.load(open(pathlib.Path(__file__).with_name("facts.json")))
SOFT, MIXED, HARD = F["soft_status"], F["mixed_status"], F["hard_status"]
REFLOG = F["reflog"].splitlines(); REVERT_LOG = F["revert_log"].splitlines()
STAGED_BEFORE, STAGED_AFTER = F["restore_staged_before"], F["restore_staged_after"]
