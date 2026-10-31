# Git & Docker Interview Bootcamp - scenario-based (draft v1)

**Promise:** answer real interview and on-call scenarios for Git and Docker confidently, with hands-on labs - not theory dumps.
**Audience:** freshers and 3-8 yr engineers moving into DevOps/SRE/backend. Tag every question Fresher / Experienced.
**Lesson format (every lesson):** 1) scenario hook 2) whiteboard answer (what to SAY in 60 s) 3) animated visual of the mechanism 4) hands-on lab 5) 10-question quiz 6) "interviewer follow-ups".

| # | Lesson | Scenarios | Status of content |
|---|---|---|---|
| 1 | Git mental model: working tree, index, repo, HEAD | basics | to write |
| 2 | The undo toolkit: restore / reset / revert / reflog | G1 G2 G3 G4 | **commands verified** |
| 3 | Branching: merge vs rebase vs fast-forward | G12 G5 | **verified** |
| 4 | Cleaning & moving history: squash, cherry-pick, stash | G6 G7 G9 | **verified** |
| 5 | Debugging history: bisect, blame, pickaxe | G8 G13 | **verified** |
| 6 | Team safety: force-with-lease, secrets, protected branches | G11 G10 | **verified** |
| 7 | Git mock interview (20 rapid-fire Qs) | all | to write |
| 8 | Containers vs VMs; namespaces & cgroups | D1 D2 | answers written, labs **not run** |
| 9 | Dockerfile craft: layers, cache, CMD/ENTRYPOINT | D3 D5 | not run |
| 10 | Small & secure images: multi-stage, hardening, secrets | D4 D9 D10 | not run |
| 11 | Storage: volumes, bind mounts | D7 | not run |
| 12 | Networking & Compose | D8 D11 | not run |
| 13 | Production debugging: exits, OOM, disk, tags | D6 D12 D13 D14 | not run |
| 14 | Docker in the real world: ECS/Kubernetes, final mock interview | D15 | not run |

## Video plan (first 4, ~6-8 min each, same animation style)
1. **Git: reset vs revert vs restore - which one and when?** (G1-G3) - animate the three areas and HEAD moving.
2. **Merge vs rebase: what really happens to your commits** (G12) - commits replayed with new SHAs.
3. **Docker layers & cache: why your build is slow** (D2 D5) - layer stack, cache hit/miss animation.
4. **"Localhost" doesn't work in Docker: container networking** (D8) - packet path between containers.
Free on YouTube; the paid course adds all 14 lessons' labs, quizzes, mock-interview sets and project repos.

## Before selling anything
- Docker labs must be run and corrected by a human on real Docker (I couldn't).
- Content must be your own original explanation - do not reuse another course's lessons.
- Validate demand with the free videos and a waitlist first; check hosting platform fees/terms yourself.
