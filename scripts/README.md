# Matthew Parker ingestion scripts

This folder contains a four-step pipeline to rebuild `src/settings/music.json` with Matthew Parker's catalog. Each step is isolated so you can inspect and fix data before moving on.

## Setup
1. Install Python dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   ```
2. Ensure you can reach the Deezer and YouTube sites from your network.

## Step 1 — song + album names
- Script: `scripts/step1_fetch_tracks.py`
- Method: search Deezer for artist **Matthew Parker**, resolve his artist ID, then walk every album/EP/single via the Deezer API. Tracklists are pulled per album. Album labels are set to the album title for albums/EPs, and to `Single` when the Deezer `record_type` is `single`.
- Output: `scripts/output/step1_tracks.json` (sorted by album for manual review)
- Logging: prints the artist match, paginated album fetches, and every track added.
- **After running**: manually delete any incorrect albums from the JSON, then run step 1b.

## Step 1b — deduplication
- Script: `scripts/step1b_deduplicate.py`
- Method: removes duplicate song titles using these rules: (1) prefer albums/EPs over singles, (2) prefer regular over deluxe editions.
- Output: overwrites `scripts/output/step1_tracks.json`
- Logging: prints which duplicates were found and which version was kept vs removed.

## Step 2 — album art URLs
- Script: `scripts/step2_fill_album_art.py`
- Method: use Deezer's album endpoint for each `deezer_album_id` from step 1; cache by album to avoid duplicate calls. Deezer is reliable for covers.
- Output: `scripts/output/step2_with_art.json`
- Logging: prints each album art URL as it is fetched.

## Step 3 — YouTube links
- Script: `scripts/step3_fill_youtube_links.py`
- Method: uses `yt_dlp` to run a `ytsearch` for each track (title + "Matthew Parker"), examines the top 5 results, and picks the one with the highest fuzzy title match. Includes exponential backoff for rate limits, checkpointing every 10 tracks, and resume support (skips tracks that already have URLs).
- Outputs:
  - `scripts/output/step3_with_urls.json` (debug with metadata)
  - `src/settings/music.json` (final app-ready payload: `title`, `album`, `art`, `url`)
- Logging: prints the search query, best matched result title/uploader/score, and progress counters.
- End-of-run prompt: shows tracks not uploaded by "Matthew Parker"; choose whether to keep those URLs or set them to "URL NEEDED".

## Step 4 — Manual URL review (optional)
- Script: `scripts/step4_manual_review.py`
- Method: interactively walks through only the tracks that need review (missing URL/"URL NEEDED" or uploader not "Matthew Parker"). Shows the current URL, uploader, and match score; prompts you to keep, replace, or skip.
- Output: overwrites `scripts/output/step3_with_urls.json` and `src/settings/music.json`
- Logging: shows track details and confirmation for each change; safe to Ctrl+C mid-run (saves on exit).
- Use this to fix any URLs missed during checkpointing, incorrect matches, or tracks that need manual correction.

## Running the pipeline
```bash
python scripts/step1_fetch_tracks.py
# Manually review and delete incorrect albums from scripts/output/step1_tracks.json
python scripts/step1b_deduplicate.py
python scripts/step2_fill_album_art.py
python scripts/step3_fill_youtube_links.py
# Optional: manually review and fix any URLs
python scripts/step4_manual_review.py
```

You can re-run later steps after manual edits to the intermediate JSON files (e.g., fix an album label in `step1_tracks.json`, then re-run steps 2 and 3).
