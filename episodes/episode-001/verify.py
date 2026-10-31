"""Episode hook: technical validation (pipeline 'validate' stage)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "automation"))
import validate_technical; sys.exit(0 if validate_technical.run("episode-001") else 1)
