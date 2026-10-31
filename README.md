# Kokoro DevOps - YouTube content & production pipeline
**Kokoro DevOps** (@KokoroDevOps) - *GenAI · FDE · Cloud Ops*. Animated, scenario-based developer education, built on the labs in [github.com/jeevanm84](https://github.com/jeevanm84).

## What is here
| Path | Contents |
|---|---|
| `automation/` | Checkpointed production pipeline: validate -> TTS -> subtitles -> render (Manim) -> assemble -> Short -> thumbnail -> metadata -> QA |
| `templates/brand.py`, `channel.json`, `assets/branding/` | Brand kit (palette sampled from the logo), single-source channel name/handle |
| `episodes/episode-001/` | Python execution episode: script, validated facts, animations, subtitles, thumbnail, metadata, QA report |
| `episodes/episode-002/` | Git undo (reset/revert/restore/reflog): script, storyboard, verified command outputs |
| `courses/git-docker-interview/` | Interview-scenario bank: 13 Git scenarios (all executed by `verify_git.py`), 15 Docker scenarios (NOT executed - run the labs yourself) |
| `upload-kit/` | Titles, descriptions, tags, thumbnails, channel avatar/banner, upload checklist, content calendar |
| `docs/` | Branding, costs, licences, YouTube <-> GitHub cross-linking plan |

## Quick start
```
pip install -r requirements.txt            # + ffmpeg, libcairo2-dev, libpango1.0-dev, fonts-dejavu-core
sh automation/setup_models.sh              # Kokoro TTS model (~350 MB), not stored in git
python automation/pipeline.py run episode-001
python automation/rebrand.py "Kokoro DevOps" --handle @KokoroDevOps
```
Python **3.12** required.

## Rules this repo follows
- **No secrets, no media in git.** Videos and audio are build outputs (`*.mp4`, `*.wav` are git-ignored); publish them to YouTube / Releases.
- **Nothing is called done unless verified.** QA is automated (`qa-report.md`); human-review items are marked MANUAL. Docker content is explicitly unverified until run on real Docker.
- Everything stays **Private** on YouTube until a human approves.

## Status
Episodes 001 and 002 rendered and QA-passed (automated checks; human review items remain MANUAL). Weekly automation, S3 storage and YouTube upload are **not built**; `.github/workflows/produce-episode.yml` has never run in CI.
