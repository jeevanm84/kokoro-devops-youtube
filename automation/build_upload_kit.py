"""Build the human-ready upload kit in upload-kit/. Re-run after rebranding. Nothing here uploads anything."""
import importlib.util, json, shutil, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from config import *
import thumbnail

ep = sys.argv[1] if len(sys.argv) > 1 else "episode-001"
cfg = json.load(open(ROOT / "channel.json")); NAME = cfg["name"]; TAG = cfg["tagline"]
E = ep_dir(ep); meta = json.load(open(E / "metadata.json")); K = ROOT / "upload-kit"
for d in ("episode-001", "short", "channel"): (K / d).mkdir(parents=True, exist_ok=True)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
spec = importlib.util.spec_from_file_location("facts", E / "facts.py"); F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
w = lambda p, t: (K / p).write_text(t.strip() + "\n")

# ---------- episode text ----------
m = meta["main"]; desc = m["description"].replace("\n\n#Python", f"\n\nNew visual explainers on how software really works - subscribe to {NAME}.\n\n#Python", 1)
w("episode-001/01-title-options.txt", f"""PRIMARY (use this):
{m['title']}

ALTERNATIVES to A/B test via YouTube 'Test & compare' if available on your channel (all honest, none clickbait):
- Python: Compiled or Interpreted? Both. Here's the Proof (Visual Guide)
- What Really Happens When You Run a Python File? (Bytecode, VM, Stack)
- Python Under the Hood: Bytecode, the VM and the Call Stack Explained
Limit: 100 characters. Keep the primary keyword (Python) in the first 40 characters.""")
w("episode-001/02-description.txt", desc)
w("episode-001/03-tags.txt", ", ".join(m["tags"]) + "\n\n(Tags matter little; the title, thumbnail and first 2 description lines matter most.)")
w("episode-001/04-pinned-comment.txt", f"""Which would you like visualized next - Docker containers, Kubernetes, CI/CD pipelines or load balancers? Reply with one word. 👇
(Everything in this video was checked against a real CPython 3.12 interpreter. Spotted a mistake? Tell me with the timestamp and I'll pin the correction.)
- {NAME}""")
w("episode-001/05-short-title-description.txt", f"TITLE: {meta['short']['title']}\n\nDESCRIPTION:\n{meta['short']['description']}\n\nFull video: <paste the main video link after it is uploaded>")
w("episode-001/06-description-te-DRAFT.txt", """TELUGU DESCRIPTION - DRAFT, MUST BE REVIEWED BY A NATIVE TELUGU SPEAKER BEFORE USE.
(The video narration is in English; this line helps Telugu viewers understand what they are clicking.)

పైథాన్ మీ కోడ్‌ను నిజంగా ఎలా రన్ చేస్తుంది? Interpreted ఆ, compiled ఆ? రెండూ! ఈ వీడియోలో tokenizer నుండి bytecode, virtual machine, call stack వరకు యానిమేషన్లతో చూద్దాం.
(వీడియో ఇంగ్లీష్‌లో ఉంది. ఇంగ్లీష్ సబ్‌టైటిల్స్ అందుబాటులో ఉన్నాయి.)""")
w("episode-001/07-community-post.txt", f"""NEW VIDEO (post after the video goes public):
How does Python REALLY run your code? Not "interpreted" or "compiled" - both. Watch the bytecode, the stack machine and the call stack come alive. ▶ <link>

POLL (post 2-3 days later) - 'What should we visualize next?': Docker containers / Kubernetes / CI-CD pipeline / Load balancer""")
shutil.copy(E / "subtitles/youtube-video.en.srt", K / "episode-001/youtube-video.en.srt"); shutil.copy(E / "subtitles/youtube-short.en.srt", K / "short/youtube-short.en.srt")
if cfg.get("status") == "FINAL":                       # only ship videos that carry the final channel name
    shutil.copy(E / "youtube-video.mp4", K / "episode-001/youtube-video.mp4"); shutil.copy(E / "youtube-short.mp4", K / "short/youtube-short.mp4")
    (K / "VIDEOS-NOT-READY.txt").unlink(missing_ok=True)
else:
    for p in (K / "episode-001/youtube-video.mp4", K / "short/youtube-short.mp4"): p.unlink(missing_ok=True)
    (K / "VIDEOS-NOT-READY.txt").write_text("Videos are intentionally NOT in this kit yet: the draft videos carry a watermark with an old/draft channel name.\nChoose the final name, then run:  python automation/rebrand.py \"Final Name\"\nThat re-renders (~5 min), re-runs QA and copies the final MP4s here.\n")
thumbnail.make(K / "episode-001/thumbnail-A.png", F.ROWS, NAME, "A"); thumbnail.make(K / "episode-001/thumbnail-B.png", F.ROWS, NAME, "B")

# ---------- channel art ----------
def fit_font(draw, text, path, max_w, start):
    s = start
    while s > 20 and draw.textlength(text, font=ImageFont.truetype(path, s)) > max_w: s -= 4
    return ImageFont.truetype(path, s)
def gradient(W, H):
    img = Image.new("RGB", (W, H)); px = img.load()
    for y in range(H):
        t = y / H
        for x in range(W): px[x, y] = tuple(int(a * (1 - t) + b * t) for a, b in zip((11, 18, 32), (22, 36, 66)))
    return img
# avatar + banner from the user's own lockup (assets/branding/lockup-dark.png, 2400x800): icon bbox (556,260,919,524), full bbox (556,190,1871,639)
LK = Image.open(ROOT / "assets/branding/lockup-dark.png").convert("RGB"); BGC = (11, 18, 32)
icon = LK.crop((556, 260, 919, 524)); av = Image.new("RGB", (800, 800), BGC)
icon = icon.resize((520, int(520 * icon.height / icon.width)), Image.LANCZOS); av.paste(icon, ((800 - icon.width) // 2, (800 - icon.height) // 2)); av.save(K / "channel/avatar-800.png")
full = LK.crop((556, 190, 1871, 639)); full = full.resize((1230, int(1230 * full.height / full.width)), Image.LANCZOS)   # fits YouTube's 1546x423 safe area
bn = Image.new("RGB", (2560, 1440), BGC); bn.paste(full, ((2560 - full.width) // 2, (1440 - full.height) // 2)); bn.save(K / "channel/banner-2560x1440.png")
w("channel/about-text.txt", f"""CHANNEL NAME: {NAME}   (handle: {cfg.get('handle') or '<choose after checking availability>'})
TAGLINE: {TAG}

ABOUT (paste into YouTube Studio > Customization > Basic info):
{NAME} turns software internals into clear animations and hands-on labs: Git, Docker, Kubernetes, CI/CD, cloud operations, GenAI and forward-deployed engineering (FDE). New visual explainer every week, for developers, DevOps and SRE engineers, and anyone preparing for technical interviews.
Every technical claim is checked before publishing. Narration is AI-generated.
Business/contact: <your email>

CHANNEL KEYWORDS: kokoro devops, genai, forward deployed engineer, fde, cloud ops, python, devops, kubernetes, docker, aws, system design, sre, ci cd, software engineering, explained visually
DEFAULTS: category Education - Visibility Private until reviewed - Language English - Made for kids: NO""")
w("UPLOAD-CHECKLIST.md", f"""# Upload checklist - Episode 001 (everything stays PRIVATE until you approve)
Prereq: final channel name chosen -> `python automation/rebrand.py "<Name>"` (re-renders the watermark, thumbnails, art, text). Do NOT upload before this.
1. Studio > Customization: upload `channel/avatar-800.png`, `channel/banner-2560x1440.png`, paste `channel/about-text.txt`.
2. Create upload > select `episode-001/youtube-video.mp4`. Title: 01-title-options.txt. Description: 02. Tags (More options): 03.
3. Thumbnail: upload thumbnail-A.png (keep B for a later test).
4. Audience: **Not made for kids**. Category: Education. Language: English. Captions: upload `youtube-video.en.srt` (English). 
5. 'Altered content' question: answer per YouTube's CURRENT wording. This video uses an AI narration voice; it depicts no real person or event, but read the prompt and decide.
6. Playlist: create "Python Internals". Add end screen (last 20 s) + one card pointing to the Short.
7. Visibility: **Private**. Watch it once inside Studio (check captions render, chapters appear = description has 0:00 chapter list).
8. When happy: set Public or schedule. Suggested first test slot: weekday evening IST; verify with Analytics after 3-4 videos.
9. After public: pin comment (04), post community note (07), upload the Short (05 + short/youtube-short.mp4) and link the long video.
10. First 48 hours: reply to every comment; note average view duration and where viewers drop (Analytics > Engagement).
Do NOT: buy views/subs, use misleading titles, or publish before the human-review items in qa-report.md are done.""")
w("CONTENT-CALENDAR.md", f"""# Next 8 episodes (DevOps-first to match {NAME}; reuse the same pipeline & visual language)
| # | Title (working) | Hook | Key visuals |
|---|---|---|---|
| 1 | How Python Actually Executes Your Code | Interpreted or compiled? Both | bytecode, stack machine, frames - DONE |
| 2 | How Docker Containers Actually Work | A container is just a process - proof | namespaces, cgroups, layered filesystem |
| 3 | What Happens When You Run kubectl apply | From YAML to a running Pod | API server, etcd, scheduler, kubelet |
| 4 | Inside a CI/CD Pipeline | Commit to production in 8 steps | stages, artifacts, rollbacks |
| 5 | Load Balancers Explained: L4 vs L7 | One URL, many servers | request routing, health checks |
| 6 | Terraform: Plan, State and Apply | Why state files break teams | graph, drift, locking |
| 7 | How a Request Travels Through an AWS VPC | Packet journey | subnets, route tables, NAT, SG vs NACL |
| 8 | Observability: Metrics, Logs, Traces | Why dashboards lie | Prometheus scrape, sampling |
Rule: each episode = 1 question hook, 1 animated mechanism, 1 real-world failure story, validated by running real code/commands.
Make each script clearly original and distinct (YouTube's policy on mass-produced, repetitive content): vary structure, add your own real incident lessons.""")
print("kit built ->", K)
