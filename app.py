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

def install_playwright():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        return True
    except:
        return False

def generate_page_image(page_num):
    ar = requests.get(f"http://api.alquran.cloud/v1/page/{page_num}/quran-uthmani").json()["data"]["ayahs"]
    en = requests.get(f"http://api.alquran.cloud/v1/page/{page_num}/en.sahih").json()["data"]["ayahs"]
    
    # Get surah information for the page
    surahs_on_page = set()
    for ayah in ar:
        surahs_on_page.add(ayah['surah']['englishName'])
    
    surah_titles = " • ".join(sorted(surahs_on_page))
    
    # Arabic + translation
    arabic_translation = []
    for a,e in zip(ar,en):
        arabic_translation.append(f"<div style='margin:10px 0'><div style=\"direction:rtl;text-align:right;font-family:'Amiri','Scheherazade New','Times New Roman',serif;font-size:24px;line-height:2.2\">{a['text']} <span style='color:#d4af37;font-size:.8em;margin-left:10px'>{a['numberInSurah']}</span></div><div style=\"font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:16px;line-height:1.6;color:#eee\">{e['text']}</div></div>")
    
    # Save Arabic + translation
    translation_html = f"""
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
        <div style="background:#1e293b;padding:16px;border-radius:10px;width:800px">
            <div style="text-align:center;margin-bottom:20px;padding:15px;background:#0f172a;border-radius:8px;border:2px solid #d4af37">
                <h1 style="margin:0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:24px;color:#d4af37;font-weight:bold">Page {page_num}</h1>
                <h2 style="margin:5px 0 0 0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:18px;color:#e2e8f0;font-weight:normal">{surah_titles}</h2>
            </div>
            {''.join(arabic_translation)}
        </div>
    </body>
    </html>
    """
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_translation.html', delete=False, encoding='utf-8') as f:
        f.write(translation_html)
        translation_file = f.name
    
    translation_output = f"quran_page_{page_num}_arabic_translation.png"
    
    try:
        # Save Arabic + translation
        result = subprocess.run([
            sys.executable, "-c", f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('file://{translation_file}')
        await page.screenshot(path='{translation_output}', full_page=True)
        await browser.close()

asyncio.run(main())
"""
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Mark page as revised
            revised_pages = load_revised_pages()
            revised_pages.add(page_num)
            save_revised_pages(revised_pages)
            os.unlink(translation_file)
            return translation_output, surah_titles
        else:
            os.unlink(translation_file)
            return None, None
    except Exception as e:
        os.unlink(translation_file)
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
        return jsonify({
            'success': True,
            'page_num': page_num,
            'surah_titles': surah_titles,
            'image_url': f'/download/{image_file}',
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
