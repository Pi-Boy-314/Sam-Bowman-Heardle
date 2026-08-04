#!/usr/bin/env python3
"""
Sam Bowman Heardle - Music Catalog Sync

Finds songs the artist has released that are not yet in music.json, matches each
one to a YouTube video, and (with --apply) adds them.

⚖️  LEGAL DISCLAIMER - READ BEFORE USE ⚖️

Same terms as the other tools in this folder: personal/educational use only.
Metadata comes from Deezer's public API; artwork stays as a link to Deezer's CDN
and is never downloaded or redistributed. You are responsible for complying with
the Deezer API Terms of Service and YouTube's Terms of Service.

────────────────────────────────────────────────────────────────────────────────

HOW IT WORKS

  1. Lists every release by the artist on Deezer (source of truth for "what
     exists"), newest first.
  2. Lists every video on the artist's YouTube channel in one pass. This is the
     important trick: per-track YouTube *search* is unreliable and frequently
     returns unrelated videos, but the channel listing is exact. Search is only
     used as a fallback for collabs hosted on a collaborator's channel.
  3. Matches Deezer tracks to YouTube videos by normalized title, requiring the
     durations to agree within DURATION_TOLERANCE seconds. A title that matches
     but whose duration does not is reported, never auto-applied.
  4. Prints a report. With --apply, appends confident matches to music.json.

Nothing is written without --apply.

USAGE

    python tools/sync_music.py                    # dry run: show what's new
    python tools/sync_music.py --since 2026-01-01 # only releases after a date
    python tools/sync_music.py --apply            # write new entries
    python tools/sync_music.py --verify           # check existing URLs still play

    After --apply, download the new clips:
        python tools/download_audio.py

REQUIREMENTS
    yt-dlp on PATH (brew install yt-dlp, or pip install yt-dlp)
    Python 3.8+ (standard library only)

CONFIG
    Both IDs below are for this project's artist. Point them somewhere else to
    reuse this script for a different Heardle.
"""

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# --- Configuration -----------------------------------------------------------

ARTIST_NAME = "Sam Bowman"
DEEZER_ARTIST_ID = 11145178
YOUTUBE_CHANNEL = "https://www.youtube.com/channel/UC4-DeiRFx7RPhooKaFAYXdA"

# A YouTube upload is accepted as "the same recording" only if its runtime is
# within this many seconds of Deezer's. Lyric videos often carry a few seconds of
# lead-in or outro, so this is deliberately loose enough to allow that but tight
# enough to reject a different mix or a full-album upload.
DURATION_TOLERANCE = 12

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
MUSIC_JSON = PROJECT_ROOT / "src" / "settings" / "music.json"

# Deezer lists a lot of duplicate/regional re-releases. Skip albums whose title
# matches these (case-insensitive substring).
ALBUM_SKIP = ()

# Track titles to never add (case-insensitive substring). Empty here; the
# Matthew Parker Heardle uses this to exclude instrumentals, whose backing track
# is identical to the vocal version already in its list.
TITLE_SKIP = ()


# --- Helpers -----------------------------------------------------------------


def deezer(path):
    """GET a Deezer API path, with retries. Returns {} on persistent failure."""
    url = f"https://api.deezer.com/{path}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=25) as resp:
                data = json.load(resp)
            if isinstance(data, dict) and data.get("error"):
                # Deezer signals quota exhaustion in-band with HTTP 200.
                time.sleep(2 * (attempt + 1))
                continue
            return data
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    print(f"  ! Deezer request failed: {path}", file=sys.stderr)
    return {}


def match_key(title):
    """
    Aggressively normalize a track title so Deezer and YouTube spellings collide.

    Deezer and YouTube disagree constantly on case, punctuation, and suffixes
    like "(from Young Pop Renegades, Vol. 2)", so all of that is stripped. This
    key is ONLY for matching -- never write it back to music.json.
    """
    t = title.lower()
    t = re.sub(r"\(from [^)]*\)", " ", t)
    t = re.sub(r"\[(official|lyric)[^\]]*\]", " ", t)
    t = re.sub(r"\((official|lyric|audio|visualizer)[^)]*\)", " ", t)
    # Drop guest credits entirely, names included. music.json often stores a
    # bare "Spark" where YouTube has "Spark (feat. Rapture Ruckus)"; keeping the
    # guest's name would make those two titles never agree.
    t = re.sub(r"[\(\[]\s*(feat|ft)\.?[^)\]]*[\)\]]", " ", t)
    t = t.replace("&", " and ")
    t = re.sub(r"\bfeat\.?\b|\bft\.?\b", " ", t)
    t = re.sub(r"[^a-z0-9]+", "", t)
    return t


def slugify(title):
    """
    Port of scripts/update-music-ids.js.

    MUST stay byte-identical to that implementation: the id becomes the audio
    filename (public/audio/<id>.mp3), so any drift silently breaks playback.
    JavaScript's \\w is ASCII-only, hence re.ASCII here.
    """
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.ASCII)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s


def yt_dlp(args, timeout=420):
    """Run yt-dlp, returning stdout ('' on failure). Never raises."""
    try:
        proc = subprocess.run(
            ["yt-dlp", *args], capture_output=True, text=True, timeout=timeout
        )
        return proc.stdout
    except FileNotFoundError:
        print("❌ yt-dlp not found on PATH. Install it: brew install yt-dlp")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        return ""


SEP = "\x1f"  # unit separator: safe against titles containing | or tabs


def parse_yt_lines(raw):
    out = []
    for line in raw.strip().splitlines():
        parts = line.split(SEP)
        if len(parts) < 3:
            continue
        vid, dur, title = parts[0], parts[1], SEP.join(parts[2:])
        try:
            dur = int(float(dur))
        except (TypeError, ValueError):
            dur = None
        out.append({"id": vid, "duration": dur, "title": title})
    return out


# --- Data collection ---------------------------------------------------------


def fetch_deezer_catalog(since=None):
    """Return [{title, album, record_type, release, duration, art}] newest first."""
    albums = deezer(f"artist/{DEEZER_ARTIST_ID}/albums?limit=300").get("data", [])
    albums.sort(key=lambda a: a.get("release_date", ""), reverse=True)

    tracks, seen = [], set()
    for alb in albums:
        release = alb.get("release_date", "")
        if since and release < since:
            continue
        if any(s.lower() in alb["title"].lower() for s in ALBUM_SKIP):
            continue

        detail = deezer(f"album/{alb['id']}")
        time.sleep(0.2)  # be polite to the public API
        for tr in detail.get("tracks", {}).get("data", []):
            key = match_key(tr["title"])
            if key in seen:
                continue
            if any(s.lower() in tr["title"].lower() for s in TITLE_SKIP):
                continue
            seen.add(key)
            tracks.append(
                {
                    "title": tr["title"],
                    # Standalone singles are recorded as album "Single" to match
                    # the convention already used throughout music.json.
                    "album": "Single"
                    if alb.get("record_type") == "single"
                    else alb["title"],
                    "record_type": alb.get("record_type"),
                    "release": release,
                    "duration": tr.get("duration"),
                    "art": alb.get("cover_medium"),
                }
            )
    return tracks


def fetch_channel_videos():
    """Every video on the artist's channel: [{id, duration, title}]."""
    raw = yt_dlp(
        [
            YOUTUBE_CHANNEL,
            "--flat-playlist",
            "--skip-download",
            "--print",
            f"%(id)s{SEP}%(duration)s{SEP}%(title)s",
        ]
    )
    return parse_yt_lines(raw)


def search_youtube(query, n=5):
    raw = yt_dlp(
        [
            f"ytsearch{n}:{query}",
            "--flat-playlist",
            "--skip-download",
            "--print",
            f"%(id)s{SEP}%(duration)s{SEP}%(title)s",
        ],
        timeout=240,
    )
    return parse_yt_lines(raw)


# --- Matching ----------------------------------------------------------------


def title_keys(video_title):
    """
    Every plausible normalized key for a YouTube title.

    Collabs are usually uploaded to the *collaborator's* channel and titled
    "Matthew Parker & Sam Bowman - Gravity Strikes Again (Official Lyric Video)".
    Matching the whole string against "Gravity Strikes Again" fails, so we also
    offer the text after each artist separator as a candidate key.
    """
    keys = {match_key(video_title)}
    for sep in (" - ", " | ", " – ", " — ", ": "):
        if sep in video_title:
            head, _, tail = video_title.partition(sep)
            keys.add(match_key(tail))
            keys.add(match_key(video_title.rsplit(sep, 1)[-1]))
    keys.discard("")
    return keys


def pick(candidates, track):
    """
    Best video for a track, or None.

    Requires a normalized title match AND runtimes agreeing within
    DURATION_TOLERANCE. Among survivors the closest runtime wins. Returning None
    is the safe outcome: the caller reports it for a human to resolve rather than
    guessing, because a wrong URL means the wrong song plays.
    """
    key = match_key(track["title"])
    dur = track.get("duration")

    titled = [c for c in candidates if key in title_keys(c["title"])]
    if not titled:
        return None
    if dur is None:
        return titled[0]

    ok = [
        c
        for c in titled
        if c["duration"] is not None and abs(c["duration"] - dur) <= DURATION_TOLERANCE
    ]
    if not ok:
        return None
    ok.sort(key=lambda c: abs(c["duration"] - dur))
    return ok[0]


# --- Commands ----------------------------------------------------------------


def url_alive(url):
    """True if YouTube still serves this video."""
    return bool(yt_dlp(["--skip-download", "--print", "%(id)s", url], timeout=90).strip())


def cmd_repair(music, apply):
    """
    Find replacement URLs for entries whose video has been taken down.

    Videos get removed, re-uploaded, or made private, which breaks both the clip
    download and the post-game reveal for that song. Rather than hand-editing
    URLs, this re-matches the dead entries against the artist's current channel
    using the same title+duration rules as the sync.
    """
    print(f"Checking {len(music)} URLs...")
    dead = [t for t in music if not t.get("url") or not url_alive(t["url"])]
    print(f"  {len(dead)} dead\n")
    if not dead:
        print("✅ Nothing to repair.")
        return 0

    # Deezer runtimes let us reject a same-titled but different recording.
    durations = {}
    for alb in deezer(f"artist/{DEEZER_ARTIST_ID}/albums?limit=300").get("data", []):
        for tr in deezer(f"album/{alb['id']}").get("tracks", {}).get("data", []):
            durations.setdefault(match_key(tr["title"]), tr.get("duration"))
        time.sleep(0.15)

    print("Listing the artist's YouTube channel...")
    channel = fetch_channel_videos()
    print(f"  {len(channel)} videos\n")

    fixed, unfixed = [], []
    for track in dead:
        probe = {"title": track["title"], "duration": durations.get(match_key(track["title"]))}
        vid = pick(channel, probe) or pick(search_youtube(f"{track['title']} {ARTIST_NAME}"), probe)
        if vid:
            fixed.append((track, vid))
        else:
            unfixed.append(track)

    for track, vid in fixed:
        print(f"✅ {track['title']}")
        print(f"   old: {track.get('url')}")
        print(f"   new: https://www.youtube.com/watch?v={vid['id']}  ({vid['duration']}s)")
    for track in unfixed:
        print(f"❔ {track['title']}  -- no replacement found, fix by hand")
        print(f"   dead url: {track.get('url')}")

    if not apply:
        print(f"\n(dry run -- {len(fixed)} repairable. Re-run with --apply to write.)")
        return 0

    for track, vid in fixed:
        track["url"] = f"https://www.youtube.com/watch?v={vid['id']}"
    MUSIC_JSON.write_text(
        json.dumps(music, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\n✅ Repaired {len(fixed)} URLs. {len(unfixed)} still need manual attention.")
    print("Now run: python tools/download_audio.py")
    return 0


def cmd_verify(music):
    """Check that every URL already in music.json still resolves on YouTube."""
    print(f"Verifying {len(music)} existing URLs (this takes a minute)...\n")
    dead = []
    for i, track in enumerate(music, 1):
        url = track.get("url", "")
        if not url:
            dead.append((track, "no url"))
            continue
        out = yt_dlp(["--skip-download", "--print", "%(id)s", url], timeout=90)
        if not out.strip():
            dead.append((track, "unavailable"))
            print(f"  [{i}/{len(music)}] ❌ {track['title']}")
        else:
            print(f"  [{i}/{len(music)}] ✅ {track['title']}", end="\r")
    print("\n")
    if dead:
        print(f"❌ {len(dead)} broken:\n")
        for track, why in dead:
            print(f"  {track['title']}  ({why})")
            print(f"    id:  {track.get('id')}")
            print(f"    url: {track.get('url')}")
        print("\nFix the url in music.json, delete the stale mp3 in public/audio/,")
        print("then re-run tools/download_audio.py.")
    else:
        print("✅ All URLs resolve.")
    return 1 if dead else 0


def main():
    ap = argparse.ArgumentParser(
        description="Sync music.json with the artist's latest releases."
    )
    ap.add_argument(
        "--apply", action="store_true", help="write new entries to music.json"
    )
    ap.add_argument("--since", metavar="YYYY-MM-DD", help="only releases on/after this")
    ap.add_argument(
        "--verify", action="store_true", help="check existing URLs still resolve"
    )
    ap.add_argument(
        "--repair",
        action="store_true",
        help="find replacement URLs for videos that have been taken down",
    )
    ap.add_argument(
        "--no-search-fallback",
        action="store_true",
        help="channel listing only; skip the per-track YouTube search fallback",
    )
    args = ap.parse_args()

    music = json.loads(MUSIC_JSON.read_text(encoding="utf-8"))

    if args.verify:
        return cmd_verify(music)

    if args.repair:
        return cmd_repair(music, args.apply)

    have = {match_key(t["title"]) for t in music}
    have_ids = {t.get("id") for t in music}

    print(f"📚 music.json currently has {len(music)} tracks")
    print(f"🔎 Fetching Deezer catalog{' since ' + args.since if args.since else ''}...")
    catalog = fetch_deezer_catalog(since=args.since)
    print(f"   {len(catalog)} distinct tracks released")

    new = [t for t in catalog if match_key(t["title"]) not in have]
    if not new:
        print("\n✅ music.json is already up to date.")
        return 0

    print(f"   {len(new)} not in music.json\n")
    print("📺 Listing the artist's YouTube channel...")
    channel = fetch_channel_videos()
    print(f"   {len(channel)} videos\n")

    matched, unmatched = [], []
    for track in new:
        vid = pick(channel, track)
        source = "channel"
        if not vid and not args.no_search_fallback:
            # Collabs are often hosted on the collaborator's channel. Try the
            # artist-qualified query first, then the bare title -- adding the
            # artist name can push an exactly-titled collab upload out of the
            # results entirely.
            for query in (f"{track['title']} {ARTIST_NAME}", track["title"]):
                vid = pick(search_youtube(query), track)
                if vid:
                    break
            source = "search"
        if vid:
            matched.append((track, vid, source))
        else:
            unmatched.append(track)

    print("=" * 72)
    print(f"NEW TRACKS: {len(new)}   matched: {len(matched)}   unmatched: {len(unmatched)}")
    print("=" * 72)

    for track, vid, source in matched:
        slug = slugify(track["title"])
        clash = "  ⚠️  ID COLLISION" if slug in have_ids else ""
        print(f"\n✅ {track['title']}")
        print(f"   album:   {track['album']}   released {track['release']}")
        print(f"   id:      {slug}{clash}")
        print(f"   youtube: https://www.youtube.com/watch?v={vid['id']}")
        print(f"   runtime: deezer {track['duration']}s / youtube {vid['duration']}s  (via {source})")

    for track in unmatched:
        print(f"\n❔ {track['title']}")
        print(f"   album:   {track['album']}   released {track['release']}")
        print(f"   runtime: {track['duration']}s")
        print("   no confident YouTube match -- add the url by hand if you want this one")

    if not args.apply:
        print("\n(dry run -- nothing written. Re-run with --apply to add the matched tracks.)")
        return 0

    added = 0
    for track, vid, _ in matched:
        slug = slugify(track["title"])
        if slug in have_ids:
            print(f"\n⚠️  Skipping '{track['title']}': id '{slug}' already exists.")
            continue
        music.append(
            {
                "title": track["title"],
                "url": f"https://www.youtube.com/watch?v={vid['id']}",
                "art": track["art"],
                "album": track["album"],
                "id": slug,
            }
        )
        have_ids.add(slug)
        added += 1

    MUSIC_JSON.write_text(
        json.dumps(music, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\n✅ Added {added} tracks. music.json now has {len(music)}.")
    print("\nNext:")
    print("  1. python tools/download_audio.py     # fetch the new 32s clips")
    print("  2. npm run dev                        # check it locally")
    print("  3. vercel --prod                      # deploy WITH the audio files")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled")
        sys.exit(130)
