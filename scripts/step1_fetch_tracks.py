import json
import sys
import time
from typing import Dict, Iterable, List, Tuple
from urllib.parse import quote

import requests

ARTIST_NAME = "Matthew Parker"
STEP1_OUTPUT = "scripts/output/step1_tracks.json"


def fetch_artist_id(name: str) -> Tuple[int, Dict]:
    """Look up the Deezer artist ID by name."""
    url = f"https://api.deezer.com/search/artist?q={quote(name)}"
    print(f"Searching Deezer for artist '{name}' -> {url}")
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    payload = response.json()
    for artist in payload.get("data", []):
        if artist.get("name", "").lower() == name.lower():
            print(f"Matched artist: {artist.get('name')} (id={artist.get('id')})")
            return int(artist["id"]), artist
    if payload.get("data"):
        fallback = payload["data"][0]
        print(f"Using first search result as fallback: {fallback.get('name')} (id={fallback.get('id')})")
        return int(fallback["id"]), fallback
    raise RuntimeError("No artist results returned from Deezer")


def fetch_paginated(url: str) -> Iterable[Dict]:
    """Yield all items from a Deezer paginated resource."""
    page = 1
    while url:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", [])
        print(f"  Page {page}: {len(data)} items from {url}")
        for item in data:
            yield item
        url = payload.get("next")
        page += 1
        time.sleep(0.25)  # be polite to the API


def fetch_albums(artist_id: int) -> List[Dict]:
    url = f"https://api.deezer.com/artist/{artist_id}/albums?limit=100"
    print(f"Fetching albums for artist {artist_id}: {url}")
    albums: List[Dict] = []
    seen = set()
    for album in fetch_paginated(url):
        album_id = int(album["id"])
        if album_id in seen:
            continue
        seen.add(album_id)
        albums.append(album)
    print(f"Found {len(albums)} unique albums/EPs/singles")
    return albums


def build_track_list(albums: List[Dict], artist_id: int) -> List[Dict]:
    results: List[Dict] = []
    seen: set = set()
    album_summary: List[Tuple[str, int]] = []
    for idx, album in enumerate(albums, start=1):
        album_id = int(album["id"])
        record_type = album.get("record_type", "").lower()
        album_title = album.get("title", "").strip()
        album_label = "Single" if record_type == "single" else album_title
        print(f"\n[{idx}/{len(albums)}] Album: {album_title} (record_type={record_type}, id={album_id})")
        tracklist_url = album.get("tracklist")
        if not tracklist_url:
            print("  No tracklist url; skipping")
            continue
        track_count = 0
        for track in fetch_paginated(tracklist_url):
            if int(track.get("artist", {}).get("id", 0)) != artist_id:
                continue  # skip appearances where he's not the primary artist
            title = track.get("title", "").strip()
            key = (title.lower(), album_label.lower())
            if key in seen:
                continue
            seen.add(key)
            results.append(
                {
                    "title": title,
                    "album": album_label,
                    "deezer_track_id": int(track.get("id")),
                    "deezer_album_id": album_id,
                    "album_record_type": record_type,
                }
            )
            print(f"    + {title}")
            track_count += 1
        album_summary.append((album_title, track_count))
        time.sleep(0.2)
    
    # Sort results by album name for easier manual review
    results.sort(key=lambda t: (t["album"].lower(), t["title"].lower()))
    
    print(f"\n{'='*60}")
    print(f"Collected {len(results)} unique tracks across {len(album_summary)} albums")
    print(f"{'='*60}")
    print("Album summary (for manual review):")
    for album_name, count in album_summary:
        print(f"  {album_name}: {count} tracks")
    print(f"{'='*60}\n")
    return results


def main() -> None:
    try:
        artist_id, artist = fetch_artist_id(ARTIST_NAME)
        albums = fetch_albums(artist_id)
        tracks = build_track_list(albums, artist_id)
        with open(STEP1_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(tracks, f, indent=2, ensure_ascii=False)
        print(f"Saved step1 track list -> {STEP1_OUTPUT}")
    except Exception as exc:
        print(f"Error during step1: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
