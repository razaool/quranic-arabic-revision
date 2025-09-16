#!/usr/bin/env python3
"""
Test script for word-by-word scraping functionality
Run this to test and demonstrate the scraping capabilities
"""

from wbw_scraper import QuranWBWScraper
from wbw_integration import WBWManager
import requests
from bs4 import BeautifulSoup
import json

def test_website_structure():
    """Test the actual structure of quranwbw.com"""
    print("Testing quranwbw.com structure...")
    
    url = "https://quranwbw.com/1/1"
    try:
        response = requests.get(url, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Print page title
        title = soup.find('title')
        print(f"Page title: {title.text if title else 'No title'}")
        
        # Look for any Arabic text
        arabic_texts = []
        for elem in soup.find_all(text=True):
            text = elem.strip()
            if text and any('\u0600' <= char <= '\u06FF' for char in text):
                arabic_texts.append(text)
        
        print(f"Found {len(arabic_texts)} Arabic text elements")
        if arabic_texts:
            print("Sample Arabic texts:")
            for i, text in enumerate(arabic_texts[:3]):
                print(f"  {i+1}: {text[:50]}...")
        
        # Look for specific patterns
        print("\nLooking for common patterns...")
        
        # Check for JavaScript loading
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags")
        
        # Check for data attributes
        elements_with_data = soup.find_all(attrs={"data-": True})
        print(f"Found {len(elements_with_data)} elements with data attributes")
        
        # Check for specific classes that might contain word data
        word_classes = []
        for elem in soup.find_all(class_=True):
            classes = ' '.join(elem.get('class', []))
            if any(keyword in classes.lower() for keyword in ['word', 'arabic', 'ayah', 'verse']):
                word_classes.append(classes)
        
        if word_classes:
            print("Found potential word-related classes:")
            for cls in set(word_classes):
                print(f"  - {cls}")
        
        return True
        
    except Exception as e:
        print(f"Error testing website: {e}")
        return False

def test_alternative_approach():
    """Test alternative scraping approaches"""
    print("\nTesting alternative approaches...")
    
    # Try different URLs or approaches
    test_urls = [
        "https://quranwbw.com/1/1",
        "https://quranwbw.com/api/1/1",  # Maybe there's an API
        "https://quranwbw.com/word/1/1",  # Different URL pattern
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"URL: {url} - Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Content length: {len(response.content)}")
                if 'json' in response.headers.get('content-type', ''):
                    print("  Appears to be JSON data!")
        except Exception as e:
            print(f"URL: {url} - Error: {e}")

def create_mock_data():
    """Create mock word-by-word data for testing"""
    print("\nCreating mock data for testing...")
    
    mock_data = {
        "1:1": {
            "url": "https://quranwbw.com/1/1",
            "surah": 1,
            "ayah": 1,
            "words": [
                {
                    "arabic": "بِسْمِ",
                    "transliteration": "bismi",
                    "translation": "In the name of",
                    "grammar": "preposition + noun"
                },
                {
                    "arabic": "اللَّهِ",
                    "transliteration": "Allahi",
                    "translation": "Allah",
                    "grammar": "proper noun"
                },
                {
                    "arabic": "الرَّحْمَٰنِ",
                    "transliteration": "ar-Rahmani",
                    "translation": "the Most Gracious",
                    "grammar": "adjective"
                },
                {
                    "arabic": "الرَّحِيمِ",
                    "transliteration": "ar-Raheemi",
                    "translation": "the Most Merciful",
                    "grammar": "adjective"
                }
            ],
            "scraped_at": "2025-09-16 19:00:00"
        }
    }
    
    # Save mock data
    with open("wbw_data.json", "w", encoding="utf-8") as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=2)
    
    print("Mock data created in wbw_data.json")
    return mock_data

def test_integration_with_mock_data():
    """Test the integration with mock data"""
    print("\nTesting integration with mock data...")
    
    # Create mock data first
    create_mock_data()
    
    # Test the integration
    manager = WBWManager()
    
    # Test getting page data
    page_data = manager.get_page_wbw_data(1)
    print(f"Page data for page 1: {len(page_data)} ayahs")
    
    # Test HTML generation
    html = manager.get_wbw_html(1)
    print(f"Generated HTML length: {len(html)}")
    print("HTML preview:")
    print(html[:300] + "..." if len(html) > 300 else html)

def main():
    """Main test function"""
    print("=== Word-by-Word Scraping Test ===\n")
    
    # Test website structure
    test_website_structure()
    
    # Test alternative approaches
    test_alternative_approach()
    
    # Create and test with mock data
    test_integration_with_mock_data()
    
    print("\n=== Test Complete ===")
    print("\nNext steps:")
    print("1. Check the actual structure of quranwbw.com manually")
    print("2. Adjust the scraper based on the real website structure")
    print("3. Use the mock data for testing the integration")
    print("4. Integrate into your main Flask app when ready")

if __name__ == "__main__":
    main()
