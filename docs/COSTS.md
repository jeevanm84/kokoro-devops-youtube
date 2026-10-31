# Costs (Episode 001 — measured, not quoted)
No provider prices were looked up; none are claimed. What was actually measured in the build sandbox (1 vCPU, 3.9 GB RAM):
| Stage | Measured | Paid service? |
|---|---|---|
| Narration (Kokoro, local CPU) | ~0.9–1.4× real-time → ~6–8 min for the 5.2 min episode (first run; cached afterwards) | No |
| Scene render, Manim 1080p30 | ~16–39 s per scene, ~5 min total for 10 scenes + Short | No |
| Assembly + loudness + Short encode | ~1–2 min | No |
| Model download (one-time) | 325 MB + 28 MB from GitHub releases | No |
| Output size | main 16.4 MB, Short ≈ small, thumbnail 139 KB | — |
**Marginal cash cost per episode today: $0** apart from CI minutes if run on GitHub Actions (free quota depends on your plan and repo visibility — check GitHub's current pricing).
Future paid items (verify current pricing before enabling): Claude API for topic/script generation (token-based), cloud TTS if you replace Kokoro, S3 storage/egress, any larger CI runner.
