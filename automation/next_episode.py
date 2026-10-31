"""Print the next episode to produce: first entry in episodes/schedule.json with "ready": true that is not fully uploaded yet."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
for e in json.load(open(ROOT / "episodes/schedule.json"))["queue"]:
    if not e.get("ready"): continue
    st = ROOT / "episodes" / e["episode"] / "upload-state.json"
    s = json.load(open(st)) if st.exists() else {}
    if not (s.get("main", {}).get("id") and s.get("short", {}).get("id")):
        print(e["episode"]); break
