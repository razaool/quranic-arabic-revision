from flask import Flask, render_template, send_file, jsonify, request
import os
import tempfile
import subprocess
import sys
import json
import random
import requests
from wbw_integration import WBWManager

app = Flask(__name__)

# Initialize WBW manager
wbw_manager = WBWManager()

def load_revised_pages():
    try:
        with open('revised_pages.json', 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_revised_pages(pages):
    with open('revised_pages.json', 'w') as f:
        json.dump(list(pages), f)

def get_random_unrevised_page():
    revised_pages = load_revised_pages()
    all_pages = set(range(1, 605))  # Pages 1-604
    unrevised_pages = all_pages - revised_pages
    
    if not unrevised_pages:
        return None
    
    return random.choice(list(unrevised_pages))

def install_playwright():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        return True
    except:
        return False

def generate_page_image(page_num):
    try:
        ar = requests.get(f"http://api.alquran.cloud/v1/page/{page_num}/quran-uthmani").json()["data"]["ayahs"]
        en = requests.get(f"http://api.alquran.cloud/v1/page/{page_num}/en.sahih").json()["data"]["ayahs"]
    except Exception as e:
        print(f"Error fetching page data: {e}")
        return None, None
    
    # Get surah information for the page
    surahs_on_page = set()
    for ayah in ar:
        surahs_on_page.add(ayah['surah']['englishName'])
    
    surah_titles = " • ".join(sorted(surahs_on_page))
    
    # Arabic only (no translation)
    arabic_only = []
    for a in ar:
        arabic_only.append(f"<div style='margin:30px 0'><div style=\"direction:rtl;text-align:right;font-family:'Amiri','Scheherazade New','Times New Roman',serif;font-size:72px;line-height:3.2\">{a['text']} <span style='color:#d4af37;font-size:.4em;margin-left:25px'>{a['numberInSurah']}</span></div></div>")
    
    # Save Arabic only
    arabic_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Scheherazade+New:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; padding: 20px; background: #1e293b; color: white; }}
        </style>
    </head>
    <body>
        <div style="background:#1e293b;padding:40px;border-radius:10px;width:2000px;max-width:100%">
            <div style="text-align:center;margin-bottom:20px;padding:15px;background:#0f172a;border-radius:8px;border:2px solid #d4af37">
                <h1 style="margin:0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:24px;color:#d4af37;font-weight:bold">Page {page_num}</h1>
                <h2 style="margin:5px 0 0 0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:18px;color:#e2e8f0;font-weight:normal">{surah_titles}</h2>
            </div>
            {''.join(arabic_only)}
        </div>
    </body>
    </html>
    """
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_arabic.html', delete=False, encoding='utf-8') as f:
        f.write(arabic_html)
        arabic_file = f.name
    
    arabic_output = f"quran_page_{page_num}_arabic.png"
    
    try:
        # Save Arabic only
        result = subprocess.run([
            sys.executable, "-c", f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({{"width": 2400, "height": 3000}})
        await page.goto('file://{arabic_file}')
        await page.screenshot(path='{arabic_output}', full_page=True)
        await browser.close()

asyncio.run(main())
"""
        ], capture_output=True, text=True)
        
        print(f"Playwright result: returncode={result.returncode}")
        print(f"Playwright stdout: {result.stdout}")
        print(f"Playwright stderr: {result.stderr}")
        
        if result.returncode == 0:
            # Mark page as revised
            revised_pages = load_revised_pages()
            revised_pages.add(page_num)
            save_revised_pages(revised_pages)
            os.unlink(arabic_file)
            return arabic_output, surah_titles
        else:
            print(f"Playwright failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            os.unlink(arabic_file)
            return None, None
    except Exception as e:
        print(f"Exception in generate_page_image: {e}")
        os.unlink(arabic_file)
        return None, None

@app.route('/')
def index():
    revised_pages = load_revised_pages()
    progress = len(revised_pages)
    total = 604
    percentage = (progress / total) * 100
    
    return render_template('index.html', 
                         progress=progress, 
                         total=total, 
                         percentage=round(percentage, 1))

@app.route('/generate', methods=['POST'])
def generate():
    page_num = get_random_unrevised_page()
    
    if not page_num:
        return jsonify({
            'success': False,
            'message': '🎉 Congratulations! You have revised all 604 pages of the Quran!'
        })
    
    image_file, surah_titles = generate_page_image(page_num)
    
    if image_file:
        # Get word-by-word data availability
        has_wbw = wbw_manager.has_wbw_data(page_num)
        wbw_link = f'/wbw/{page_num}' if has_wbw else f'/scrape-page/{page_num}'
        
        return jsonify({
            'success': True,
            'page_num': page_num,
            'surah_titles': surah_titles,
            'image_url': f'/download/{image_file}',
            'wbw_link': wbw_link,
            'wbw_available': has_wbw,
            'message': f'✅ Page {page_num} generated successfully!'
        })
    else:
        return jsonify({
            'success': False,
            'message': '❌ Error generating page image'
        })

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

@app.route('/progress')
def progress():
    revised_pages = load_revised_pages()
    return jsonify({
        'revised': len(revised_pages),
        'total': 604,
        'percentage': round((len(revised_pages) / 604) * 100, 1)
    })

@app.route('/scraped-data')
def scraped_data():
    """Display all scraped word-by-word data"""
    try:
        # Load the scraped data
        if os.path.exists('wbw_data.json'):
            with open('wbw_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Create HTML display
        html_parts = [
            '<!DOCTYPE html>',
            '<html><head><meta charset="UTF-8">',
            '<title>Scraped Word-by-Word Data</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }',
            '.container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }',
            '.ayah-item { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }',
            '.ayah-header { color: #d4af37; font-weight: bold; margin-bottom: 10px; }',
            '.word-item { display: inline-block; margin: 5px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; min-width: 100px; text-align: center; }',
            '.arabic-word { font-size: 18px; font-family: "Amiri", serif; direction: rtl; margin-bottom: 5px; }',
            '.transliteration { font-size: 12px; color: #666; margin-bottom: 3px; }',
            '.translation { font-size: 12px; color: #333; }',
            '.stats { background: #e8f4fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }',
            '</style>',
            '</head><body>',
            '<div class="container">',
            '<h1>📚 Scraped Word-by-Word Data</h1>'
        ]
        
        # Add statistics
        total_ayahs = len(data)
        total_words = sum(len(ayah_data.get('words', [])) for ayah_data in data.values())
        html_parts.extend([
            '<div class="stats">',
            f'<h3>📊 Statistics</h3>',
            f'<p><strong>Total Ayahs Scraped:</strong> {total_ayahs}</p>',
            f'<p><strong>Total Words:</strong> {total_words}</p>',
            f'<p><strong>Data File:</strong> wbw_data.json</p>',
            '</div>'
        ])
        
        if data:
            # Sort by surah and ayah
            sorted_data = sorted(data.items(), key=lambda x: (x[1]['surah'], x[1]['ayah']))
            
            for key, ayah_data in sorted_data:
                surah = ayah_data['surah']
                ayah = ayah_data['ayah']
                words = ayah_data.get('words', [])
                
                html_parts.extend([
                    f'<div class="ayah-item">',
                    f'<div class="ayah-header">Surah {surah}, Ayah {ayah}</div>'
                ])
                
                if words:
                    for word in words:
                        html_parts.extend([
                            '<div class="word-item">',
                            f'<div class="arabic-word">{word["arabic"]}</div>',
                            f'<div class="transliteration">{word["transliteration"] or "N/A"}</div>',
                            f'<div class="translation">{word["translation"] or "N/A"}</div>',
                            '</div>'
                        ])
                else:
                    html_parts.append('<p style="color: #666;">No word data available</p>')
                
                html_parts.append('</div>')
        else:
            html_parts.append('<p>No scraped data found. <a href="/scrape-page/1">Start scraping</a></p>')
        
        html_parts.extend([
            '<p><a href="/">← Back to Main App</a></p>',
            '</div></body></html>'
        ])
        
        return ''.join(html_parts)
        
    except Exception as e:
        return f"<html><body><h1>Error</h1><p>Error loading scraped data: {e}</p><a href='/'>← Back</a></body></html>"

@app.route('/scrape-page/<int:page_num>')
def scrape_page(page_num):
    """Scrape word-by-word data for a specific page"""
    try:
        wbw_manager.scrape_page_if_needed(page_num)
        wbw_manager.scraper.save_data()
        
        return f"""
        <html><body>
        <h1>✅ Scraping Complete</h1>
        <p>Page {page_num} has been scraped for word-by-word data.</p>
        <p><a href="/scraped-data">View All Scraped Data</a></p>
        <p><a href="/wbw/{page_num}">View Page {page_num} WBW</a></p>
        <p><a href="/">← Back to Main App</a></p>
        </body></html>
        """
    except Exception as e:
        return f"<html><body><h1>Error</h1><p>Error scraping page {page_num}: {e}</p><a href='/'>← Back</a></body></html>"

@app.route('/wbw/<int:page_num>')
def word_by_word(page_num):
    """Display word-by-word translation for a page"""
    try:
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
                <h1>📖 Word-by-Word Translation - Page {page_num}</h1>
                {html}
                <p><a href="/scraped-data">View All Scraped Data</a></p>
                <p><a href="/">← Back to Main App</a></p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<html><body><h1>Error</h1><p>Error loading WBW data for page {page_num}: {e}</p><a href='/'>← Back</a></body></html>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
