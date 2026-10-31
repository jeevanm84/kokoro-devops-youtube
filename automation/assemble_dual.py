"""
Assemble a video with two audio tracks (English + Telugu).
YouTube's multi-language audio upload only supports one audio stream per video file,
so we produce:
  - youtube-video-en.mp4   (English audio — main upload)
  - youtube-video-te.mp4   (Telugu audio — upload as additional language track in Studio)
  - youtube-short-te.mp4   (Telugu Short)
Both are timed to the LONGER language per scene so animations stay in sync.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

def ep_dir(ep): return ROOT / "episodes" / ep

def make_video(video_src, audio_src, out, subtitles=None):
    # All -i inputs must come before -map/-c flags in ffmpeg
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-i", str(video_src), "-i", str(audio_src)]
    if subtitles:
        cmd += ["-i", str(subtitles)]
    cmd += ["-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k"]
    if subtitles:
        cmd += ["-map", "2", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng"]
    cmd.append(str(out))
    subprocess.run(cmd, check=True)

def run(ep):
    d = ep_dir(ep)
    audio_dir = d / "build" / "audio_tracks"
    en_audio = d / "build" / "audio" / "main.wav"   # existing English track
    te_audio = audio_dir / "te.wav"

    if not te_audio.exists():
        print(f"[dual] Telugu track not found at {te_audio}. Run tts_sarvam.py first.")
        return False

    # English version (main upload, existing pipeline output)
    main_mp4 = d / "youtube-video.mp4"
    en_out = d / "youtube-video-en.mp4"
    if main_mp4.exists():
        import shutil; shutil.copy(main_mp4, en_out)
        print(f"[dual] EN video: {en_out}")

    # Telugu version
    te_out = d / "youtube-video-te.mp4"
    subs = d / "subtitles" / "youtube-video.en.srt"
    make_video(main_mp4, te_audio, te_out, subs if subs.exists() else None)
    print(f"[dual] TE video: {te_out}")

    # Telugu Short
    short_mp4 = d / "youtube-short.mp4"
    te_short_audio = audio_dir / "te_short.wav"
    if short_mp4.exists() and te_short_audio.exists():
        te_short_out = d / "youtube-short-te.mp4"
        make_video(short_mp4, te_short_audio, te_short_out)
        print(f"[dual] TE short: {te_short_out}")

    return True

if __name__ == "__main__":
    ep = sys.argv[1] if len(sys.argv) > 1 else "episode-002"
    run(ep)
