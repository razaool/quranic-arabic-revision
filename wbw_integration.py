#!/usr/bin/env python3
"""
Integration script to add word-by-word functionality to the main Flask app
This script provides functions that can be imported into your main app.py
"""

import json
import os
from wbw_scraper import QuranWBWScraper

class WBWManager:
    def __init__(self, data_file="wbw_data.json"):
        self.scraper = QuranWBWScraper(data_file)
        self.data_file = data_file
    
    def get_page_wbw_data(self, page_num):
        """Get word-by-word data for all ayahs on a page"""
        try:
            # Get page data from alquran.cloud to know which ayahs are on this page
            import requests
            response = requests.get(f"http://api.alquran.cloud/v1/page/{page_num}/quran-uthmani")
            response.raise_for_status()
            
            ayahs = response.json()["data"]["ayahs"]
            page_wbw_data = []
            
            for ayah in ayahs:
                surah_num = ayah['surah']['number']
                ayah_num = ayah['numberInSurah']
                
                # Get word-by-word data
                wbw_data = self.scraper.get_ayah_data(surah_num, ayah_num)
                if wbw_data:
                    page_wbw_data.append({
                        'surah': surah_num,
                        'ayah': ayah_num,
                        'arabic_text': ayah['text'],
                        'wbw_data': wbw_data
                    })
            
            return page_wbw_data
            
        except Exception as e:
            print(f"Error getting WBW data for page {page_num}: {e}")
            return []
    
    def has_wbw_data(self, page_num):
        """Check if we have word-by-word data for a page"""
        page_data = self.get_page_wbw_data(page_num)
        return len(page_data) > 0 and any(ayah['wbw_data']['words'] for ayah in page_data)
    
    def scrape_page_if_needed(self, page_num):
        """Scrape word-by-word data for a page if we don't have it"""
        if not self.has_wbw_data(page_num):
            print(f"Scraping WBW data for page {page_num}...")
            self.scraper.scrape_page(page_num)
            self.scraper.save_data()
            return True
        return False
    
    def get_wbw_html(self, page_num):
        """Generate HTML for word-by-word display"""
        page_data = self.get_page_wbw_data(page_num)
        
        if not page_data:
            return "<p>No word-by-word data available for this page.</p>"
        
        html_parts = []
        for ayah_data in page_data:
            surah = ayah_data['surah']
            ayah = ayah_data['ayah']
            wbw_data = ayah_data['wbw_data']
            
            html_parts.append(f'<div class="ayah-wbw" style="margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px;">')
            html_parts.append(f'<h4 style="color: #d4af37; margin-bottom: 10px;">Surah {surah}, Ayah {ayah}</h4>')
            
            if wbw_data['words']:
                html_parts.append('<div class="words-container" style="display: flex; flex-wrap: wrap; gap: 10px;">')
                for word in wbw_data['words']:
                    html_parts.append(f'''
                        <div class="word-item" style="border: 1px solid #ccc; padding: 8px; border-radius: 4px; min-width: 100px; text-align: center;">
                            <div class="arabic-word" style="font-size: 18px; font-family: 'Amiri', serif; direction: rtl; margin-bottom: 5px;">
                                {word['arabic']}
                            </div>
                            <div class="transliteration" style="font-size: 12px; color: #666; margin-bottom: 3px;">
                                {word['transliteration'] or 'N/A'}
                            </div>
                            <div class="translation" style="font-size: 12px; color: #333;">
                                {word['translation'] or 'N/A'}
                            </div>
                        </div>
                    ''')
                html_parts.append('</div>')
            else:
                html_parts.append('<p style="color: #666;">Word-by-word data not available for this ayah.</p>')
            
            html_parts.append('</div>')
        
        return ''.join(html_parts)

# Example usage functions
def add_wbw_to_flask_app():
    """
    Instructions for integrating WBW functionality into your Flask app:
    
    1. Import this module in your app.py:
       from wbw_integration import WBWManager
    
    2. Initialize the manager:
       wbw_manager = WBWManager()
    
    3. Add a new route for WBW data:
       @app.route('/wbw/<int:page_num>')
       def word_by_word(page_num):
           wbw_manager.scrape_page_if_needed(page_num)
           html = wbw_manager.get_wbw_html(page_num)
           return html
    
    4. Modify your generate route to include WBW data:
       In your generate() function, add:
       wbw_html = wbw_manager.get_wbw_html(page_num)
       return jsonify({
           # ... existing fields ...
           'wbw_html': wbw_html,
           'has_wbw': wbw_manager.has_wbw_data(page_num)
       })
    """
    pass

if __name__ == "__main__":
    # Test the integration
    manager = WBWManager()
    
    # Test with page 1
    print("Testing WBW integration...")
    page_data = manager.get_page_wbw_data(1)
    print(f"Found data for {len(page_data)} ayahs on page 1")
    
    if page_data:
        html = manager.get_wbw_html(1)
        print("Generated HTML length:", len(html))
        print("First 200 characters:", html[:200])
    else:
        print("No data found, attempting to scrape...")
        manager.scrape_page_if_needed(1)
