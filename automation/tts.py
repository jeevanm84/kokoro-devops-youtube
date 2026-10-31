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
def _ok(a, text):
    wps = len(text.split()) / max(len(a) / SR, 1e-6)
    return np.isfinite(a).all() and len(a) and np.abs(a).max() <= 1.0 and 0.8 <= wps <= 4.5, wps

def _kokoro_synth(text, cfg):
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
    sp = cfg.get("speed", 1.0)
    for attempt, s_ in enumerate((sp, sp * 1.01, sp * 0.99)):       # retry on numerically bad output
        a, sr = _kokoro.create(text, voice=cfg["voice"], speed=s_, lang=cfg.get("lang", "en-us"))
        a = a.astype(np.float32); ok, wps = _ok(a, text)
        if ok: return a
        print(f"[tts] REJECTED clip (attempt {attempt}): wps={wps:.1f} :: {text[:40]}", flush=True)
    raise RuntimeError(f"TTS failed validation for: {text}")

def _sarvam_synth(text, cfg):
    """Sarvam Bulbul (sarvamai SDK). Needs SARVAM_API_KEY. Telugu must be in native script (Sarvam docs)."""
    import os, tempfile
    from sarvamai import SarvamAI
    from sarvamai.play import save
    key = os.environ.get("SARVAM_API_KEY")
    if not key: raise RuntimeError("SARVAM_API_KEY is not set (GitHub secret or local env)")
    client = SarvamAI(api_subscription_key=key)
    r = client.text_to_speech.convert(text=text, language_code=cfg.get("language", "en-IN"), speaker=cfg.get("speaker"),
                                      model=cfg.get("model", "bulbul:v3"), pace=cfg.get("pace", 1.0),
                                      speech_sample_rate=SR, output_audio_codec="wav")
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        save(r, f.name); a, sr = sf.read(f.name)
    if a.ndim > 1: a = a.mean(axis=1)
    if sr != SR: raise RuntimeError(f"Sarvam returned {sr} Hz, expected {SR}")
    a = a.astype(np.float32); ok, wps = _ok(a, text)
    if not ok: raise RuntimeError(f"Sarvam clip failed validation (wps={wps:.1f}): {text[:60]}")
    return a

def synth(text, cfg):
    key = hashlib.sha256((json.dumps(cfg, sort_keys=True) + "|" + text).encode()).hexdigest()[:20]
    f = CACHE / "tts" / f"{key}.wav"
    if f.exists():
        return sf.read(f)[0].astype(np.float32), True
    a = {"kokoro": _kokoro_synth, "sarvam": _sarvam_synth}[cfg.get("provider", "kokoro")](text, cfg)
    a = _trim(a)
    f.parent.mkdir(parents=True, exist_ok=True); sf.write(f, a, SR)
    return a, False

def voice_cfg(script):
    """script.json "tts" block wins; legacy top-level voice/speed means Kokoro."""
    return script.get("tts") or {"provider": "kokoro", "voice": script["voice"], "speed": script["speed"]}

def build_track(sentences, cfg):
    """Return (audio, [{'text','start','end'}], total_seconds), padded to a whole number of frames."""
    parts, cues, t = [], [], LEAD_S
    parts.append(np.zeros(int(LEAD_S * SR), np.float32))
    for i, s in enumerate(sentences):
        a, _ = synth(s, cfg)
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
        audio, cues, total = build_track(sc["sentences"], voice_cfg(script))
        sf.write(vo / f"{sc['id']}.wav", audio, SR)
        timing[sc["id"]] = {"duration": round(total, 4), "sentences": cues}
        print(f"[tts] {sc['id']}: {total:6.2f}s  ({len(cues)} sentences)", flush=True)
    json.dump(timing, open(build_dir(ep) / "timing.json", "w"), indent=2)
    main = sum(timing[s["id"]]["duration"] for s in script["scenes"])
    print(f"[tts] main total {main/60:.2f} min | short {timing['short']['duration']:.1f}s")

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "episode-001")
