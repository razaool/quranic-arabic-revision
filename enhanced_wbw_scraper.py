#!/usr/bin/env python3
"""
Enhanced Word-by-Word Scraper using Playwright for JavaScript rendering
This version can handle JavaScript-loaded content from quranwbw.com
"""

import requests
import json
import time
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class EnhancedWBWScraper:
    def __init__(self, data_file="wbw_data.json"):
        self.data_file = data_file
        self.base_url = "https://quranwbw.com"
        self.load_existing_data()
    
    def load_existing_data(self):
        """Load existing scraped data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {}
        except Exception as e:
            print(f"Error loading existing data: {e}")
            self.data = {}
    
    def save_data(self):
        """Save scraped data to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"Data saved to {self.data_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def scrape_ayah_with_playwright(self, surah_num, ayah_num):
        """Scrape word-by-word data using Playwright for JavaScript rendering"""
        url = f"{self.base_url}/{surah_num}/{ayah_num}"
        key = f"{surah_num}:{ayah_num}"
        
        # Check if we already have this data
        if key in self.data and self.data[key].get('words'):
            print(f"Data for {key} already exists, skipping...")
            return self.data[key]
        
        try:
            print(f"Scraping {url} with Playwright...")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set user agent
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                
                # Navigate to the page
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait a bit for JavaScript to load content
                page.wait_for_timeout(3000)
                
                # Get the page content after JavaScript execution
                content = page.content()
                
                browser.close()
            
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for word-by-word data
            words_data = []
            
            # Try different selectors that might contain word data
            selectors_to_try = [
                '.word',
                '.arabic-word',
                '.word-item',
                '.verse-word',
                '[class*="word"]',
                '[class*="arabic"]',
                '[data-word]'
            ]
            
            for selector in selectors_to_try:
                elements = soup.select(selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector '{selector}'")
                    for elem in elements:
                        text = elem.get_text().strip()
                        if text and any('\u0600' <= char <= '\u06FF' for char in text):
                            # Parse the text to separate Arabic, transliteration, and translation
                            parts = text.split()
                            arabic_part = ''
                            transliteration_part = ''
                            translation_part = ''
                            
                            # Find Arabic text (contains Arabic characters)
                            arabic_words = []
                            other_words = []
                            
                            for part in parts:
                                if any('\u0600' <= char <= '\u06FF' for char in part):
                                    arabic_words.append(part)
                                else:
                                    other_words.append(part)
                            
                            if arabic_words:
                                arabic_part = ' '.join(arabic_words)
                                
                                # Try to separate transliteration and translation
                                if other_words:
                                    # Look for patterns like "al-hamdu" (transliteration) and "All praises" (translation)
                                    transliteration_words = []
                                    translation_words = []
                                    
                                    for word in other_words:
                                        # If it contains hyphens or looks like transliteration
                                        if '-' in word or word.islower() or any(char.islower() for char in word):
                                            transliteration_words.append(word)
                                        else:
                                            translation_words.append(word)
                                    
                                    transliteration_part = ' '.join(transliteration_words)
                                    translation_part = ' '.join(translation_words)
                                
                                word_data = {
                                    'arabic': arabic_part,
                                    'transliteration': transliteration_part,
                                    'translation': translation_part,
                                    'grammar': ''
                                }
                                
                                words_data.append(word_data)
            
            # If no structured data found, try to extract any Arabic text
            if not words_data:
                print("No structured data found, trying to extract Arabic text...")
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                for line in lines:
                    if any('\u0600' <= char <= '\u06FF' for char in line) and len(line) < 50:
                        # This looks like a word or short phrase
                        words_data.append({
                            'arabic': line,
                            'transliteration': '',
                            'translation': '',
                            'grammar': ''
                        })
            
            # Store the data
            ayah_data = {
                'url': url,
                'surah': surah_num,
                'ayah': ayah_num,
                'words': words_data,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'method': 'playwright'
            }
            
            self.data[key] = ayah_data
            print(f"Scraped {len(words_data)} words for {key}")
            
            # Be respectful - add delay between requests
            time.sleep(2)
            
            return ayah_data
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_page_with_playwright(self, page_num):
        """Scrape all ayahs on a specific page using Playwright"""
        try:
            # Get page data from alquran.cloud to know which ayahs are on this page
            response = requests.get(f"http://api.alquran.cloud/v1/page/{page_num}/quran-uthmani")
            response.raise_for_status()
            
            ayahs = response.json()["data"]["ayahs"]
            page_data = {
                'page': page_num,
                'ayahs': []
            }
            
            for ayah in ayahs:
                surah_num = ayah['surah']['number']
                ayah_num = ayah['numberInSurah']
                
                ayah_data = self.scrape_ayah_with_playwright(surah_num, ayah_num)
                if ayah_data:
                    page_data['ayahs'].append(ayah_data)
            
            return page_data
            
        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")
            return None

def test_enhanced_scraper():
    """Test the enhanced scraper"""
    scraper = EnhancedWBWScraper()
    
    print("Testing enhanced scraper with Playwright...")
    
    # Test scraping Surah 1, Ayah 2
    data = scraper.scrape_ayah_with_playwright(1, 2)
    if data:
        print(f"Successfully scraped Surah 1, Ayah 2!")
        print(f"Found {len(data['words'])} words")
        if data['words']:
            print("First few words:")
            for i, word in enumerate(data['words'][:3]):
                print(f"  {i+1}: {word['arabic']} - {word['transliteration']} - {word['translation']}")
    else:
        print("Failed to scrape data")
    
    # Save the data
    scraper.save_data()

if __name__ == "__main__":
    test_enhanced_scraper()
