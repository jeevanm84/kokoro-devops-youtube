"""Assembly stage: concat scene videos, build loudness-normalised master audio, mux with soft subtitles (main)
and burn mobile captions (Short). Fails loudly on any duration mismatch instead of papering over it."""
import json, subprocess, sys
import numpy as np, soundfile as sf
from config import *

def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode: raise RuntimeError(f"{' '.join(map(str, cmd))[:200]}\n{r.stderr[-1500:]}")
    return r

def probe(path, entry="format=duration"):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", entry, "-of", "csv=p=0", str(path)]).stdout.strip().split(",")[0])

def master_audio(wavs, out):
    """Concat per-scene wavs (24 kHz) -> 48 kHz, two-pass EBU R128 normalise to -16 LUFS / -1.5 dBTP."""
    audio = np.concatenate([sf.read(w)[0].astype(np.float32) for w in wavs]); raw = out.with_suffix(".raw.wav")
    sf.write(raw, audio, 24000)
    m = sh(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"]).stderr
    j = json.loads(m[m.rindex("{"): m.rindex("}") + 1])
    af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000")
    sh(["ffmpeg", "-y", "-hide_banner", "-i", str(raw), "-af", af, "-ar", "48000", str(out)])
    raw.unlink()

def run_main(ep):
    script = json.load(open(ep_dir(ep) / "script.json")); timing = json.load(open(build_dir(ep) / "timing.json")); b = build_dir(ep)
    vids = []
    for sc in script["scenes"]:
        v = b / "scenes" / f"{sc['id']}.mp4"; d = probe(v)
        if abs(d - timing[sc["id"]]["duration"]) > 1.5 / FPS:
            raise RuntimeError(f"{sc['id']}: video {d:.3f}s != audio {timing[sc['id']]['duration']:.3f}s (re-render scene)")
        vids.append(v)
    lst = b / "concat.txt"; lst.write_text("".join(f"file '{v}'\n" for v in vids))
    sh(["ffmpeg", "-y", "-hide_banner", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(b / "video_silent.mp4")])
    master_audio([ep_dir(ep) / "voiceover" / f"{s['id']}.wav" for s in script["scenes"]], ep_dir(ep) / "voiceover" / "narration-master.wav")
    sh(["ffmpeg", "-y", "-hide_banner", "-i", str(b / "video_silent.mp4"), "-i", str(ep_dir(ep) / "voiceover/narration-master.wav"),
        "-i", str(ep_dir(ep) / "subtitles/youtube-video.en.srt"), "-map", "0:v", "-map", "1:a", "-map", "2:s",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
        "-metadata", f"title={script['title']}", "-movflags", "+faststart", "-shortest", str(ep_dir(ep) / "youtube-video.mp4")])
    print(f"[assemble] youtube-video.mp4 {probe(ep_dir(ep) / 'youtube-video.mp4'):.2f}s")

def run_short(ep):
    b = build_dir(ep); vo = ep_dir(ep) / "voiceover"; t = json.load(open(b / "timing.json"))["short"]
    v = b / "scenes" / "short.mp4"
    if abs(probe(v) - t["duration"]) > 1.5 / FPS: raise RuntimeError("short video/audio duration mismatch")
    master_audio([vo / "short.wav"], vo / "short-master.wav")
    ass = (b / "short.ass").as_posix().replace(":", r"\:")
    sh(["ffmpeg", "-y", "-hide_banner", "-i", str(v), "-i", str(vo / "short-master.wav"), "-vf", f"ass={ass}", "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-shortest", str(ep_dir(ep) / "youtube-short.mp4")])
    print(f"[short] youtube-short.mp4 {probe(ep_dir(ep) / 'youtube-short.mp4'):.2f}s")

if __name__ == "__main__":
    ep = sys.argv[2] if len(sys.argv) > 2 else "episode-001"
    run_main(ep) if sys.argv[1] == "main" else run_short(ep)
