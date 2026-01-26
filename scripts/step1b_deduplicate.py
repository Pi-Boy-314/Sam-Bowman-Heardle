import json
from typing import Dict, List

STEP1_INPUT = "scripts/output/step1_tracks.json"
STEP1_OUTPUT = "scripts/output/step1_tracks.json"


def load_tracks() -> List[Dict]:
    with open(STEP1_INPUT, "r", encoding="utf-8") as f:
        return json.load(f)


def is_deluxe(album_name: str) -> bool:
    """Check if album name indicates deluxe/expanded edition."""
    lower = album_name.lower()
    return any(keyword in lower for keyword in ["deluxe", "expanded", "special edition", "anniversary"])


def priority_score(track: Dict) -> tuple:
    """
    Return a priority tuple for sorting. Lower = better priority.
    Priority: album > single, non-deluxe > deluxe
    """
    record_type = track.get("album_record_type", "").lower()
    album_name = track.get("album", "")
    
    # First priority: prefer albums/EPs over singles
    type_priority = 0 if record_type in ["album", "ep"] else 1
    
    # Second priority: prefer non-deluxe over deluxe
    deluxe_priority = 1 if is_deluxe(album_name) else 0
    
    return (type_priority, deluxe_priority)


def deduplicate_tracks(tracks: List[Dict]) -> List[Dict]:
    """Remove duplicates, keeping the best version per title."""
    groups: Dict[str, List[Dict]] = {}
    
    # Group by normalized title
    for track in tracks:
        title_key = track["title"].lower().strip()
        if title_key not in groups:
            groups[title_key] = []
        groups[title_key].append(track)
    
    # For each group, keep the best one
    result: List[Dict] = []
    duplicates_removed = 0
    
    for title_key, group in groups.items():
        if len(group) == 1:
            result.append(group[0])
        else:
            # Sort by priority and take the first (best) one
            sorted_group = sorted(group, key=priority_score)
            best = sorted_group[0]
            result.append(best)
            duplicates_removed += len(group) - 1
            
            print(f"Duplicate: '{best['title']}'")
            print(f"  Kept: {best['album']} ({best['album_record_type']})")
            for dup in sorted_group[1:]:
                print(f"  Removed: {dup['album']} ({dup['album_record_type']})")
    
    # Re-sort by album and title for consistent output
    result.sort(key=lambda t: (t["album"].lower(), t["title"].lower()))
    
    print(f"\n{'='*60}")
    print(f"Deduplication complete:")
    print(f"  Original: {len(tracks)} tracks")
    print(f"  After deduplication: {len(result)} tracks")
    print(f"  Removed: {duplicates_removed} duplicates")
    print(f"{'='*60}\n")
    
    return result


def main() -> None:
    tracks = load_tracks()
    print(f"Loaded {len(tracks)} tracks from {STEP1_INPUT}\n")
    
    deduplicated = deduplicate_tracks(tracks)
    
    with open(STEP1_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(deduplicated, f, indent=2, ensure_ascii=False)
    
    print(f"Saved deduplicated tracks -> {STEP1_OUTPUT}")


if __name__ == "__main__":
    main()
