# Git interview scenarios (13)

**Verification:** every command below was executed in a scratch repository with the Git installed on the machine running the check, and its outcome asserted (13/13 passed). Run `python verify_git.py` to re-check.

Level: Fresher = 0-3 yrs, Experienced = 3+ yrs.

## G1 - Undo the last commit but keep my work  _(Fresher)_

**Interviewer:** I committed too early. How do I undo the commit but keep the changes?

**Strong answer:**
- `git reset --soft HEAD~1` moves the branch back one commit and leaves the changes STAGED.
- `--mixed` (default) leaves them unstaged; `--hard` throws them away (dangerous).
- Only safe for commits not yet pushed/shared - otherwise use `git revert`.

**Likely follow-up:** Difference between soft, mixed and hard? What if it was already pushed?

**Try it (setup shown as run in the verifier):**
```bash
commit one; commit two
git reset --soft HEAD~1
test "$(n)" = 1
if git diff --cached --quiet; then exit 1; fi
grep -q two f.txt
```

## G2 - I committed on the wrong branch  _(Fresher)_

**Interviewer:** I made a commit on main that belongs on a feature branch. Fix it before pushing.

**Strong answer:**
- Create the branch at the current commit: `git branch feature`.
- Move main back: `git reset --hard HEAD~1` (the commit is still on `feature`).
- Check with `git log --oneline --all --graph`.

**Likely follow-up:** What if you had already pushed main? (Don't rewrite shared history - revert instead.)

**Try it (setup shown as run in the verifier):**
```bash
commit one; commit two
git branch feature
git reset --hard HEAD~1
test "$(n main)" = 1; test "$(n feature)" = 2
```

## G3 - Undo a commit that is already pushed  _(Fresher)_

**Interviewer:** A bad commit is on the shared main branch. How do you undo it safely?

**Strong answer:**
- `git revert <sha>` creates a NEW commit that reverses the change; history is preserved.
- Never `reset` + force-push shared branches - it rewrites history others rely on.
- For a merge commit use `git revert -m 1 <merge-sha>`.

**Likely follow-up:** Why not reset? What does -m 1 mean?

**Try it (setup shown as run in the verifier):**
```bash
commit one; commit bad
git revert --no-edit HEAD >/dev/null
test "$(n)" = 3
if grep -q bad f.txt; then exit 1; fi
```

## G4 - Recover a deleted branch / lost commits  _(Experienced)_

**Interviewer:** I deleted a branch with unmerged work. Is it gone?

**Strong answer:**
- Not yet: `git reflog` records where HEAD and branches pointed, for ~90 days by default for reachable entries (30 for unreachable).
- Find the sha, then `git branch recovered <sha>`.
- Garbage collection eventually removes unreachable commits - recover quickly.

**Likely follow-up:** What does reflog track? Does it get pushed? (No - it is local.)

**Try it (setup shown as run in the verifier):**
```bash
commit one; git checkout -q -b feature; commit work; sha=$(git rev-parse HEAD)
git checkout -q main; git branch -D feature >/dev/null
if git rev-parse --verify -q feature >/dev/null; then exit 1; fi
git reflog | grep -q work
git branch recovered "$sha"
git log --oneline recovered | grep -q work
```

## G5 - Resolve a merge conflict  _(Fresher)_

**Interviewer:** Walk me through resolving a merge conflict.

**Strong answer:**
- `git merge` stops and marks files (`git status` shows both added/modified).
- Edit the file, remove the `<<<<<<<`/`=======`/`>>>>>>>` markers, keep the correct result.
- `git add <file>` then `git commit` (or `git merge --continue`). `git merge --abort` backs out.

**Likely follow-up:** How do you reduce conflicts? (small PRs, frequent rebase/merge from main, ownership)

**Try it (setup shown as run in the verifier):**
```bash
commit base; git checkout -q -b b1; echo b1 > c.txt; git add .; git commit -qm b1
git checkout -q main; echo main > c.txt; git add .; git commit -qm m1
if git merge b1 >/dev/null 2>&1; then exit 1; fi
git status --short | grep -qE '^(AA|UU)'
printf 'resolved\n' > c.txt; git add c.txt; git commit -qm merged
test "$(git cat-file -p HEAD | grep -c '^parent')" = 2
```

## G6 - Squash messy commits before a PR  _(Experienced)_

**Interviewer:** My branch has 4 noisy commits. Clean it up.

**Strong answer:**
- `git rebase -i HEAD~3` then mark later commits `squash`/`fixup`.
- Only rewrite commits that are not yet shared (or agree with the team).
- Alternative: `git reset --soft HEAD~3 && git commit`.

**Likely follow-up:** Squash vs fixup? What changes about commit SHAs after a rebase?

**Try it (setup shown as run in the verifier):**
```bash
commit one; commit two; commit three; commit four
GIT_SEQUENCE_EDITOR="sed -i '2,3s/^pick/squash/'" GIT_EDITOR=true git rebase -i HEAD~3 >/dev/null 2>&1
test "$(n)" = 2
```

## G7 - Ship one fix to a release branch (cherry-pick)  _(Experienced)_

**Interviewer:** A hotfix is on main but only that fix must go to release/1.0.

**Strong answer:**
- `git switch release/1.0 && git cherry-pick <sha>` copies just that commit (new SHA).
- Keep notes of cherry-picks; prefer fixing on the release branch and merging forward when possible.

**Likely follow-up:** Cherry-pick vs merge? Conflicts?

**Try it (setup shown as run in the verifier):**
```bash
cf a.txt base; git branch release; cf feat.txt feat; cf hot.txt hotfix; fix=$(git rev-parse HEAD)
git checkout -q release; git cherry-pick "$fix" >/dev/null
test -f hot.txt; if test -f feat.txt; then exit 1; fi
```

## G8 - Find which commit broke the build (bisect)  _(Experienced)_

**Interviewer:** It worked last week, now it's broken, 200 commits later. How do you find the culprit fast?

**Strong answer:**
- `git bisect start <bad> <good>` does a binary search over history (~log2 N steps).
- Automate: `git bisect run <test-script>` (exit 0 = good, 1-127 = bad).
- Finish with `git bisect reset`.

**Likely follow-up:** What if the test is flaky? What about skipping untestable commits (`bisect skip`)?

**Try it (setup shown as run in the verifier):**
```bash
commit c1; commit c2; commit c3; commit BUG; commit c5; commit c6
good=$(git rev-parse HEAD~5)
git bisect start HEAD "$good" >/dev/null
git bisect run sh -c '! grep -q BUG f.txt' > out.txt 2>&1
grep -q "first bad commit" out.txt
git show -s --format=%s refs/bisect/bad | grep -q BUG
git bisect reset >/dev/null 2>&1
```

## G9 - Urgent hotfix while I have half-done work  _(Fresher)_

**Interviewer:** Mid-feature, a production bug lands. How do you switch context cleanly?

**Strong answer:**
- `git stash` saves tracked changes (add `-u` for untracked).
- Switch branch, fix, push. Come back: `git stash pop`.
- `git stash list` to see entries; worktrees (`git worktree add`) are a nicer alternative.

**Likely follow-up:** Stash vs WIP commit? Does stash include untracked files by default? (No.)

**Try it (setup shown as run in the verifier):**
```bash
commit one; echo wip >> f.txt; git stash -q; test -z "$(git status --porcelain)"
git checkout -q -b hotfix; commit fix; git checkout -q main; git stash pop -q; grep -q wip f.txt
```

## G10 - A secret was committed (and pushed)  _(Experienced)_

**Interviewer:** Someone committed an AWS key to the repo. What do you do?

**Strong answer:**
- FIRST: revoke/rotate the credential - assume it is compromised; history rewriting does not un-leak it.
- Remove it from history (`git filter-repo`, or `filter-branch`/BFG), expire reflogs, gc, then force-push and tell everyone to re-clone.
- Prevent: `.gitignore`, pre-commit secret scanning, push protection, secrets manager.

**Likely follow-up:** Why isn't deleting the file in a new commit enough? (It stays in history.)

**Try it (setup shown as run in the verifier):**
```bash
commit one; echo "AWS_KEY=AKIAFAKE" > .env; git add .env; git commit -qm "add env"; commit two
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --index-filter 'git rm --cached --ignore-unmatch -q .env' -- --all >/dev/null 2>&1
git for-each-ref --format='%(refname)' refs/original | xargs -r -n1 git update-ref -d
git reflog expire --expire=now --all; git gc -q --prune=now
if git log --all -p | grep -q AKIAFAKE; then exit 1; fi
```

## G11 - Force-push safely  _(Experienced)_

**Interviewer:** After rebasing my branch I must force-push. How do you avoid wiping a teammate's work?

**Strong answer:**
- Use `git push --force-with-lease` - it refuses if the remote moved since you last fetched.
- Plain `--force` overwrites whatever is there (demonstrated below: teammate's commit is lost).
- Protect main with branch protection; never force-push shared branches.

**Likely follow-up:** What does the lease compare against? (your remote-tracking ref)

**Try it (setup shown as run in the verifier):**
```bash
git init -q --bare -b main ../remote.git
commit one; git remote add origin ../remote.git; git push -q origin main 2>/dev/null
git clone -q ../remote.git ../mate; (cd ../mate && echo m >> f.txt && git commit -qam mate && git push -q origin main 2>/dev/null)
commit mine
if git push -q --force-with-lease origin main 2>/dev/null; then exit 1; fi
git push -q --force origin main 2>/dev/null
test "$(git --git-dir=../remote.git log --oneline main | wc -l | tr -d ' ')" = 2
if git --git-dir=../remote.git log --format=%s main | grep -q mate; then exit 1; fi
```

## G12 - Merge vs rebase  _(Fresher)_

**Interviewer:** Explain merge vs rebase. When do you use each?

**Strong answer:**
- Merge keeps true history and adds a merge commit; rebase replays your commits on the new base for a LINEAR history (new SHAs).
- Rebase local/private branches; merge (or squash-merge) into shared branches; never rebase published shared history.
- Golden rule: don't rewrite commits others have based work on.

**Likely follow-up:** What is a fast-forward merge?

**Try it (setup shown as run in the verifier):**
```bash
cf a.txt base; git checkout -q -b feat; cf f1.txt f1; git checkout -q main; cf m1.txt m1
git checkout -q feat; git rebase -q main
test "$(git rev-list --merges feat | wc -l | tr -d ' ')" = 0
git checkout -q main; git merge -q --ff-only feat
test "$(git rev-list --merges main | wc -l | tr -d ' ')" = 0
```

## G13 - Who introduced this line, and when?  _(Experienced)_

**Interviewer:** A config value changed in production. How do you find the commit that introduced it?

**Strong answer:**
- `git log -S"token=abc"` (pickaxe) lists commits that added/removed that string; `-G` for regex.
- `git blame <file>` shows the last commit per line; `git log -p -- <file>` shows file history.
- `git blame -w -C` ignores whitespace/moved code.

**Likely follow-up:** Blame vs pickaxe? Why can blame mislead after reformatting?

**Try it (setup shown as run in the verifier):**
```bash
commit one; commit "token=abc"; commit three
git log -S"token=abc" --format=%s | grep -q 'token=abc' 
```

