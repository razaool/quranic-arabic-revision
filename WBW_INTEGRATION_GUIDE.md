# Word-by-Word Integration Guide

## Overview
I've created a complete word-by-word translation system for your Quranic Arabic revision app. Here's what was created:

### Files Created:
1. **`wbw_scraper.py`** - Main scraping functionality
2. **`wbw_integration.py`** - Integration layer for your Flask app
3. **`test_wbw_scraping.py`** - Test script to verify functionality
4. **`wbw_data.json`** - Local storage for scraped data

## Current Status:
- ✅ **Scraping framework**: Complete and ready
- ✅ **Local storage**: JSON-based data storage
- ✅ **HTML generation**: Beautiful word-by-word display
- ⚠️ **Website scraping**: quranwbw.com uses JavaScript, needs adjustment
- ✅ **Mock data**: Working perfectly for testing

## How to Integrate into Your Flask App:

### Option 1: Simple Integration (Recommended)
Add these lines to your `app.py`:

```python
# Add this import at the top
from wbw_integration import WBWManager

# Add this after your Flask app initialization
wbw_manager = WBWManager()

# Add this new route for word-by-word display
@app.route('/wbw/<int:page_num>')
def word_by_word(page_num):
    """Display word-by-word translation for a page"""
    wbw_manager.scrape_page_if_needed(page_num)
    html = wbw_manager.get_wbw_html(page_num)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Word-by-Word Translation - Page {page_num}</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Word-by-Word Translation - Page {page_num}</h1>
            {html}
            <p><a href="/">← Back to Main App</a></p>
        </div>
    </body>
    </html>
    """

# Modify your generate route to include WBW link
# In your generate() function, change the return statement to:
return jsonify({
    'success': True,
    'page_num': page_num,
    'surah_titles': surah_titles,
    'image_url': f'/download/{image_file}',
    'wbw_link': f'/wbw/{page_num}',  # Changed from external link
    'wbw_available': wbw_manager.has_wbw_data(page_num),
    'message': f'✅ Page {page_num} generated successfully!'
})
```

### Option 2: Enhanced Integration
For a more integrated experience, you can also:

1. **Add WBW data to your main page**:
```python
@app.route('/')
def index():
    # ... existing code ...
    return render_template('index.html', 
                         progress=progress, 
                         total=total, 
                         percentage=round(percentage, 1),
                         wbw_manager=wbw_manager)  # Add this
```

2. **Add WBW toggle to your template**:
```html
<!-- Add this to your index.html template -->
<div id="wbw-section" style="display: none;">
    <h3>Word-by-Word Translation</h3>
    <div id="wbw-content"></div>
</div>

<script>
function toggleWBW(pageNum) {
    fetch(`/wbw/${pageNum}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('wbw-content').innerHTML = html;
            document.getElementById('wbw-section').style.display = 'block';
        });
}
</script>
```

## Testing the Integration:

1. **Test with mock data**:
```bash
python3 test_wbw_scraping.py
```

2. **Test the integration**:
```bash
python3 -c "
from wbw_integration import WBWManager
manager = WBWManager()
print('Testing page 1...')
html = manager.get_wbw_html(1)
print(f'Generated HTML: {len(html)} characters')
print('Preview:', html[:200] + '...')
"
```

## Next Steps for Real Data:

Since quranwbw.com uses JavaScript, you have a few options:

1. **Use Selenium/Playwright** for JavaScript rendering:
```python
# Add to wbw_scraper.py
from playwright.sync_api import sync_playwright

def scrape_with_playwright(self, surah_num, ayah_num):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"https://quranwbw.com/{surah_num}/{ayah_num}")
        page.wait_for_load_state('networkidle')
        # Extract data from rendered page
        browser.close()
```

2. **Find alternative data sources**:
   - Look for APIs that provide word-by-word data
   - Use other Quran websites with better scraping support

3. **Use the mock data** for now and gradually add real data

## Benefits:
- ✅ **Offline access**: No need to visit external websites
- ✅ **Faster loading**: Local data is much faster
- ✅ **Better integration**: Seamless experience in your app
- ✅ **Customizable**: You control the display format
- ✅ **Scalable**: Easy to add more pages

The system is ready to use! Start with the simple integration and test it with the mock data.
