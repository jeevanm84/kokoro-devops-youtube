# Weekly routine — Kokoro DevOps

**Every Monday, 10 minutes of your time.** Everything else is automated.

## Your Monday checklist
| # | Task | Time | Where |
|---|---|---|---|
| 1 | Open YouTube Studio → Analytics → last week's video | 3 min | studio.youtube.com |
| 2 | Note: avg view duration, top drop-off point, best traffic source | 1 min | — |
| 3 | Reply to every new comment; pin a question if none pinned yet | 2 min | Studio → Comments |
| 4 | Check if this week's episode uploaded (Actions tab → produce-episode) | 30 s | GitHub |
| 5 | Open the private video in Studio, watch 2 min, check captions | 2 min | Studio |
| 6 | Answer the **"Does this video contain altered or synthetic content?"** question | 30 s | Studio → Details |
| 7 | Upload the thumbnail (until phone-verified; then the script does it) | 30 s | Studio → Details |
| 8 | **Publish** (change visibility to Public) | 10 s | Studio → Visibility |
| 9 | Paste the YouTube link into the lab repo README badge and push | 1 min | GitHub |
| 10 | Post the community update (07-community-post.txt) | 30 s | Studio → Community |

**Total: about 10 minutes.**

## To queue the next episode
```
# In your local repo:
# Open episodes/schedule.json and set "ready": true for the next episode, then:
git add episodes/schedule.json
git commit -m "queue episode-00N for production"
git push
# The Monday workflow picks it up automatically.
```

## What the automation does without you
- Renders all animations and the Short.
- Runs QA (a failed check blocks the upload).
- Uploads the main video and Short as **PRIVATE** with captions to YouTube.
- Records the video IDs so nothing is uploaded twice.

## What the automation never does without you
- Makes a video public.
- Answers the altered-content question.
- Posts comments or community posts.
- Spends money beyond GitHub Actions free minutes and the Sarvam API call.

## Monthly (10 minutes)
- Check Analytics → Audience retention on every published video.
- Update CONTENT-CALENDAR.md with the next 4 weeks of topics.
- Run `python3 automation/upload_youtube.py --auth-only` and update YT_TOKEN_JSON secret if the token is near expiry.

## Estimated weekly costs (check current pricing yourself)
| Item | Cost |
|---|---|
| GitHub Actions (render ~60 min on ubuntu-24.04) | Free on public repo; ~$0.50 on private |
| Sarvam Bulbul v3 (one episode ~5 min audio) | Check sarvam.ai/pricing |
| YouTube Data API upload | Free (within quota) |
| S3 (not built yet) | $0 until you add S3 |
