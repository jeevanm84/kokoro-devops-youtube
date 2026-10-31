# QA report — episode-002

**Result: PASS (automated checks) — manual items remain**

## Technical accuracy

| Status | Check | Detail |
|---|---|---|
| PASS | all on-screen claims executed against the real tool (CPython or Git) | 10 checks |

## Main video

| Status | Check | Detail |
|---|---|---|
| PASS | file exists | /home/claude/youtube-production/episodes/episode-002/youtube-video.mp4 |
| PASS | H.264 / yuv420p | h264 yuv420p |
| PASS | 1920x1080, 16:9, square pixels | 1920x1080 sar=None |
| PASS | duration within 5-8 min | 317.0s = 5.28 min |
| PASS | audio AAC present | aac 48000Hz |
| PASS | A/V duration match (<=0.15s) | v=316.933333 a=316.949000 |
| PASS | no missing frames (packets vs expected) | 9508 vs 9508.0 @ 30fps |
| PASS | no black frames | [] |
| PASS | loudness -18..-14 LUFS | -16.0 LUFS |
| PASS | no clipping (peak <= -1 dB) | max -1.5 dB |
| PASS | no dead-air > 2.5 s | [] |
| PASS | embedded subtitle track |  |
| PASS | file size sane (<2 GB) | 15.6 MB |

## Subtitles

| Status | Check | Detail |
|---|---|---|
| PASS | ordered, non-overlapping |  |
| PASS | ends within video | last end 316.96s |
| PASS | <=2 lines, <=42 chars/line | 93 cues |
| PASS | reading speed <= 21 cps | max 19.8, mean 15.8 |
| PASS | min cue duration >= 0.7 s | min 1.07s |

## Sync & narration

| Status | Check | Detail |
|---|---|---|
| PASS | every animation cue lands within 0.5 s of its word | worst lateness 0.00s |
| PASS | scene render time == audio time | all scenes ±1 frame |
| PASS | effective pace 120-155 wpm (incl. pauses) | 152 wpm effective, 164 wpm while speaking (803 words) |

## Short

| Status | Check | Detail |
|---|---|---|
| PASS | file exists |  |
| PASS | 1080x1920 9:16 H.264 |  |
| PASS | duration 30-60 s | 32.2s |
| PASS | A/V match (<=0.15s) |  |
| PASS | loudness -18..-14 LUFS, no clipping | -16.1 LUFS, max -1.5 dB |
| PASS | captions burned in (white text in caption band) | ['0.030', '0.036', '0.022'] |

## Thumbnail

| Status | Check | Detail |
|---|---|---|
| PASS | 1280x720, PNG, < 2 MB | (1280, 720) 102 KB |
| PASS | high contrast (luma p95-p5 > 0.55) | 0.57 |
| MANUAL | visual review of thumbnail at small size |  |

## Needs human review

| Status | Check | Detail |
|---|---|---|
| MANUAL | narration clarity / pronunciation (listen once) | AI voice; automated checks cover levels and timing only |
| MANUAL | licensing (fonts DejaVu, Manim MIT, Kokoro Apache-2.0, no third-party media) | documented in docs/ASSETS-LICENSES.md; not machine-verified |
| MANUAL | text readability on mobile | frames reviewed by the producing agent; confirm on a phone |
| MANUAL | documented claims (PyPy JIT, 3.11 specializing interpreter) | cited in description sources |
