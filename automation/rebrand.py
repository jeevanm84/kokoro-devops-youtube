"""One command to apply the final channel name everywhere.
  python automation/rebrand.py "Final Name" [--handle @name]
Rewrites channel.json, re-renders only what changed (watermarks), rebuilds video/short/thumbnail/QA, then the upload kit."""
import json, subprocess, sys
from config import ROOT
args = [a for a in sys.argv[1:]]; name = args[0]
cfg = json.load(open(ROOT / "channel.json")); cfg["name"] = name; cfg["status"] = "FINAL"
if "--handle" in args: cfg["handle"] = args[args.index("--handle") + 1]
json.dump(cfg, open(ROOT / "channel.json", "w"), indent=2, ensure_ascii=False)
A = ROOT / "automation"
for cmd in (["python3", str(A / "pipeline.py"), "run", "episode-001", "--from", "render"], ["python3", str(A / "build_upload_kit.py"), "episode-001"]):
    if subprocess.run(cmd).returncode: sys.exit(1)
