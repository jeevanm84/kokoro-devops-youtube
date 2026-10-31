# Weekly automation - setup (one time)

**What runs every Monday 15:00 IST** (`.github/workflows/produce-episode.yml`):

| Step | What happens | Fails safely if... |
|---|---|---|
| select | picks the first `ready: true` episode in `episodes/schedule.json` that isn't uploaded yet | nothing ready -> job ends with a notice, no cost |
| render | validate facts -> voice -> subtitles -> render -> assemble -> Short -> thumbnail -> metadata -> **QA** | any check fails -> **no upload** |
| upload | uploads main + Short as **PRIVATE** with captions (+ thumbnail once phone-verified) | token missing/expired -> clear error; already uploaded -> skipped |
| record | commits `upload-state.json` (video IDs) back to the repo | - |

You only: **flip `ready` to true** for an episode, then **review and publish** in YouTube Studio.

## 1. Google: stop the weekly token expiry
While the OAuth app is in *Testing*, Google refresh tokens expire after ~7 days, which would break unattended weekly runs.
1. Google Cloud -> **Google Auth Platform -> Audience -> Publishing status -> Publish app** (to *In production*). For your own use you can keep using it unverified; you'll still see the "unverified app" screen when signing in.
2. On your Mac, sign in again to get a long-lived token:
   ```
   cd ~/kokoro-devops-youtube && source .venv/bin/activate
   rm -f ~/.config/kokoro-devops/token.json
   python3 automation/upload_youtube.py --auth-only
   ```
Check Google's current rules if this behaves differently.

## 2. GitHub: environment + secrets (from your Mac, with `gh`)
```
cd ~/kokoro-devops-youtube
gh api -X PUT repos/jeevanm84/kokoro-devops-youtube/environments/youtube
gh secret set YT_CLIENT_SECRET_JSON --env youtube < ~/.config/kokoro-devops/client_secret.json
gh secret set YT_TOKEN_JSON         --env youtube < ~/.config/kokoro-devops/token.json
gh secret set SARVAM_API_KEY        # paste the key when prompted (only once you use Sarvam)
gh secret list --env youtube
```
Secrets never appear in logs or in the repo. If `main` is branch-protected, allow `github-actions[bot]` to push (it only commits `upload-state.json`).

## 3. First run (manual)
GitHub -> Actions -> **produce-episode** -> Run workflow -> episode `episode-002`, upload ON. Send the log of any failed step.

## 4. Voice per episode (`episodes/<ep>/script.json`)
```json
"tts": {"provider": "sarvam", "model": "bulbul:v3", "speaker": "<name from the playground>", "language": "en-IN", "pace": 0.95}
```
Telugu: `"language": "te-IN"` with the narration in Telugu script. Without a `tts` block the free Kokoro voice is used.

## 5. Weekly routine
1. Approve the next episode's script (I draft, you review).
2. Set `"ready": true` in `episodes/schedule.json`, commit, push.
3. Monday: review the private upload in Studio, answer the altered-content question, publish.

Not automated yet: topic/script generation via the Claude API; the Telugu second audio track (add it in Studio - I don't know of public API support for multi-language audio upload); S3 storage (GitHub artifacts are kept 30 days instead).
