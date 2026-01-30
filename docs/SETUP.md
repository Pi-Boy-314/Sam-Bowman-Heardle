# Sam Bowman Heardle - Complete Setup Guide

Everything you need to set up, download audio, and deploy this project.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Initial Setup](#initial-setup)
3. [Audio Download](#audio-download)
4. [Deployment to Vercel](#deployment-to-vercel)
5. [Troubleshooting](#troubleshooting)

---

## Legal Notice

**READ THIS BEFORE DOWNLOADING AUDIO**

The tools provided in this repository (`tools/download_audio.py` and `tools/scrape_deezer.py`) are for **educational and personal use only**.

**You must ensure:**
- You own the rights to all music being downloaded
- You have explicit permission from copyright holders
- You are complying with all applicable laws and Terms of Service

**Using these tools to download copyrighted content without permission is illegal.** The authors assume no liability for misuse.

For safer alternatives:
- Use official streaming APIs (Spotify Web Playback SDK, YouTube IFrame API)
- Obtain proper licenses for public deployment
- Use Creative Commons or public domain music

---

## Quick Start

**For first-time setup:**

```powershell
# 1. Install dependencies
npm install
pip install yt-dlp

# 2. Download audio files (1-2 hours for 88 tracks)
python tools/download_audio.py

# 3. Run locally
npm run dev

# 4. Build for production
npm run build
```

**Verify setup:**
- Dev server should load at http://localhost:5173
- Audio plays from `/api/audio?id={song-id}` (not YouTube)
- Use `npm run dev-host` to test on other devices on your LAN

---

## Initial Setup

### Prerequisites

- **Node.js** (v16+)
- **Python** (3.7+)
- **ffmpeg** (for audio conversion)

### Step 1: Install Node Packages

```bash
npm install
```

### Step 2: Install Python Dependencies

```bash
pip install yt-dlp
```

### Step 3: Install ffmpeg

#### Windows (Chocolatey - Recommended)

```powershell
# Install Chocolatey if you don't have it:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install ffmpeg:
choco install ffmpeg

# Add to PATH (PowerShell as Administrator):
$ffmpegPath = "C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$ffmpegPath", "Machine")

# Restart PowerShell and verify:
ffmpeg -version
```

#### Windows (Manual)

1. Download from https://ffmpeg.org/download.html#build-windows
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Search "environment variables" in Windows Start
   - Edit the system environment variables → Environment Variables
   - Under System variables, select "Path" → Edit
   - Add: `C:\ffmpeg\bin`
   - OK three times
4. Restart terminal and verify: `ffmpeg -version`

#### macOS

```bash
brew install ffmpeg
```

#### Linux

```bash
sudo apt-get install ffmpeg
```

---

## Audio Download

### Download All Tracks

Run this to download all 88 songs from YouTube:

```bash
python tools/download_audio.py
```

**What it does:**
- Validates `yt-dlp` and `ffmpeg` are installed
- Reads `src/settings/music.json` for YouTube URLs
- Downloads audio from each URL with browser-like headers
- Converts to MP3 (192kbps) using ffmpeg
- Saves to `public/audio/` with ID-based filenames (e.g., `ashes.mp3`)
- Skips already-downloaded files (safe to re-run)
- Displays progress and file sizes

**Expected time:** 1-2 hours for 88 songs (~2.5GB total)

**Audio files are NOT committed to git** — excluded in `.gitignore`. They're uploaded separately to Vercel during deployment.

### Check Progress

```powershell
# Count downloaded files:
(Get-ChildItem public\audio\*.mp3).Count

# List recent downloads:
Get-ChildItem public\audio\ | Sort-Object LastWriteTime -Descending | Select-Object -First 10
```

### Common Issues


**Solutions:**
1. Run script again (sometimes temporary)
2. Update yt-dlp: `pip install --upgrade yt-dlp`
3. Try: `pip install --upgrade yt-dlp -U`
4. Check YouTube URL is still valid (not deleted/private)
5. Manually download problematic videos and place in `public/audio/{id}.mp3` (matching the ID from music.json)
2. Update yt-dlp: `pip install --upgrade yt-dlp`
3. Check if YouTube URL is still valid
4. Manually download problematic videos and place in `public/audio/{id}.mp3`

**ffmpeg Not Found**

Make sure:
1. ffmpeg is installed (see Step 3 above)
2. Added to system PATH
3. Restarted terminal after installation
4. Run: `ffmpeg -version` to verify

---

## Deployment to Vercel

### Prerequisites

- GitHub account
- Vercel account (free tier works)
- All audio files downloaded to `public/audio/`

### Step 1: Commit Code to GitHub

```bash
# Initialize git (if not already)
git init

# Add files (audio excluded via .gitignore)
git add .
git commit -m "Initial commit with audio backend"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

**Important:** Audio files are NOT committed to GitHub (excluded in `.gitignore`). They'll be uploaded to Vercel separately.

### Step 2: Deploy to Vercel

1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "New Project"
4. Import your repository
5. Configure:
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
6. Click "Deploy"

Vercel will build and deploy your frontend. Audio files will be handled in the next step.

### Step 3: Deploy with Audio Files

**Option 1: Vercel CLI (Recommended)**

```bash
# Install Vercel CLI (if not already)
npm install -g vercel

# Login to Vercel
vercel login

# Link to your project (if not already linked)
vercel link

# Deploy with all files including audio
vercel --prod
```

The CLI automatically includes `public/audio/` files in the deployment.

**Option 2: Git Push (Automatic)**

Once linked, simply push to GitHub:

```bash
git push origin main
```

Vercel auto-deploys on push. However, audio files are in `.gitignore`, so you must use Vercel CLI or upload them separately.

**Option 3: Manual Upload via Vercel Dashboard**

1. After initial deployment, go to Vercel dashboard
2. Click your project
3. File Browser (left sidebar) → `public/` folder
4. Drag-and-drop `audio/` folder with MP3 files

### Step 4: Verify CORS Configuration

The API endpoint `/api/audio` in `api/audio.js` includes CORS restrictions and rate limiting:

**Current configuration:**
- **Rate limit:** 20 requests/min per IP (prevents abuse)
- **CORS whitelist:** 
  - `http://localhost:5173` (local dev)
  - `http://localhost:3000` (alt local dev)
  - `https://sam-bowman-heardle.vercel.app` (production)

**If you deploy to a different Vercel URL:**

1. Update `api/audio.js` with your new domain:

```javascript
const allowedOrigins = [
  'http://localhost:5173',
  'http://localhost:3000',
  'https://your-custom-domain.vercel.app', // Add your Vercel URL
];
```

2. Redeploy: `vercel --prod`

### Step 5: Test Deployment

1. **Visit your Vercel URL** and play a song
2. **Check network tab** (F12 → Network) → requests to `/api/audio?id=...` should return 200 OK
3. **Check browser console** (F12 → Console) for any CORS errors
4. **iOS/Android test:** 
   - Control Center should show "Sam Bowman Heardle" (using LocalAudioPlayer)
   - If it shows YouTube title, the app fell back to YouTube player
5. **Rate limit test:** Rapidly click play/pause 20+ times → 429 errors expected after 20 requests/min

2. Redeploy: `vercel --prod`` folder with MP3 filed
2. Settings → Environment → File System
3. Upload `public/audio/` folder contents

### Step 4: Configure CORS

The API endpoint `/api/audio` includes CORS restrictions. Update allowed origins in `api/audio.js`:

```javascript
const allowedOrigins = [
  'https://your-vercel-domain.vercel.app',
  'http://localhost:5173', // For local dev
];
```

Redeploy after updating.

### Step 5: Test Deployment

1. Visit your Vercel URL
2. Play a song → should load from `/api/audio?id={id}`
3. Check iOS Safari → Control Center should show "Sam Bowman Heardle" (not YouTube title)

---

## Troubleshooting

### Audio Not Playing on Vercel

**Diagnostics:**
1. Open browser console: F12 → Console
2. Open network tab: F12 → Network
3. Click play → check `/api/audio?id=...` requests

**Common issues:**

| Problem | Cause | Fix |
|---------|-------|-----|
| 404 error in Network tab | Audio file missing from Vercel | Use Vercel CLI: `vercel --prod` |
| CORS error in console | Domain not in `allowedOrigins` | Update `api/audio.js` with your Vercel URL |
| Requests to YouTube instead | Music IDs missing from `music.json` | Run: `node scripts/update-music-ids.js` |
| 429 error after many plays | Rate limit exceeded (20/min per IP) | Wait 1 minute or test on different IP |
| Empty audio duration | File corrupted or ffmpeg failed | Re-run: `python tools/download_audio.py` |

**Verify files uploaded:**
- Vercel dashboard → File Browser → `public/audio/` should show MP3 files
- Or check deployment logs for audio file sizes

### iOS/Android Control Center Shows Wrong Title

**Expected behavior:** Should show "Sam Bowman Heardle" (using LocalAudioPlayer)
**Actual behavior:** Shows YouTube title (fell back to YouTube player)

**Root cause:** Music entries missing `id` field in `music.json`

**Fix:**

1. Regenerate all IDs:
```bash
node scripts/update-music-ids.js
```

2. Verify each track has an `id` field:
```bash
grep -c '"id":' src/settings/music.json
```
Should match total track count (~88)

3. Hard refresh browser:
   - Windows/Linux: Ctrl+Shift+R
   - Mac: Cmd+Shift+R
4. Re-test on mobile

### Downloads Keep Failing

**403 Forbidden:**
- Update yt-dlp: `pip install --upgrade yt-dlp`
- Check if video is region-locked or age-restricted
- Try VPN if region-locked

**ffmpeg errors:**
- Verify: `ffmpeg -version` works in terminal
- Check PATH includes ffmpeg bin directory
- Restart terminal after adding to PATH

### Vercel Bandwidth Limit Exceeded

**Free tier limits:** 100GB/month bandwidth

**Bandwidth estimate:**
- Average song: ~2.5MB (192kbps MP3, ~2 min)
- Per user per day: 2.5MB × 6 attempts = 15MB
- 100 daily users: 1.5GB/day = ~45GB/month ✓ (OK)
- 300+ daily users: ~135GB/month ✗ (exceeds limit)

**Rate limiting helps:** 20 req/min/IP prevents excessive downloads from one user.

**Solutions if you exceed limit:**

1. **Upgrade to Vercel Pro:** $20/month → 1TB bandwidth
2. **Reduce audio quality:**
   - Edit `tools/download_audio.py`: change `'preferredquality': '192'` to `'128'`
   - Re-download audio: `python tools/download_audio.py`
   - Files will be ~1.3MB each instead of ~2.5MB
   - Re-deploy: `vercel --prod`
3. **Use external CDN:**
   - Upload audio to Cloudflare R2, Backblaze B2, or AWS S3
   - Update `music.json` URLs to point to CDN
   - Vercel API handles routing/rate-limiting

**Estimate usage:**
- Average song: ~23MB
- Per user: ~23MB × 6 attempts = 138MB
- 30 daily users: ~4GB/day = ~120GB/month (exceeds limit)

**Solutions:**
1. Upgrade to Vercel Pro ($20/month, 1TB bandwidth)
2. Use external CDN for audio files (Cloudflare R2, Backblaze B2)
3. Reduce audio quality in `tools/download_audio.py`: `'preferredquality': '128'` instead of `'192'`

---

## Project Structure

```
Sam-Bowman-Heardle/
├── api/
│   └── audio.js                    # Vercel serverless: serves /api/audio?id=...
│                                   # Rate limits (20/min per IP), CORS, caching
├── public/
│   └── audio/                      # Downloaded MP3 files (NOT in git)
│       ├── ashes.mp3               # Auto-generated by download_audio.py
│       ├── cloudburst-xander-sallows-remix.mp3
│       └── ... (88 total)
├── src/
│   ├── App.vue                     # Root Vue component
│   ├── main.js                     # App entry, game state, daily rotation
│   ├── components/                 # Vue SFCs
│   │   ├── MainGame.vue            # Game UI
│   │   ├── TransportBar.vue        # Player controls + player selection
│   │   ├── GuessBar.vue            # Search/autocomplete
│   │   └── Modals/                 # Modal dialogs
│   ├── players/                    # Audio player implementations
│   │   ├── PlayerBase.ts           # Abstract base class
│   │   ├── LocalAudioPlayer.ts     # HTML5 audio (primary)
│   │   ├── YoutubePlayer.ts        # YouTube iframe (fallback)
│   │   └── SoundcloudPlayer.ts     # SoundCloud widget (fallback)
│   └── settings/
│       ├── music.json              # 88 tracks: title, url, art, album, id
│       ├── settings.json           # Game config: guess count, times, start-date
│       └── themes.json             # Color schemes
├── scripts/
│   └── update-music-ids.js         # Auto-generate IDs from titles in music.json
├── tools/                          # Development utilities
│   ├── download_audio.py           # Download+convert YouTube → MP3
│   └── scrape_deezer.py            # Fetch album art from Deezer API
├── docs/                           # Documentation
│   ├── README.md                   # Project overview and features
│   └── SETUP.md                    # This file - complete setup guide
├── vercel.json                     # Vercel config: build, output, function memory
└── .gitignore                      # Excludes audio files: public/audio/*.mp3
```

---

## Development

### Run Locally

```bash
npm run dev
```

Access at: http://localhost:5173

### Run on Network (for mobile testing)

```bash
npm run dev-host
```

Access at: http://YOUR_IP:5173

### Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

---

## Configuration

### Music List (`src/settings/music.json`)

```json
[
  {
    "title": "Ashes",
    "url": "https://www.youtube.com/watch?v=hyDJK5XCp6Q",
    "art": "https://cdn-images.dzcdn.net/images/cover/fcab396222642bad0db02bcb4c08a8c1/250x250-000000-80-0-0.jpg",
    "album": "Children of the Burning Heart",
    "id": "ashes"
  }
]
```

**Fields:**
- `title` (string): Display name
- `url` (string): YouTube URL → used by `tools/download_audio.py` to fetch audio, and as fallback player if local unavailable
- `art` (string): Album art URL (fetched from Deezer API by `tools/scrape_deezer.py`)
- `album` (string): Album name for grouping
- `id` (string): URL-safe slug used as filename in `public/audio/{id}.mp3` and API queries. Auto-generated by `update-music-ids.js` if missing.

**Adding new tracks:**
1. Add entry with `title`, `url`, `album`
2. Run: `node scripts/update-music-ids.js` (generates `id`)
3. Run: `python tools/scrape_deezer.py` (fetches `art`)
4. Run: `python tools/download_audio.py` (downloads audio)

### Game Settings (`src/settings/settings.json`)

```json
{
  "heardle-name": "Sam Bowman Heardle",
  "start-date": "2026-01-14T06:00:00.000Z",
  "guess-number": 6,
  "times": [1, 2, 4, 8, 16, 32]
}
```

**Fields:**
- `heardle-name` (string): App title shown in UI and Control Center
- `start-date` (ISO 8601 string): When game starts. Song rotates daily based on days since this date (Central Time). **Changing this resets all player stats!**
- `guess-number` (integer): Max attempts per day
- `times` (integer array): Playback duration per guess in seconds. Length must equal `guess-number`.
- `infinite` (boolean, optional): If `true`, random song each day instead of cycling through list

**Example changes:**
- To rotate every 2 days: Use modulo in `main.js` seed calculation
- To extend guesses to 7 attempts: Add 7th element to `times` array and set `guess-number: 7`

---

## Customizing for Another Artist

This project is designed to be easily adapted for any artist. Here's the complete guide:

### Overview: What's Artist-Specific?

The project has **clean separation** between generic game logic and artist-specific content:

| Component | Artist-Specific? | Location |
|-----------|------------------|----------|
| Game mechanics | ❌ Generic | `src/main.js`, Vue components |
| Audio players | ❌ Generic | `src/players/` |
| **Artist name** | ✅ **Customize** | `src/settings/settings.json` line 2 |
| **Song list** | ✅ **Customize** | `src/settings/music.json` (all 88 songs) |
| **Social links** | ✅ **Customize** | Modal components |
| **Documentation** | ✅ **Customize** | README, SETUP, docs |

---

### Customization Checklist

#### Phase 1: Configuration (15 minutes)

**1. Update `src/settings/settings.json` line 2:**
```json
"heardle-name": "Your Artist Name"
```
This single change updates everywhere the artist name appears (all phrases auto-substitute `{heardle-name}`).

**2. Create `src/settings/music.json` with your songs:**
```json
[
  {
    "title": "Song Title",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "album": "Album Name",
    "art": "https://image-url.jpg"
  }
]
```
**Don't worry about the `id` field yet** — it's auto-generated in Phase 2.

**3. Update `tools/scrape_deezer.py` line 12:**
```python
query = f'artist:"YOUR_ARTIST_NAME" track:"{title}"'
```
This fetches album art from Deezer during Phase 2.

#### Phase 2: Prepare Audio & Metadata (2-3 hours)

**1. Auto-generate song IDs:**
```bash
node scripts/update-music-ids.js
```
Creates URL-safe `id` fields from song titles in `music.json`.

**2. Fetch album art from Deezer:**
```bash
python tools/scrape_deezer.py
```
Updates `art` field in `music.json` with official artwork. Safe to re-run.

**3. Download audio files:**
```bash
python tools/download_audio.py
```
- Reads YouTube URLs from `music.json`
- Converts to MP3 (192kbps)
- Saves to `public/audio/{id}.mp3`
- Skips already-downloaded files (safe to resume)

**Expected time:** ~30 seconds per song (1 hr for 88 songs)

#### Phase 3: Update UI & Links (20 minutes)

**1. `src/components/Modals/AboutModal.vue` line 12:**
```vue
<p>Your Artist Heardle is a version of Heardle that features songs from Your Artist's discography.</p>
```

**2. `src/components/Modals/SupportModal.vue` lines 12-27:**
Replace all artist links:
```vue
<h3 class="section-title">Check Out Your Artist's Music</h3>
<div class="link-item">
  <span class="link-label">YouTube</span>
  <a href="https://www.youtube.com/@your-channel">your-channel</a>
</div>
<div class="link-item">
  <span class="link-label">Spotify</span>
  <a href="https://open.spotify.com/artist/SPOTIFY_ID">Spotify Link</a>
</div>
```

#### Phase 4: Update Documentation (15 minutes)

Update all references to "Sam Bowman" in:

1. **`README.md` line 1:**
   ```markdown
   # Your Artist Heardle
   ```

2. **`README.md` line 3:**
   ```markdown
   A fork of [Heardle-Base](...) customized for Your Artist's music...
   ```

3. **`README.md` line 7:**
   ```markdown
   - **Your Artist songs** with album art and metadata
   ```

4. **`.github/copilot-instructions.md` line 1:**
   ```markdown
   # Copilot instructions — Your Artist Heardle
   ```

5. **`.github/copilot-instructions.md` line 7:**
   ```markdown
   - **Fork context**: Customized fork for Your Artist's music
   ```

#### Phase 5: Deployment (15 minutes)

**1. Update `api/audio.js` line 52 with your Vercel domain:**
```javascript
const allowedOrigins = [
  'http://localhost:5173',
  'http://localhost:3000',
  'https://your-vercel-url.vercel.app',  // Add your deployment URL
];
```

**2. Update `package.json` line 1:**
```json
"name": "your-artist-heardle",
```

**3. Deploy:**
```bash
npm run build
vercel --prod
```

---

### File Reference: Exact Locations to Customize

```
src/settings/
  ├─ settings.json (Line 2)
  │  └─ "heardle-name": "ARTIST_NAME"
  │
  └─ music.json (ENTIRE FILE)
     └─ Replace all 88 songs with your artist's tracks

src/components/Modals/
  ├─ AboutModal.vue (Line 12)
  │  └─ Update description text
  │
  └─ SupportModal.vue (Lines 12-27)
     └─ Update all social media links

tools/scrape_deezer.py (Line 12)
  └─ query = f'artist:"ARTIST_NAME" track:"{title}"'

api/audio.js (Line 52)
  └─ const allowedOrigins = [..., 'YOUR_VERCEL_URL']

Documentation:
  ├─ README.md (Lines 1, 3, 7)
  ├─ SETUP.md (Line 1)
  └─ .github/copilot-instructions.md (Lines 1, 7)

Optional:
  └─ package.json (Line 1)
     └─ "name": "your-project-name"
```

---

### Example: Adapting for Matthew Parker

Here's a complete minimal example:

**Step 1: Update settings.json**
```json
{
  "heardle-name": "Matthew Parker",
  "start-date": "2024-10-21T00:00:00.000Z",
  ...
}
```

**Step 2: Create music.json (5 songs minimum)**
```json
[
  {
    "title": "Adventure",
    "url": "https://www.youtube.com/watch?v=8y6sONFwOSw",
    "album": "Adventure"
  },
  {
    "title": "If I Were A Dinosaur",
    "url": "https://www.youtube.com/watch?v=BVPfUP_Fnxs",
    "album": "Walmart"
  }
]
```

**Step 3: Update scrape_deezer.py line 12**
```python
query = f'artist:"Matthew Parker" track:"{title}"'
```

**Step 4: Generate IDs and fetch art**
```bash
node scripts/update-music-ids.js
python tools/scrape_deezer.py
```

**Step 5: Download audio**
```bash
python tools/download_audio.py
```

**Step 6: Update modals**
- AboutModal.vue: `"Matthew Parker Heardle features songs from Matthew Parker's discography."`
- SupportModal.vue: Update links to Matthew's YouTube, Spotify, Apple Music

**Step 7: Deploy**
```bash
npm run build
vercel --prod
```

Done! You now have a Matthew Parker Heardle.

---

### Troubleshooting Customization

| Problem | Cause | Solution |
|---------|-------|----------|
| Album art not fetching | Artist name doesn't match Deezer database | Edit scrape_deezer.py with exact artist name from Deezer |
| Some songs still show "Sam Bowman" in UI | Modal files not updated | Check AboutModal.vue and SupportModal.vue are edited |
| Audio download fails with 403 | Video region-locked or age-restricted | Try VPN, or manually download and place in `public/audio/{id}.mp3` |
| Control Center shows wrong title | Missing `id` field in music.json | Run: `node scripts/update-music-ids.js` |
| Blank album art | Deezer search found no results | Manually add image URL to music.json, or edit scrape_deezer.py to use exact artist name |
| Settings show artist name but modals don't | Modals have hardcoded text | Edit SupportModal.vue and AboutModal.vue directly |

---

### Advanced: Multi-Artist Setup

If hosting multiple artists:

**Option 1: Separate Repositories** (recommended)
- Clone this repo for each artist
- Customize independently
- Deploy to separate Vercel projects
- Simple, completely isolated

**Option 2: Git Branches**
- Keep `main` branch for Sam Bowman
- Create `matthew-parker`, `xander-sallows` branches
- Switch branches to customize
- Easier to maintain common code

**Option 3: Environment-Based** (advanced)
- Create multiple `music-{artist}.json` files
- Load based on environment variable: `ARTIST_NAME=matthew-parker`
- Single deployment, multiple artists via URL parameter
- Requires code changes to `main.js`

---

### Tips for Best Results

1. **YouTube URL verification:** Test each URL before downloading
   ```bash
   curl "https://www.youtube.com/watch?v=VIDEO_ID" --head
   ```

2. **Deezer artist name:** Use exact name from Deezer API search
   - Visit: https://www.deezer.com/search/ARTIST_NAME
   - Copy exact name from URL

3. **Music list size:** Start with 10-20 songs for testing, then expand
   - Phase testing: `npm run dev` with small list
   - Production: Full catalog after verified

4. **Album art manually:** If Deezer fails, add URLs manually
   ```json
   "art": "https://direct-image-url.jpg"
   ```

5. **Test on mobile:** Verify Control Center shows correct artist name
   - iOS: Control Center audio widget
   - Android: Lock screen player
   - Should show `{heardle-name}` from settings.json

---

## Need Help?

**Common commands:**

```bash
# Check how many audio files downloaded
# Windows PowerShell:
(Get-ChildItem public\audio\*.mp3 | Measure-Object).Count

# macOS/Linux:
ls public/audio/*.mp3 | wc -l

# Verify all music.json entries have IDs
node scripts/update-music-ids.js

# Re-download audio (or continue incomplete downloads)
python tools/download_audio.py

# Update album art from Deezer
python tools/scrape_deezer.py

# Deploy to Vercel with audio
vercel --prod

# Check API is working locally
curl "http://localhost:5173/api/audio?id=ashes" --output test.mp3
```

**Useful links:**
- **Original repo:** https://github.com/s4pph1r3-dev/Heardle-Base
- **yt-dlp docs:** https://github.com/yt-dlp/yt-dlp (YouTube downloader)
- **ffmpeg download:** https://ffmpeg.org/download.html (audio converter)
- **Vercel docs:** https://vercel.com/docs (deployment)
- **Deezer API:** Used by `tools/scrape_deezer.py` (album art)

**Still stuck?** Check the [copilot-instructions.md](.github/copilot-instructions.md) for architecture details.
