"""Metadata stage: YouTube title/description/tags/chapters from script + real scene timings. Always private until human approval."""
import json, sys
from config import *

SOURCES = [
    ("Python docs: dis — Disassembler for Python bytecode", "https://docs.python.org/3/library/dis.html"),
    ("Python docs: Data model (objects, values, types)", "https://docs.python.org/3/reference/datamodel.html"),
    ("Python docs: gc — Garbage Collector interface", "https://docs.python.org/3/library/gc.html"),
    ("PEP 3147 — PYC repository directories (__pycache__)", "https://peps.python.org/pep-3147/"),
    ("PEP 617 — New PEG parser for CPython", "https://peps.python.org/pep-0617/"),
    ("What's New in Python 3.11 — Faster CPython", "https://docs.python.org/3/whatsnew/3.11.html"),
    ("PEP 659 — Specializing Adaptive Interpreter", "https://peps.python.org/pep-0659/"),
]

def mmss(s): return f"{int(s // 60)}:{int(s % 60):02d}"

def run(ep):
    sc = json.load(open(ep_dir(ep) / "script.json")); tm = json.load(open(build_dir(ep) / "timing.json"))
    t, chapters = 0.0, []
    for s in sc["scenes"]:
        chapters.append((t, s["chapter"])); t += tm[s["id"]]["duration"]
    chap = "\n".join(f"{mmss(a)} {b}" for a, b in chapters)
    desc = f"""Is Python interpreted or compiled? Both. This video shows, step by step, what CPython does between pressing Enter and seeing output: tokenizing, parsing to an AST, compiling to bytecode, executing on a stack-based virtual machine, how names bind to objects (reference counting), and how call frames build the call stack.

Everything shown was checked against a real CPython 3.12 interpreter. Details differ in other implementations (e.g. PyPy) and versions.

CHAPTERS
{chap}

SOURCES
""" + "\n".join(f"- {a}: {b}" for a, b in SOURCES) + """

Narration is an AI-generated voice. Animations are original, built programmatically with Manim.

#Python #Programming #CPython"""
    tags = ["python", "how python works", "cpython", "python bytecode", "python interpreter", "python virtual machine", "dis module",
            "python internals", "python reference counting", "python call stack", "python for beginners", "python explained", "abstract syntax tree",
            "interpreted vs compiled", "software engineering"]
    short_desc = ("Is Python interpreted or compiled? Both: CPython compiles source to bytecode, then a virtual machine executes it on a stack. "
                  "Full visual walkthrough on the channel.\n\n#Shorts #Python #Programming")
    meta = {
        "episode": ep, "privacyStatus": "private", "approvalRequired": True,
        "main": {"title": sc["title"], "description": desc, "tags": tags, "categoryId": "27", "defaultLanguage": "en",
                 "defaultAudioLanguage": "en", "selfDeclaredMadeForKids": False,
                 "files": {"video": "youtube-video.mp4", "thumbnail": "thumbnail.png", "captions": "subtitles/youtube-video.en.srt"},
                 "chapters": [{"start": round(a, 2), "title": b} for a, b in chapters]},
        "short": {"title": "Python: interpreted or compiled? Both. #Shorts", "description": short_desc, "tags": ["python", "shorts", "bytecode", "programming"],
                  "categoryId": "27", "defaultLanguage": "en", "selfDeclaredMadeForKids": False,
                  "files": {"video": "youtube-short.mp4", "captions": "subtitles/youtube-short.en.srt"}},
        "sources": [{"title": a, "url": b} for a, b in SOURCES],
        "disclosures": ["AI-generated narration voice (Kokoro TTS, Apache-2.0 model); review YouTube's current altered/synthetic-content disclosure rules before publishing."],
    }
    assert len(meta["main"]["title"]) <= 100 and len(meta["main"]["description"]) <= 5000 and sum(len(x) + 1 for x in tags) <= 500
    assert chapters[0][0] == 0 and len(chapters) >= 3 and all(chapters[i + 1][0] - chapters[i][0] >= 10 for i in range(len(chapters) - 1))
    json.dump(meta, open(ep_dir(ep) / "metadata.json", "w"), indent=2, ensure_ascii=False)
    print(f"[metadata] ok: title {len(meta['main']['title'])} chars, {len(chapters)} chapters, {len(tags)} tags")

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "episode-001")
