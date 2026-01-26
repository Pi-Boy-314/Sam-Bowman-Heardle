import json
import sys
import time
from typing import Dict, List

import requests

STEP1_INPUT = "scripts/output/step1_tracks.json"
STEP2_OUTPUT = "scripts/output/step2_with_art.json"


def load_tracks() -> List[Dict]:
    with open(STEP1_INPUT, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_album_cover(album_id: int) -> str:
    url = f"https://api.deezer.com/album/{album_id}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    cover = data.get("cover_medium") or data.get("cover") or data.get("cover_big")
    if not cover:
        raise RuntimeError(f"No cover image found for album {album_id}")
    return cover


def attach_album_art(tracks: List[Dict]) -> List[Dict]:
    album_cache: Dict[int, str] = {}
    updated: List[Dict] = []
    for idx, track in enumerate(tracks, start=1):
        album_id = int(track.get("deezer_album_id"))
        if album_id not in album_cache:
            try:
                album_cache[album_id] = fetch_album_cover(album_id)
                print(f"[{idx}/{len(tracks)}] Album {album_id} art -> {album_cache[album_id]}")
            except Exception as exc:
                print(f"[{idx}/{len(tracks)}] Failed to fetch art for album {album_id}: {exc}")
                album_cache[album_id] = None
            time.sleep(0.2)
        art_url = album_cache.get(album_id)
        updated.append({**track, "art": art_url})
    return updated


def main() -> None:
    try:
        tracks = load_tracks()
        print(f"Loaded {len(tracks)} tracks from {STEP1_INPUT}")
        updated = attach_album_art(tracks)
        with open(STEP2_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(updated, f, indent=2, ensure_ascii=False)
        print(f"Saved step2 output with album art -> {STEP2_OUTPUT}")
    except Exception as exc:
        print(f"Error during step2: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
