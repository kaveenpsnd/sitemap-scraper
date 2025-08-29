from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import csv
import random
from collections import defaultdict
import sys
from datetime import datetime

BASE_URL = 'https://www.my-blog.com.'
visited = set()
to_visit = [(BASE_URL, 0)]  # (url, depth)
all_urls = set()
url_depth_map = defaultdict(int)  # Track depth for each URL

# Statistics tracking
stats = {
    'start_time': None,
    'urls_found': 0,
    'urls_processed': 0,
    'max_depth': 0,
    'depth_counts': defaultdict(int)
}

# Paths to ignore
excluded_paths = [
    '/cdn-cgi/l/email-protection',
    '/wp-admin/',
    '/tag/',
    '/category/',
    '/author/',
    '/wp-includes/',
    '/wp-content/',
    '/wp-content/plugins/',
    '/wp-content/themes/',
    '/wp-content/uploads/',
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.pdf'
]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def is_valid(url):
    parsed = urlparse(url)
    return parsed.netloc == urlparse(BASE_URL).netloc

def should_exclude(url):
    return any(url.lower().endswith(ext) for ext in excluded_paths)

def update_display():
    """Update the console display with current statistics"""
    elapsed_time = time.time() - stats['start_time']
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Clear the console
    sys.stdout.write('\033[2J\033[H')
    
    print("=" * 80)
    print(f"🕒 Crawling Progress - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"⏱️  Time Elapsed: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    print(f"📊 Current Statistics:")
    print(f"   • URLs Found: {stats['urls_found']}")
    print(f"   • URLs Processed: {stats['urls_processed']}")
    print(f"   • Current Queue Size: {len(to_visit)}")
    print(f"   • Maximum Depth Reached: {stats['max_depth']}")
    print("\n📈 Depth Distribution:")
    for depth in sorted(stats['depth_counts'].keys()):
        print(f"   • Depth {depth}: {stats['depth_counts'][depth]} URLs")
    print("\n🔄 Current Status:")
    if to_visit:
        current_url, current_depth = to_visit[-1]
        print(f"   • Processing: {current_url}")
        print(f"   • Current Depth: {current_depth}")
    print("=" * 80)

def crawl():
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    stats['start_time'] = time.time()
    
    try:
        while to_visit:
            url, current_depth = to_visit.pop()
            if url in visited:
                continue

            try:
                # Add random delay between 2-5 seconds
                time.sleep(random.uniform(2, 5))
                
                driver.get(url)
                # Wait for the page to load
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Get the page source and parse with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                visited.add(url)
                all_urls.add(url)
                url_depth_map[url] = current_depth
                stats['max_depth'] = max(stats['max_depth'], current_depth)
                stats['depth_counts'][current_depth] += 1
                stats['urls_processed'] += 1
                
                # Find all links
                new_urls = []
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href'].split('#')[0]  # Remove anchor links
                    full_url = urljoin(url, href)

                    if (
                        is_valid(full_url) and
                        not should_exclude(full_url) and
                        full_url not in visited and
                        full_url not in [u[0] for u in to_visit]
                    ):
                        new_urls.append((full_url, current_depth + 1))
                        stats['urls_found'] += 1

                # Add new URLs to the front of the queue (depth-first)
                to_visit.extend(new_urls)
                
                # Update display every 5 URLs processed
                if stats['urls_processed'] % 5 == 0:
                    update_display()

            except Exception as e:
                print(f'Error processing {url}: {e}')
                continue

    finally:
        driver.quit()
        return stats['max_depth']

if __name__ == "__main__":
    print("Starting depth-first crawl... This may take a while due to rate limiting.")
    print("Make sure you have Chrome and ChromeDriver installed.")
    print("Press Ctrl+C to stop the crawl at any time.")
    time.sleep(3)  # Give user time to read the message
    
    try:
        max_depth = crawl()
        update_display()  # Final display update
        print(f"\n✅ Finished crawling. Total unique pages found: {len(all_urls)}")
        print(f"Maximum depth reached: {max_depth}")

        # Export to CSV with depth information
        with open('pastpapers_urls.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['URL', 'Depth'])  # header
            for url in sorted(all_urls):
                writer.writerow([url, url_depth_map[url]])

        print("📁 Exported all URLs to pastpapers_urls.csv with depth information")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Crawling stopped by user. Saving progress...")
        # Save progress even if interrupted
        with open('pastpapers_urls.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['URL', 'Depth'])
            for url in sorted(all_urls):
                writer.writerow([url, url_depth_map[url]])
        print("📁 Progress saved to pastpapers_urls.csv")
