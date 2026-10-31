"""Voiceover stage: per-sentence neural TTS (Kokoro, local, open-source) with content-hash caching.

Produces, per scene, a WAV with fixed lead/gap/tail silence, plus timing.json holding exact
sentence start/end times. Animations and subtitles both read this file, so sync is by construction.
TTS provider is behind `synth()` so a cloud voice (e.g. ElevenLabs/Polly) can be swapped in.
"""
import hashlib, json, sys
import numpy as np, soundfile as sf
from config import *

SR = 24000

def _trim(a, thr=0.008, keep=int(0.04 * SR)):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    return a[max(idx[0] - keep, 0): idx[-1] + keep]

_kokoro = None
def synth(text, voice, speed):
    global _kokoro
    key = hashlib.sha256(f"kokoro-v1.0-fp32|{voice}|{speed}|{text}".encode()).hexdigest()[:20]
    f = CACHE / "tts" / f"{key}.wav"
    if f.exists():
        return sf.read(f)[0].astype(np.float32), True
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
    a = None
    for attempt, sp in enumerate((speed, speed * 1.01, speed * 0.99)):      # retry on numerically bad output
        a, sr = _kokoro.create(text, voice=voice, speed=sp, lang="en-us")
        a = a.astype(np.float32)
        wps = len(text.split()) / max(len(a) / SR, 1e-6)
        if np.isfinite(a).all() and len(a) and np.abs(a).max() <= 1.0 and 0.8 <= wps <= 4.5:
            break
        print(f"[tts] REJECTED clip (attempt {attempt}): peak={np.abs(a).max() if len(a) else 'empty'} wps={wps:.1f} :: {text[:40]}", flush=True)
    else:
        raise RuntimeError(f"TTS failed validation for: {text}")
    assert sr == SR
    a = _trim(a)
    f.parent.mkdir(parents=True, exist_ok=True)
    sf.write(f, a, SR)
    return a, False

def build_track(sentences, voice, speed):
    """Return (audio, [{'text','start','end'}], total_seconds), padded to a whole number of frames."""
    parts, cues, t = [], [], LEAD_S
    parts.append(np.zeros(int(LEAD_S * SR), np.float32))
    for i, s in enumerate(sentences):
        a, _ = synth(s, voice, speed)
        d = len(a) / SR
        cues.append({"text": s, "start": round(t, 3), "end": round(t + d, 3)})
        parts.append(a)
        t += d
        if i < len(sentences) - 1:
            parts.append(np.zeros(int(GAP_S * SR), np.float32)); t += GAP_S
    parts.append(np.zeros(int(TAIL_S * SR), np.float32)); t += TAIL_S
    frames = int(np.ceil(t * FPS)); total = frames / FPS
    audio = np.concatenate(parts)
    audio = np.pad(audio, (0, max(int(round(total * SR)) - len(audio), 0)))[: int(round(total * SR))]
    return audio, cues, total

def run(ep):
    script = json.load(open(ep_dir(ep) / "script.json"))
    vo = ep_dir(ep) / "voiceover"; vo.mkdir(exist_ok=True)
    timing = {}
    for sc in script["scenes"] + [script["short"]]:
        audio, cues, total = build_track(sc["sentences"], script["voice"], script["speed"])
        sf.write(vo / f"{sc['id']}.wav", audio, SR)
        timing[sc["id"]] = {"duration": round(total, 4), "sentences": cues}
        print(f"[tts] {sc['id']}: {total:6.2f}s  ({len(cues)} sentences)", flush=True)
    json.dump(timing, open(build_dir(ep) / "timing.json", "w"), indent=2)
    main = sum(timing[s["id"]]["duration"] for s in script["scenes"])
    print(f"[tts] main total {main/60:.2f} min | short {timing['short']['duration']:.1f}s")

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "episode-001")
