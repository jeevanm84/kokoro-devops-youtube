"""Shared configuration for the production pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FPS = 30
MAIN_RES = (1920, 1080)
SHORT_RES = (1080, 1920)
THUMB_RES = (1280, 720)
LEAD_S, GAP_S, TAIL_S = 0.5, 0.35, 0.6      # silence around narration, seconds
KOKORO_MODEL = ROOT / "assets/models/kokoro-v1.0.onnx"
KOKORO_VOICES = ROOT / "assets/models/voices-v1.0.bin"
CACHE = ROOT / ".cache"

def ep_dir(ep: str) -> Path:
    return ROOT / "episodes" / ep

def build_dir(ep: str) -> Path:
    d = ep_dir(ep) / "build"
    d.mkdir(parents=True, exist_ok=True)
    return d
