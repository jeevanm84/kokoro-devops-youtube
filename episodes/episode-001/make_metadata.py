"""Episode hook: metadata.json (chapters from real timings)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "automation"))
import metadata; metadata.run("episode-001")
