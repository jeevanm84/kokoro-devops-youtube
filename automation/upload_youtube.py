"""Upload an episode (main video + Short) to YouTube as PRIVATE, with title, description, tags, thumbnail and captions.

    python automation/upload_youtube.py episode-002 --dry-run     # validate everything, upload nothing
    python automation/upload_youtube.py episode-002               # upload main + short (skips anything already uploaded)
    python automation/upload_youtube.py episode-002 --only main   # or --only short

Safety: privacyStatus is hard-coded to "private"; publishing stays a manual, human step in YouTube Studio.
Idempotent: uploaded video IDs are recorded in episodes/<ep>/upload-state.json; re-runs skip them (use --force to override).
Credentials live OUTSIDE the repo: ~/.config/kokoro-devops/client_secret.json (OAuth desktop client) and token.json.
Reads episodes/<ep>/metadata.json. Video files are build outputs (not in git): put youtube-video.mp4 / youtube-short.mp4 in the episode folder.
"""
import argparse, json, os, pathlib, random, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = pathlib.Path(os.environ.get("KOKORO_CONFIG_DIR", pathlib.Path.home() / ".config" / "kokoro-devops"))
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
RETRY_STATUS = {500, 502, 503, 504}

def validate(ep_dir, item, meta):
    errs, f = [], meta["files"]
    for key in ("video", "thumbnail", "captions"):
        if key in f and not (ep_dir / f[key]).exists():
            errs.append(f"missing {key}: {ep_dir / f[key]}" + ("  (videos are not in git: copy the MP4 here)" if key == "video" else ""))
    if len(meta["title"]) > 100: errs.append(f"title > 100 chars ({len(meta['title'])})")
    if len(meta["description"]) > 5000: errs.append("description > 5000 chars")
    if sum(len(t) + 1 for t in meta.get("tags", [])) > 500: errs.append("tags > 500 chars total")
    if any(c in meta["title"] for c in "<>") or any(c in meta["description"] for c in "<>"): errs.append("YouTube rejects < and > in title/description")
    v = ep_dir / f.get("video", "_")
    if v.exists() and v.stat().st_size == 0: errs.append("video file is empty")
    return errs

def service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    tok, sec = CFG / "token.json", CFG / "client_secret.json"
    creds = Credentials.from_authorized_user_file(str(tok), SCOPES) if tok.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try: creds.refresh(Request())
        except Exception as e:
            print(f"[auth] refresh failed ({e.__class__.__name__}); signing in again"); creds = None
    if (not creds or not creds.valid) and os.environ.get("CI"):
        sys.exit("[auth] No valid YouTube token in CI. Re-authorise on your Mac (upload_youtube.py --auth-only) and update the YT_TOKEN_JSON secret.")
    if not creds or not creds.valid:
        if not sec.exists(): sys.exit(f"[auth] {sec} not found. See docs/YOUTUBE-UPLOAD-SETUP.md")
        creds = InstalledAppFlow.from_client_secrets_file(str(sec), SCOPES).run_local_server(port=0)
        CFG.mkdir(parents=True, exist_ok=True); tok.write_text(creds.to_json()); os.chmod(tok, 0o600)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)

def resumable(request, label):
    from googleapiclient.errors import HttpError
    resp, attempt = None, 0
    while resp is None:
        try:
            status, resp = request.next_chunk()
            if status: print(f"[{label}] {int(status.progress() * 100)}%", flush=True)
        except HttpError as e:
            reason = e.error_details[0].get("reason") if getattr(e, "error_details", None) else ""
            if e.resp.status == 403 and reason in ("quotaExceeded", "uploadLimitExceeded"):
                sys.exit(f"[{label}] YouTube says {reason}. Stop and retry tomorrow; nothing is duplicated.")
            if e.resp.status not in RETRY_STATUS or attempt >= 6: raise
            attempt += 1; wait = min(2 ** attempt + random.random(), 60); print(f"[{label}] HTTP {e.resp.status}, retry in {wait:.0f}s"); time.sleep(wait)
        except (ConnectionError, TimeoutError, OSError) as e:
            if attempt >= 6: raise
            attempt += 1; wait = min(2 ** attempt + random.random(), 60); print(f"[{label}] {e.__class__.__name__}, retry in {wait:.0f}s"); time.sleep(wait)
    return resp

def upload(yt, ep_dir, item, meta):
    from googleapiclient.http import MediaFileUpload
    f = meta["files"]
    body = {"snippet": {"title": meta["title"], "description": meta["description"], "tags": meta.get("tags", []),
                        "categoryId": meta.get("categoryId", "27"), "defaultLanguage": meta.get("defaultLanguage", "en"),
                        "defaultAudioLanguage": meta.get("defaultAudioLanguage", "en")},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": bool(meta.get("selfDeclaredMadeForKids", False))}}
    assert body["status"]["privacyStatus"] == "private"
    req = yt.videos().insert(part="snippet,status", body=body, notifySubscribers=False,
                             media_body=MediaFileUpload(str(ep_dir / f["video"]), chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4"))
    vid = resumable(req, item)["id"]
    print(f"[{item}] uploaded PRIVATE: https://youtu.be/{vid}  (Studio: https://studio.youtube.com/video/{vid}/edit)")
    return vid

def extras(yt, ep_dir, item, meta, vid, state):
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    f = meta["files"]
    if "thumbnail" in f and not state.get("thumbnail"):
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(ep_dir / f["thumbnail"]), mimetype="image/png")).execute()
            state["thumbnail"] = True; print(f"[{item}] thumbnail set")
        except HttpError as e:
            print(f"[{item}] thumbnail NOT set (HTTP {e.resp.status}). Custom thumbnails need a phone-verified channel; set it in Studio.")
    if "captions" in f and not state.get("captions"):
        try:
            yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "en", "name": "English", "isDraft": False}},
                                 media_body=MediaFileUpload(str(ep_dir / f["captions"]), mimetype="application/octet-stream")).execute()
            state["captions"] = True; print(f"[{item}] English captions added")
        except HttpError as e:
            print(f"[{item}] captions NOT added (HTTP {e.resp.status}); upload the .srt in Studio > Subtitles.")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("episode", nargs="?", default=""); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", choices=["main", "short"]); ap.add_argument("--force", action="store_true"); ap.add_argument("--auth-only", action="store_true", help="sign in, save token, upload nothing")
    a = ap.parse_args()
    if a.auth_only:
        service(); print(f"[auth] token saved to {CFG / 'token.json'}"); return
    a.episode = pathlib.Path(a.episode.rstrip("/")).name          # accept "episode-001" or "episodes/episode-001"
    ep_dir = ROOT / "episodes" / a.episode
    if not (ep_dir / "metadata.json").exists():
        found = sorted(p.parent.name for p in (ROOT / "episodes").glob("*/metadata.json"))
        sys.exit(f"No metadata.json for '{a.episode}'. Use an episode name, e.g.: python3 automation/upload_youtube.py {found[0] if found else 'episode-001'} --dry-run  (available: {', '.join(found)})")
    meta = json.load(open(ep_dir / "metadata.json"))
    sp = ep_dir / "upload-state.json"; state = json.load(open(sp)) if sp.exists() else {}
    items = [a.only] if a.only else ["main", "short"]
    bad = {i: validate(ep_dir, i, meta[i]) for i in items if i in meta}
    for i, errs in bad.items():
        print(f"[check] {i}: " + ("OK" if not errs else "; ".join(errs)))
    if any(bad.values()): sys.exit(1)
    if a.dry_run:
        for i in items:
            m = meta[i]; print(f"[dry-run] {i}: would upload PRIVATE '{m['title']}' ({(ep_dir / m['files']['video']).stat().st_size / 1e6:.1f} MB), "
                                f"{len(m.get('tags', []))} tags, thumbnail={'thumbnail' in m['files']}, captions={'captions' in m['files']}; "
                                + (f"already uploaded as {state[i]['id']} -> would SKIP" if i in state and state[i].get("id") and not a.force else "not yet uploaded"))
        return
    yt = service()
    for i in items:
        st = state.setdefault(i, {})
        if st.get("id") and not a.force:
            alive = yt.videos().list(part="id", id=st["id"]).execute().get("items")
            if alive: print(f"[{i}] already uploaded as {st['id']} -> skipping video upload")
            else: print(f"[{i}] recorded video {st['id']} no longer exists -> uploading again"); st.clear()
        if not st.get("id"):
            st["id"] = upload(yt, ep_dir, i, meta[i]); json.dump(state, open(sp, "w"), indent=2)   # save immediately: no duplicates on retry
        extras(yt, ep_dir, i, meta[i], st["id"], st); json.dump(state, open(sp, "w"), indent=2)
    print("Done. Everything is PRIVATE. Review in YouTube Studio, answer the 'altered content' question there, then publish manually.")

if __name__ == "__main__":
    main()
