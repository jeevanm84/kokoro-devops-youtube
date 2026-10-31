"""
Upload the Telugu audio track to an existing YouTube video as a second language track.
YouTube API does not support multi-language audio upload via videos.insert/update —
this feature is only available in YouTube Studio UI.
This script generates the Telugu video file ready for manual upload in Studio.

Studio steps (after running this script):
  1. Open studio.youtube.com -> your video -> Audio tracks (or Dubbing tab)
  2. Click "Add language" -> Telugu
  3. Upload youtube-video-te.mp4
  Viewers then switch languages via the gear icon while watching.
"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
def run(ep):
    d = ROOT / "episodes" / ep
    te = d / "youtube-video-te.mp4"
    if not te.exists():
        print(f"Telugu video not found: {te}\nRun: python automation/tts_sarvam.py {ep} te\n     python automation/assemble_dual.py {ep}")
        return
    sz = te.stat().st_size / 1e6
    print(f"""
Telugu video ready: {te} ({sz:.1f} MB)

To add as a second language track in YouTube Studio:
  1. Open https://studio.youtube.com
  2. Click the video -> Dubbing (or Audio tracks)
  3. Click "Add language" and choose Telugu
  4. Upload: {te.name}
  5. Save

Viewers will then see a language selector (gear icon) while watching.
""")

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "episode-002")
