# YouTube <-> GitHub flywheel (built on jeevanm84's own repos)
Observed on 2026-10-30 from the public pages: GitHub profile had **1 follower**, 0 following, 17 repos; `git-command-master-map` had **0 stars**. These are the baselines to beat. I cannot promise any follower or revenue number.

## Principle
Every video teaches ONE scenario using YOUR lab; the viewer's next step is a link to the exact lab. Every repo README links back to the video. Content stays original because it is your own repo.

## Video -> repo mapping (first 8)
| # | Video (interview scenario) | Repo + lab to link | Notes |
|---|---|---|---|
| 1 | Git: undo a commit - reset vs revert vs restore | git-command-master-map, Lab 05 (Undo and reflog recovery), docs/TROUBLESHOOTING.md | Show `./scripts/new-sandbox.sh`, then the lab |
| 2 | Merge vs rebase - what happens to commits | Lab 02 (Branching/merging), Lab 04 (Rebase/cherry-pick) | Animated commit replay |
| 3 | Resolve a merge conflict like a pro | Lab 03 (Conflicts) | Scenario: two devs, one file |
| 4 | Find the commit that broke prod (git bisect) | Lab 06 (Bisect) | `git bisect run` demo |
| 5 | Docker layers and build cache | docker-zero-to-production (layered + multi-stage build labs) | confirm exact lab names in the repo |
| 6 | Docker networking: why localhost fails | docker-zero-to-production (storage/networking lab) | |
| 7 | Compose and Swarm high availability | docker-zero-to-production (Compose/Swarm labs) | |
| 8 | CI/CD to Docker Hub with Jenkins | docker-zero-to-production (Jenkins -> Docker Hub -> Swarm pipeline) | |
Then follow the repo order in your own roadmap: Kubernetes, Terraform HA web platform, Packer, CI/CD and GitOps, Observability/SRE, CloudFront/WAF/Shield.
Links used (all seen on your public profile): github.com/jeevanm84 - /git-command-master-map - /docker-zero-to-production - /kubernetes-zero-to-production - /terraform-aws-ha-web-platform - jeevanm84.github.io/git-command-master-map/ (interactive Visual Map).

## Paste into every video description
```
HANDS-ON LAB (free, run it yourself): <repo lab URL>
Whole repo: https://github.com/jeevanm84/<repo>   (star it if it helped)
Interactive Git map: https://jeevanm84.github.io/git-command-master-map/
Follow on GitHub: https://github.com/jeevanm84
```
## Pinned comment
"Try the lab from this video: <lab URL>. Stuck? Open a GitHub Discussion on the repo and I'll answer. Which scenario next?"

## Add to each repo README (you commit these - I cannot edit your repos)
```
[![Watch the video](https://img.shields.io/badge/YouTube-Watch%20the%20walkthrough-red?logo=youtube)](<video URL>)
```
Add the video URL under each lab's header, and your channel link to the profile README "Connect and collaborate" section. Turn on GitHub Discussions (already linked in your profile) so viewers have somewhere to ask.

## Growth tactics that are legitimate
- 1 long video + 3 Shorts per week from the same lab; every Short links the lab.
- Shareable assets: the GitHub Pages Visual Map (post it on LinkedIn with a 30-second clip).
- Titles = the exact interview question people search ("git reset vs revert", "docker localhost not working").
- Ask viewers to star the repo only AFTER they finish the lab (higher intent).
- Telugu/Indian dev communities (WhatsApp/Telegram/LinkedIn groups): share the lab, not just the video.
- Track weekly: YouTube impressions, CTR, avg view duration, link clicks (UTM-tag the links: ?utm_source=youtube&utm_medium=video&utm_campaign=git-undo); GitHub stars, clones, followers (Insights > Traffic).
Do NOT buy followers/stars/views or use sub-for-sub schemes: they violate platform rules and hurt reach and monetization.

## Before recording each video
1. Run the lab yourself and note anything that fails. 2. Send me the lab's README/commands (or its URL) so I can build the script and animation from it and validate commands in a sandbox where possible (Git: yes; Docker: no runtime here, you must run them).
