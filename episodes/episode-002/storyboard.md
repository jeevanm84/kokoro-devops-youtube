# Episode 002 storyboard - Git undo toolkit
All terminal snippets below are REAL output captured by verify_git_undo.py (Git 2.43). Animate them verbatim.
Layout reuses templates/brand.py (same visual language as Episode 001: cards, amber data packet, pointer).

| Scene | Visual | On-screen terminal / labels (verbatim) |
|---|---|---|
| s01 hook | Terminal: `git commit` -> red "oops" stamp; four tool names fly in | - |
| s02 three places | Three columns Working dir -> Index -> Repository, HEAD pointer on latest commit (from the repo's own diagram) | - |
| s03 restore | File card with red edit; `git restore app.txt` removes it. Then staged card moves back | before: `M  app.txt` after: ` M app.txt` |
| s04 reset | Commit chain A-B-C, branch label slides C -> B. Three lanes (soft/mixed/hard) show which of the three places reset | soft: `M  app.txt`  mixed: ` M app.txt`  hard: (empty) |
| s05 revert | Chain A-B-C then new commit "Revert C" appended; C stays | `git log --oneline`:
8c8774d Revert "C: oops"
9b20f4a C: oops
210465b B: second
f4f9b8f A: first |
| s06 reflog | Journal list slides; pointer jumps back to lost commit | `git reflog`:
e938990 HEAD@{0}: reset: moving to HEAD~1
8a1b9c4 HEAD@{1}: commit: C: oops
e938990 HEAD@{2}: commit: B: second |
| s07 replay | Split screen: left a 3-commit chain A-B-C, right a live-style terminal replaying the commands | soft `M  app.txt` / mixed ` M app.txt` / hard (empty) / reflog:\ne938990 HEAD@{0}: reset: moving to HEAD~1
8a1b9c4 HEAD@{1}: commit: C: oops
e938990 HEAD@{2}: commit: B: second |
| s08 mistakes | Three red-flag cards: pushed+reset+force, uncommitted+hard, revert!=secret removal | - |
| s09 interview | Seven-step framework chain: Impact -> Evidence -> Investigation -> Mitigation -> Communication -> Permanent fix -> Prevention (from docs/INTERVIEW_QUESTIONS.md) | - |
| s10 lab | Repo card + "Lab 05 Undo and reflog recovery" + QR/URL; subscribe button | https://github.com/jeevanm84/git-command-master-map |
Short (30 s): three lanes soft/mixed/hard only.
