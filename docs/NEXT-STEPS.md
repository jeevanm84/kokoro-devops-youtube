# What YOU need to do next
## Now (no accounts needed)
1. **Watch `youtube-video.mp4` and `youtube-short.mp4` end to end, with sound, on a phone too.** Automated QA cannot judge pronunciation, taste or readability. Note anything wrong (timestamps).
2. **Decide the channel name** (placeholder "Under The Hood") and check handle/trademark availability.
3. **Decide the voice:** keep the free local Kokoro voice, or tell me a paid provider to wire in.
4. Read `qa-report.md` MANUAL items and `docs/ASSETS-LICENSES.md`.
## To publish Episode 001 (manual path, works today)
5. Create the YouTube channel; upload `youtube-video.mp4` as **Private**, set the thumbnail, paste title/description/tags from `metadata.json`, upload `subtitles/youtube-video.en.srt`. Repeat for the Short. Disclose AI narration if YouTube's current rules require it.
## To automate (needs your accounts — I cannot do these)
6. Create a GitHub repo, push this folder, run the `produce-episode` workflow manually, and send me the log if it fails.
7. For weekly script generation: an **Anthropic API key** stored as a GitHub secret.
8. For uploads: a Google Cloud project, YouTube Data API v3 enabled, an OAuth client, and a one-time consent. Unverified API projects may be restricted to private uploads — check current YouTube policy.
9. For S3 + AWS OIDC: an AWS account/role (least privilege, bucket for artifacts).
10. Tell me whether you want the TypeScript + Remotion rebuild, and where it can be tested (Docker or GitHub Actions) — it cannot be tested in this sandbox.
