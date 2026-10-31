# Telugu + English dual audio track — how it works

## What viewers see
While the video plays, they click the **gear icon → Audio track** and switch between:
- **English** (default)
- **తెలుగు** (Telugu)

One video, one URL, two languages. YouTube handles the switching.

## How we produce it
1. English audio: existing Kokoro pipeline (or Sarvam English voice)
2. Telugu audio: Sarvam Bulbul v3, speaker Manan, language te-IN, natural code-mixed style
3. Both tracks are timed to the LONGER language per scene so animations stay in sync
4. We produce two MP4 files: `youtube-video-en.mp4` (main upload) and `youtube-video-te.mp4` (Telugu track)

## Commands (on your Mac, after getting SARVAM_API_KEY)
```bash
cd ~/kokoro-devops-youtube && source .venv/bin/activate
export SARVAM_API_KEY="your-key-here"    # never commit this

# Generate Telugu audio
python automation/tts_sarvam.py episode-002 te

# Assemble Telugu video
python automation/assemble_dual.py episode-002

# See upload instructions
python automation/upload_telugu_track.py episode-002
```

## Adding Telugu track in YouTube Studio (manual, ~2 minutes)
The YouTube Data API does not support multi-language audio upload.
Do it once per video in Studio:
1. Open studio.youtube.com → your video
2. Click **Dubbing** tab (or **Audio tracks**)
3. Click **Add language** → Telugu
4. Upload `episodes/episode-002/youtube-video-te.mp4`
5. Save

## Telugu narration style
- Technical terms in English: `commit`, `branch`, `reset`, `staging area`, `reflog`
- Explanations in natural conversational Telugu
- Same style as popular Telugu DevOps channels (NareshIT, TechWorld with Murali)
- No formal/literary Telugu — the way engineers actually speak

## Getting the Sarvam API key
1. Go to dashboard.sarvam.ai
2. Sign up (free tier available)
3. Create an API key
4. Add to GitHub: `gh secret set SARVAM_API_KEY --env youtube`
5. Local use: `export SARVAM_API_KEY="sk-..."` in your terminal session
