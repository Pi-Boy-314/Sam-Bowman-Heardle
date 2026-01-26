import json
from typing import Dict, List

STEP3_INPUT = "scripts/output/step3_with_urls.json"
STEP3_OUTPUT = "scripts/output/step3_with_urls.json"
FINAL_MUSIC_JSON = "src/settings/music.json"


def load_tracks() -> List[Dict]:
    with open(STEP3_INPUT, "r", encoding="utf-8") as f:
        return json.load(f)


def save_outputs(tracks: List[Dict]) -> None:
    with open(STEP3_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(tracks, f, indent=2, ensure_ascii=False)
    final_payload = [
        {"title": t["title"], "album": t["album"], "art": t.get("art"), "url": t.get("url")}
        for t in tracks
    ]
    with open(FINAL_MUSIC_JSON, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, indent=2, ensure_ascii=False)
    print(f"\nSaved final music list -> {FINAL_MUSIC_JSON}")


def review_track(track: Dict, idx: int, total: int) -> None:
    """Interactively review a single track and optionally replace its URL."""
    print(f"\n{'='*70}")
    print(f"[{idx}/{total}] {track['title']}")
    print(f"{'='*70}")
    print(f"Album: {track.get('album', 'N/A')}")
    print(f"Current URL: {track.get('url', 'None')}")
    
    uploader = track.get('yt_uploader')
    match_score = track.get('yt_match_score')
    if uploader:
        print(f"Uploader: {uploader}")
    if match_score is not None:
        print(f"Match Score: {match_score:.2f}")
    
    print()
    response = input("Keep this URL? (y/n/skip): ").strip().lower()
    
    if response == 'n':
        new_url = input("Enter replacement URL (or 'URL NEEDED'): ").strip()
        if new_url:
            track["url"] = new_url
            # Clear auto-generated metadata if manually replaced
            track.pop("yt_uploader", None)
            track.pop("yt_match_score", None)
            print(f"✓ Updated URL to: {new_url}")
        else:
            print("✗ No URL provided, keeping original")
    elif response == 'skip':
        print("Skipped")
    else:
        print("✓ Keeping current URL")


def main() -> None:
    tracks = load_tracks()
    print(f"Loaded {len(tracks)} tracks from {STEP3_INPUT}")
    
    # Filter tracks that need review: no URL, "URL NEEDED", or uploader is not Matthew Parker
    tracks_to_review = []
    for track in tracks:
        url = track.get("url")
        uploader = (track.get("yt_uploader") or "").lower()
        
        needs_review = (
            not url
            or url == "URL NEEDED"
            or (url and uploader and uploader != "matthew parker")
        )
        
        if needs_review:
            tracks_to_review.append(track)
    
    if not tracks_to_review:
        print("\n✓ All tracks have valid URLs uploaded by Matthew Parker!")
        print("No manual review needed.")
        return
    
    print("=" * 70)
    print("Manual URL Review")
    print("=" * 70)
    print(f"Found {len(tracks_to_review)} tracks to review (non-Matthew Parker or missing URLs)")
    print(f"Skipping {len(tracks) - len(tracks_to_review)} tracks with valid Matthew Parker URLs")
    print()
    print("For each track, you can:")
    print("  - Enter 'y' to keep the current URL")
    print("  - Enter 'n' to replace it (you'll be prompted for a new URL)")
    print("  - Enter 'skip' to skip without changes")
    print("  - Press Ctrl+C to save and exit early")
    print("=" * 70)
    
    try:
        for idx, track in enumerate(tracks_to_review, start=1):
            review_track(track, idx, len(tracks_to_review))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Saving progress...")
    
    save_outputs(tracks)
    print(f"Saved updated tracks -> {STEP3_OUTPUT}")
    print("\nReview complete!")


if __name__ == "__main__":
    main()
