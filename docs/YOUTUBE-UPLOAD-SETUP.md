# Automated YouTube upload - one-time setup (on your Mac)

`automation/upload_youtube.py` uploads an episode's main video + Short as **PRIVATE**, with title, description, tags, thumbnail and English captions, using the official YouTube Data API v3. Publishing stays manual in YouTube Studio.

## 1. Google Cloud (about 10 minutes, once)
1. Open https://console.cloud.google.com and create a project, e.g. `kokoro-devops`.
2. **APIs & Services -> Library**: enable **YouTube Data API v3**.
3. **APIs & Services -> OAuth consent screen** (Google Auth Platform): user type **External**, app name `Kokoro DevOps uploader`, your email; add **your own Google account as a Test user**.
4. **Credentials -> Create credentials -> OAuth client ID -> Application type: Desktop app**. Download the JSON.
5. Save it outside the repo:
   ```
   mkdir -p ~/.config/kokoro-devops
   mv ~/Downloads/client_secret_*.json ~/.config/kokoro-devops/client_secret.json
   chmod 600 ~/.config/kokoro-devops/client_secret.json
   ```
Never commit this file (`.gitignore` blocks `client_secret*.json` and `token*.json`; the script keeps them in `~/.config/kokoro-devops/`).

## 2. Install and test (no upload)
```
cd ~/kokoro-devops-youtube
python3 -m pip install -r requirements-upload.txt
cp ~/Downloads/<episode-2 main video>.mp4  episodes/episode-002/youtube-video.mp4
cp ~/Downloads/<episode-2 short>.mp4       episodes/episode-002/youtube-short.mp4
python3 automation/upload_youtube.py episode-002 --dry-run
```
## 3. Upload
```
python3 automation/upload_youtube.py episode-002
```
The first run opens your browser: sign in and **choose the Kokoro DevOps channel**. Re-running is safe: already-uploaded items are skipped (IDs saved in `episodes/<ep>/upload-state.json`; commit that file so other machines/CI don't upload duplicates).

## Things Google controls (verify current rules)
- **Unverified API projects:** YouTube has stated that videos uploaded through `videos.insert` from unverified API projects created after 28 July 2020 are restricted to **private** until the project passes a YouTube API Services compliance audit. Private is what we want for review, but you may need the audit (or to re-upload manually in Studio) before those videos can go public. Check the current policy and apply for the audit early if needed.
- **Testing-mode tokens:** while the OAuth app is in "Testing" with External users, Google issues refresh tokens that expire after about 7 days, so you will sign in again weekly unless the app is published/verified.
- **Quota:** uploads use a large share of the default daily API quota (`videos.insert` has historically cost 1,600 of 10,000 units/day). The script stops cleanly on `quotaExceeded`; re-run tomorrow, nothing is duplicated.
- **Custom thumbnails** need a phone-verified channel; if not verified the script warns and you set the thumbnail in Studio.
- In Studio, answer the **altered/synthetic content** question yourself (AI narration) before publishing.
