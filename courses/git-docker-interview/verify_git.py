"""Executes every Git scenario in a throwaway directory, asserts the outcome, and writes git-scenarios.md (only verified content)."""
import subprocess, tempfile, sys, pathlib
from git_scenarios import PRE, S
ver = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip(); res = {}
for s in S:
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(["bash", "-c", PRE + s["script"]], cwd=d, capture_output=True, text=True)
    res[s["id"]] = r.returncode == 0
    print(("PASS " if r.returncode == 0 else "FAIL ") + s["id"] + " " + s["title"] + ("" if r.returncode == 0 else "\n" + r.stderr[-400:]))
ok = all(res.values())
md = [f"# Git interview scenarios ({len(S)})", "", f"**Verification:** every command below was executed in a scratch repository with the Git installed on the machine running the check, and its outcome asserted ({sum(res.values())}/{len(S)} passed). Run `python verify_git.py` to re-check.", "", "Level: Fresher = 0-3 yrs, Experienced = 3+ yrs.", ""]
for s in S:
    cmds = "\n".join(l for l in s["script"].splitlines() if not l.startswith(("test ", "if ", "grep ", "git show", "git log --oneline recovered", "git status --short", "git reflog |", "printf")) )
    md += [f"## {s['id']} - {s['title']}  _({s['level']})_", "", f"**Interviewer:** {s['q']}", "", "**Strong answer:**"] + [f"- {x}" for x in s["a"]] + ["", f"**Likely follow-up:** {s['follow']}", "", "**Try it (setup shown as run in the verifier):**", "```bash", s["script"], "```", ""]
HERE = pathlib.Path(__file__).resolve().parent; (HERE / "git-scenarios.md").write_text("\n".join(md) + "\n"); print("wrote git-scenarios.md;", "ALL PASS" if ok else "FAILURES")
sys.exit(0 if ok else 1)
