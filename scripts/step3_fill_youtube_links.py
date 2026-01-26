import difflib
import json
import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

from yt_dlp import YoutubeDL

STEP2_INPUT = "scripts/output/step2_with_art.json"
STEP3_OUTPUT = "scripts/output/step3_with_urls.json"
FINAL_MUSIC_JSON = "src/settings/music.json"

SEARCH_RESULTS = 5  # how many YouTube results to consider per track
EXPECTED_UPLOADER = "Matthew Parker"
CHECKPOINT_EVERY = 10  # write intermediate progress every N tracks
MAX_RETRIES = 6
BASE_BACKOFF_SECONDS = 15


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def score_match(track_title: str, candidate_title: str) -> float:
    return difflib.SequenceMatcher(None, normalize(track_title), normalize(candidate_title)).ratio()


def _extract_with_retry(ydl: YoutubeDL, search_url: str) -> Optional[Dict]:
    """Call ydl.extract_info with exponential backoff on rate limits (HTTP 429)."""
    delay = BASE_BACKOFF_SECONDS
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return ydl.extract_info(search_url, download=False)
        except Exception as exc:
            msg = str(exc).lower()
            is_rl = (
                "429" in msg
                or "too many requests" in msg
                or "rate limit" in msg
                or "quota" in msg
            )
            if attempt == MAX_RETRIES or not is_rl:
                raise
            print(f"  Rate limited (attempt {attempt}/{MAX_RETRIES}). Sleeping {delay}s...")
            time.sleep(delay)
            delay = min(delay * 2, 5 * 60)
    return None


def pick_best_youtube_url(track: Dict, ydl: YoutubeDL) -> Tuple[Optional[str], Optional[str], float]:
    """
    Returns: (url, uploader, match_score)
    """
    query = f"Matthew Parker - {track['title']}"
    search_url = f"ytsearch{SEARCH_RESULTS}:{query}"
    print(f"Searching YouTube for: {query}")
    info = _extract_with_retry(ydl, search_url)
    entries = info.get("entries", []) if info else []
    if not entries:
        print("  No YouTube results")
        return None, None, 0.0
    best_entry = None
    best_score = -1.0
    for entry in entries:
        candidate_title = entry.get("title", "")
        score = score_match(track["title"], candidate_title)
        if score > best_score:
            best_score = score
            best_entry = entry
    if best_entry:
        uploader = best_entry.get("uploader", "Unknown")
        print(
            f"  Best match: {best_entry.get('title')} | uploader={uploader} | score={best_score:.2f}"
        )
        return best_entry.get("webpage_url"), uploader, best_score
    return None, None, 0.0


def load_tracks() -> List[Dict]:
    # Prefer resuming from step3 output if it exists
    source = STEP3_OUTPUT if os.path.exists(STEP3_OUTPUT) else STEP2_INPUT
    with open(source, "r", encoding="utf-8") as f:
        tracks = json.load(f)
    print(f"Loaded {len(tracks)} tracks from {source}")
    return tracks


def save_outputs(tracks: List[Dict]) -> None:
    with open(STEP3_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(tracks, f, indent=2, ensure_ascii=False)
    final_payload = [
        {"title": t["title"], "album": t["album"], "art": t.get("art"), "url": t.get("url")}
        for t in tracks
    ]
    with open(FINAL_MUSIC_JSON, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, indent=2, ensure_ascii=False)
    print(f"Saved final music list -> {FINAL_MUSIC_JSON}")


def main() -> None:
    try:
        tracks = load_tracks()
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "nocheckcertificate": True,
            "default_search": "ytsearch",
            "no_warnings": True,  # suppress non-critical warnings
            # light pacing between requests to reduce rate-limit risk
            "sleep_interval_requests": 0.1,
            "max_sleep_interval_requests": 0.6,
        }
        flagged_tracks: List[Dict] = []
        
        with YoutubeDL(ydl_opts) as ydl:
            for idx, track in enumerate(tracks, start=1):
                print(f"[{idx}/{len(tracks)}] {track['title']} ({track['album']})")

                # Resume support: skip if a usable URL already exists
                existing_url = track.get("url")
                if existing_url and existing_url != "URL NEEDED":
                    print("  Skipping (already has URL)")
                    continue
                try:
                    url, uploader, score = pick_best_youtube_url(track, ydl)
                except Exception as exc:
                    print(f"  YouTube search error: {exc}")
                    url, uploader, score = None, None, 0.0
                
                track["url"] = url
                track["yt_uploader"] = uploader
                track["yt_match_score"] = score
                
                # Flag if uploader is not Matthew Parker
                if url and uploader and uploader.lower() != EXPECTED_UPLOADER.lower():
                    flagged_tracks.append(track)
                    print(f"  ⚠️  FLAGGED: Uploader is '{uploader}', not '{EXPECTED_UPLOADER}'")
                
                # Small polite pause between searches
                time.sleep(0.6)

                # Periodic checkpoint
                if idx % CHECKPOINT_EVERY == 0:
                    print("  Checkpoint: saving intermediate results...")
                    try:
                        save_outputs(tracks)
                    except Exception as exc:
                        print(f"  Failed to save checkpoint: {exc}")
        
        # Review flagged tracks with user
        if flagged_tracks:
            print(f"\n{'='*70}")
            print(f"⚠️  Found {len(flagged_tracks)} tracks NOT uploaded by '{EXPECTED_UPLOADER}':")
            print(f"{'='*70}")
            for track in flagged_tracks:
                print(f"\n  • {track['title']} ({track['album']})")
                print(f"    Uploader: {track['yt_uploader']}")
                print(f"    URL: {track['url']}")
            
            print(f"\n{'='*70}")
            response = input(f"Include these non-{EXPECTED_UPLOADER} URLs? (y/n): ").strip().lower()
            
            if response != 'y':
                print(f"Marking {len(flagged_tracks)} tracks as 'URL NEEDED'...")
                for track in flagged_tracks:
                    track["url"] = "URL NEEDED"
            else:
                print(f"Keeping all URLs as found.")
        
        save_outputs(tracks)
        print(f"\nSaved step3 output -> {STEP3_OUTPUT}")
        print(f"Saved final music.json -> {FINAL_MUSIC_JSON}")
    except Exception as exc:
        print(f"Error during step3: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
