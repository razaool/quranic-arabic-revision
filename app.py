from flask import Flask, render_template, send_file, jsonify, request
import os
import tempfile
import subprocess
import sys
import json
import random
import requests

app = Flask(__name__)

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

def get_page_ayahs(page_num):
    """Get the surah and ayah numbers for a given page"""
    try:
        response = requests.get(f"http://api.alquran.cloud/v1/page/{page_num}/quran-uthmani")
        response.raise_for_status()
        ayahs = response.json()["data"]["ayahs"]
        
        # Get the first and last ayah on the page
        first_ayah = ayahs[0]
        last_ayah = ayahs[-1]
        
        return {
            'first_surah': first_ayah['surah']['number'],
            'first_ayah': first_ayah['numberInSurah'],
            'last_surah': last_ayah['surah']['number'],
            'last_ayah': last_ayah['numberInSurah']
        }
    except Exception as e:
        print(f"Error fetching page ayahs: {e}")
        return None

def generate_wbw_link(page_num):
    """Generate quranwbw.com link for the first ayah on the page"""
    page_ayahs = get_page_ayahs(page_num)
    if page_ayahs:
        surah = page_ayahs['first_surah']
        ayah = page_ayahs['first_ayah']
        return f"https://quranwbw.com/{surah}/{ayah}"
    return None

def install_playwright():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        return True
    except:
        return False

def generate_page_image(page_num, max_retries=3):
    """Generate page image with retry logic to handle Playwright crashes"""
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries} for page {page_num}")
            
            # Fetch page data
            ar = requests.get(f"http://api.alquran.cloud/v1/page/{page_num}/quran-uthmani").json()["data"]["ayahs"]
            
            # Get surah information for the page
            surahs_on_page = set()
            for ayah in ar:
                surahs_on_page.add(ayah['surah']['englishName'])
            
            surah_titles = " • ".join(sorted(surahs_on_page))
            
            # Arabic only (no translation)
            arabic_only = []
            for a in ar:
                arabic_only.append(f"<div style='margin:30px 0'><div style=\"direction:rtl;text-align:right;font-family:'Amiri','Scheherazade New','Times New Roman',serif;font-size:72px;line-height:3.2;color:white\">{a['text']} <span style='color:#cccccc;font-size:.4em;margin-left:25px'>{a['numberInSurah']}</span></div></div>")
            
            # Save Arabic only
            arabic_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Scheherazade+New:wght@400;700&display=swap" rel="stylesheet">
                <style>
                    body {{ margin: 0; padding: 0; background: #000000; color: white; }}
                </style>
            </head>
            <body>
                <div style="background:#000000;padding:40px;border-radius:10px;width:2000px;max-width:100%;margin:20px 20px 20px 0px">
                    <div style="text-align:center;margin-bottom:20px;padding:15px;background:#1a1a1a;border-radius:8px;border:2px solid white">
                        <h1 style="margin:0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:24px;color:white;font-weight:bold">Page {page_num}</h1>
                        <h2 style="margin:5px 0 0 0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:18px;color:#cccccc;font-weight:normal">{surah_titles}</h2>
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
            
            # Try Playwright with timeout and better error handling
            result = subprocess.run([
                sys.executable, "-c", f"""
import asyncio
import signal
import sys
from playwright.async_api import async_playwright

async def main():
    try:
        async with async_playwright() as p:
            # Use Firefox instead of Chromium for better stability
            browser = await p.firefox.launch()
            page = await browser.new_page()
            await page.set_viewport_size({{"width": 2400, "height": 3000}})
            await page.goto('file://{arabic_file}', timeout=30000)
            await page.screenshot(path='{arabic_output}', full_page=True)
            await browser.close()
            print("SUCCESS: Image generated successfully")
    except Exception as e:
        print(f"ERROR: {{e}}")
        sys.exit(1)

asyncio.run(main())
"""
            ], capture_output=True, text=True, timeout=60)
            
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
                
                # If this is the last attempt, return failure
                if attempt == max_retries - 1:
                    return None, None
                
                # Wait before retrying
                import time
                time.sleep(2)
                continue
                
        except Exception as e:
            print(f"Exception in generate_page_image (attempt {attempt + 1}): {e}")
            if 'arabic_file' in locals():
                os.unlink(arabic_file)
            
            # If this is the last attempt, return failure
            if attempt == max_retries - 1:
                return None, None
            
            # Wait before retrying
            import time
            time.sleep(2)
            continue
    
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
        # Generate WBW link for quranwbw.com
        wbw_link = generate_wbw_link(page_num)
        
        return jsonify({
            'success': True,
            'page_num': page_num,
            'surah_titles': surah_titles,
            'image_url': f'/download/{image_file}',
            'wbw_link': wbw_link,
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

@app.route('/completed')
def completed_pages():
    revised_pages = load_revised_pages()
    total = 604
    percentage = round((len(revised_pages) / total) * 100, 1)
    
    # Sort pages for better display
    sorted_pages = sorted(list(revised_pages))
    
    return render_template('completed.html', 
                         revised_pages=sorted_pages,
                         progress=len(revised_pages),
                         total=total,
                         percentage=percentage)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
