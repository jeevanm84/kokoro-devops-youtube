"""
Sarvam Bulbul TTS — generates audio for one language track.
Called by pipeline.py when script.json has a tts_te block.
Needs SARVAM_API_KEY in env (GitHub secret or local export).

Usage:
    python automation/tts_sarvam.py episode-002 te    # Telugu track
    python automation/tts_sarvam.py episode-002 en    # English track via Sarvam
"""
import json, os, pathlib, sys, hashlib, numpy as np, soundfile as sf, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SR = 24000

def ep_dir(ep): return ROOT / "episodes" / ep

def get_client():
    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        sys.exit("[sarvam] SARVAM_API_KEY not set. Export it or add as GitHub secret.")
    from sarvamai import SarvamAI
    return SarvamAI(api_subscription_key=key)

def synth_sentence(client, text, cfg, cache_dir):
    h = hashlib.sha256((json.dumps(cfg, sort_keys=True) + "|" + text).encode()).hexdigest()[:20]
    f = cache_dir / f"{h}.wav"
    if f.exists():
        a, _ = sf.read(f); return a.astype(np.float32)
    from sarvamai.play import save
    r = client.text_to_speech.convert(
        text=text, language_code=cfg["language"], speaker=cfg.get("speaker", "Manan"),
        model=cfg.get("model", "bulbul:v3"), pace=cfg.get("pace", 0.95),
        speech_sample_rate=SR, output_audio_codec="wav")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        save(r, tmp.name)
        a, sr = sf.read(tmp.name)
    os.unlink(tmp.name)
    if a.ndim > 1: a = a.mean(axis=1)
    if sr != SR:
        import resampy; a = resampy.resample(a, sr, SR)
    a = a.astype(np.float32)
    sf.write(f, a, SR); return a

def silence(secs): return np.zeros(int(SR * secs), dtype=np.float32)

def build_track(script, lang, client, cache_dir):
    """Build full audio track for one language. Returns (audio_array, timings_dict)."""
    cfg = script["tts_te"] if lang == "te" else script.get("tts", {"provider": "kokoro"})
    sentences_key = "sentences_te" if lang == "te" else "sentences"
    timings = {}; full = silence(0.3)

    for sc in script["scenes"]:
        sents = sc.get(sentences_key, sc["sentences"])  # fallback to English
        scene_start = len(full) / SR
        sent_times = []; t = scene_start
        clips = []
        for sent in sents:
            a = synth_sentence(client, sent, cfg, cache_dir)
            sent_times.append({"text": sent, "start": t, "end": t + len(a)/SR})
            t += len(a)/SR + 0.18
            clips.append(a); clips.append(silence(0.18))
        clips.append(silence(0.35))
        chunk = np.concatenate(clips)
        timings[sc["id"]] = {"start": scene_start, "duration": len(chunk)/SR, "sentences": sent_times}
        full = np.concatenate([full, chunk])

    return full, timings

def loudnorm(wav_in, wav_out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_in,
                    "-af", "loudnorm=I=-16:TP=-1.5", wav_out], check=True)

def run(ep, lang="te"):
    d = ep_dir(ep); script = json.load(open(d / "script.json"))
    cache = ROOT / ".cache" / "tts_sarvam"; cache.mkdir(parents=True, exist_ok=True)
    out_dir = d / "build" / "audio_tracks"; out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[sarvam] generating {lang} track for {ep}...")
    client = get_client()
    audio, timings = build_track(script, lang, client, cache)

    raw = out_dir / f"{lang}_raw.wav"; sf.write(raw, audio, SR)
    norm = out_dir / f"{lang}.wav"; loudnorm(str(raw), str(norm))
    raw.unlink()

    json.dump(timings, open(out_dir / f"{lang}_timing.json", "w"), indent=2, ensure_ascii=False)
    print(f"[sarvam] {lang} track done: {len(audio)/SR:.1f}s -> {norm}")
    return norm, timings

if __name__ == "__main__":
    ep = sys.argv[1] if len(sys.argv) > 1 else "episode-002"
    lang = sys.argv[2] if len(sys.argv) > 2 else "te"
    run(ep, lang)
