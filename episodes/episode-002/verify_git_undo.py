"""Runs every Git behaviour shown in Episode 002 (undo toolkit) in a scratch repo, asserts the claims, and records REAL terminal output to facts.json."""
import json, os, subprocess, tempfile
env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x", "GIT_CONFIG_GLOBAL": "/dev/null"}
facts, results = {}, []
def sh(cmd, cwd, check=True):
    r = subprocess.run(cmd, shell=True, cwd=cwd, env=env, capture_output=True, text=True)
    if check and r.returncode: raise RuntimeError(f"{cmd}\n{r.stderr}")
    return (r.stdout + r.stderr).rstrip("\n")
def check(name, ok, detail=""):
    results.append((name, bool(ok))); print(("PASS " if ok else "FAIL ") + name, "" if ok else detail)
def fresh():
    d = tempfile.mkdtemp(); sh("git init -q -b main .", d)
    for m in ("A: first", "B: second", "C: oops"):
        sh(f"echo '{m}' >> app.txt && git add . && git commit -qm '{m}'", d)
    return d

# soft / mixed / hard
d = fresh(); sh("git reset --soft HEAD~1", d)
facts["soft_status"] = sh("git status --short", d); facts["soft_log"] = sh("git log --oneline", d)
check("soft: HEAD moved back 1 commit", facts["soft_log"].count("\n") == 1)
check("soft: change stays STAGED (M in first column)", facts["soft_status"].startswith("M "), facts["soft_status"])
d = fresh(); sh("git reset --mixed HEAD~1", d)
facts["mixed_status"] = sh("git status --short", d)
check("mixed: change stays in working tree, UNSTAGED", facts["mixed_status"].startswith(" M"), facts["mixed_status"])
d = fresh(); sh("git reset --hard HEAD~1", d)
facts["hard_status"] = sh("git status --short", d); facts["hard_file"] = open(f"{d}/app.txt").read().strip()
check("hard: nothing left to commit, file content reverted", facts["hard_status"] == "" and "oops" not in facts["hard_file"])
# reflog recovery after hard reset
lost = sh("git rev-parse --short HEAD@{1}", d); facts["reflog"] = sh("git reflog -3", d)
sh("git reset --hard HEAD@{1}", d)
check("reflog: reset --hard commit recovered via HEAD@{1}", "oops" in open(f"{d}/app.txt").read(), facts["reflog"])
# restore
d = fresh(); sh("echo junk >> app.txt", d); facts["restore_before"] = sh("git status --short", d)
sh("git restore app.txt", d); check("restore: discards working-tree change", sh("git status --short", d) == "" and "junk" not in open(f"{d}/app.txt").read())
sh("echo staged >> app.txt && git add app.txt", d); facts["restore_staged_before"] = sh("git status --short", d)
sh("git restore --staged app.txt", d); facts["restore_staged_after"] = sh("git status --short", d)
check("restore --staged: unstages but keeps the edit", facts["restore_staged_after"].startswith(" M") and "staged" in open(f"{d}/app.txt").read())
# revert (shared-branch safe)
d = fresh(); sh("git revert --no-edit HEAD", d); facts["revert_log"] = sh("git log --oneline", d)
check("revert: adds a NEW commit, history preserved (4 commits)", facts["revert_log"].count("\n") == 3 and "oops" not in open(f"{d}/app.txt").read())
check("revert: original bad commit still in history", "C: oops" in facts["revert_log"])
# hard reset does not touch untracked files
d = fresh(); sh("echo keep > untracked.txt", d); sh("git reset --hard HEAD~1", d)
check("hard reset does NOT delete untracked files", os.path.exists(f"{d}/untracked.txt"))
json.dump(facts, open("facts.json", "w"), indent=2)
print(f"{sum(ok for _, ok in results)}/{len(results)} passed"); raise SystemExit(0 if all(ok for _, ok in results) else 1)
