#!/usr/bin/env python3
"""
Word-by-Word Translation Scraper for QuranWBW.com
This module scrapes word-by-word translation data and stores it locally.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin

class QuranWBWScraper:
    def __init__(self, data_file="wbw_data.json"):
        self.data_file = data_file
        self.base_url = "https://quranwbw.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
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
    
    def scrape_ayah(self, surah_num, ayah_num):
        """Scrape word-by-word data for a specific ayah"""
        url = f"{self.base_url}/{surah_num}/{ayah_num}"
        key = f"{surah_num}:{ayah_num}"
        
        # Check if we already have this data
        if key in self.data:
            print(f"Data for {key} already exists, skipping...")
            return self.data[key]
        
        try:
            print(f"Scraping {url}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract word-by-word data
            words_data = []
            
            # Look for word containers (this may need adjustment based on actual HTML structure)
            word_containers = soup.find_all(['div', 'span'], class_=lambda x: x and 'word' in x.lower())
            
            if not word_containers:
                # Alternative approach - look for any elements containing Arabic text
                word_containers = soup.find_all(text=True)
                word_containers = [elem for elem in word_containers if elem.strip() and any('\u0600' <= char <= '\u06FF' for char in elem)]
            
            for container in word_containers:
                if isinstance(container, str):
                    text = container.strip()
                else:
                    text = container.get_text().strip()
                
                if text and any('\u0600' <= char <= '\u06FF' for char in text):
                    # This is Arabic text, extract word data
                    word_data = {
                        'arabic': text,
                        'transliteration': '',
                        'translation': '',
                        'grammar': ''
                    }
                    
                    # Try to find associated translation/transliteration
                    parent = container.parent if hasattr(container, 'parent') else None
                    if parent:
                        # Look for translation in nearby elements
                        translation_elem = parent.find_next(['div', 'span'], class_=lambda x: x and ('translation' in x.lower() or 'meaning' in x.lower()))
                        if translation_elem:
                            word_data['translation'] = translation_elem.get_text().strip()
                    
                    words_data.append(word_data)
            
            # If we didn't find structured data, try a different approach
            if not words_data:
                # Look for any text that might contain word-by-word data
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                for line in lines:
                    if any('\u0600' <= char <= '\u06FF' for char in line):
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
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.data[key] = ayah_data
            print(f"Scraped {len(words_data)} words for {key}")
            
            # Be respectful - add delay between requests
            time.sleep(1)
            
            return ayah_data
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_page(self, page_num):
        """Scrape all ayahs on a specific page"""
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
                
                ayah_data = self.scrape_ayah(surah_num, ayah_num)
                if ayah_data:
                    page_data['ayahs'].append(ayah_data)
            
            return page_data
            
        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")
            return None
    
    def get_ayah_data(self, surah_num, ayah_num):
        """Get word-by-word data for an ayah (from cache or scrape if needed)"""
        key = f"{surah_num}:{ayah_num}"
        
        if key in self.data:
            return self.data[key]
        
        # Scrape if not in cache
        return self.scrape_ayah(surah_num, ayah_num)
    
    def get_page_data(self, page_num):
        """Get word-by-word data for all ayahs on a page"""
        try:
            # Get page data from alquran.cloud
            response = requests.get(f"http://api.alquran.cloud/v1/page/{page_num}/quran-uthmani")
            response.raise_for_status()
            
            ayahs = response.json()["data"]["ayahs"]
            page_data = []
            
            for ayah in ayahs:
                surah_num = ayah['surah']['number']
                ayah_num = ayah['numberInSurah']
                
                ayah_data = self.get_ayah_data(surah_num, ayah_num)
                if ayah_data:
                    page_data.append(ayah_data)
            
            return page_data
            
        except Exception as e:
            print(f"Error getting page {page_num} data: {e}")
            return []

def main():
    """Example usage"""
    scraper = QuranWBWScraper()
    
    # Scrape a few pages as example
    print("Starting to scrape word-by-word data...")
    
    # Scrape page 1 as an example
    page_data = scraper.scrape_page(1)
    if page_data:
        print(f"Scraped page 1 with {len(page_data['ayahs'])} ayahs")
    
    # Save all data
    scraper.save_data()
    
    print("Scraping completed!")

if __name__ == "__main__":
    main()
