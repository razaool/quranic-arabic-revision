# One Page A Day - Quran Revision Web App

A simple Flask web app for daily Quran revision that generates random pages with Arabic text and English translation.

## Features

- 🎲 **Random Page Generation**: Automatically selects unrevised pages
- 📱 **iPad Optimized**: Works perfectly in Safari on iPad
- 📊 **Progress Tracking**: Shows completion percentage and revised pages
- 🖼️ **Image Download**: Downloads PNG images for annotation
- 📖 **Surah Information**: Displays which surahs are on each page
- 🚫 **No Duplicates**: Prevents revisiting the same page twice

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Run the app**:
   ```bash
   python app.py
   ```

3. **Access on iPad**:
   - Open Safari on your iPad
   - Go to `http://[your-computer-ip]:5001`
   - Bookmark for easy access

## Usage

1. Click "Generate Random Page" button
2. Wait for page generation (takes ~10-15 seconds)
3. Click "Download Image for iPad" 
4. Image downloads to your iPad Photos
5. Open in your favorite annotation app (GoodNotes, Notability, etc.)
6. Annotate and study!

## Files

- `app.py` - Main Flask application
- `templates/index.html` - Web interface
- `requirements.txt` - Python dependencies
- `revised_pages.json` - Progress tracking (auto-created)
- `quran_page_*.png` - Generated images

## Technical Details

- Uses AlQuran Cloud API for Quran data
- Playwright for HTML-to-image conversion
- JSON file for persistent progress tracking
- Responsive design optimized for mobile/iPad
- Beautiful Arabic typography with proper RTL support

## Network Access

To access from iPad, make sure your computer and iPad are on the same WiFi network, then use your computer's IP address instead of localhost.