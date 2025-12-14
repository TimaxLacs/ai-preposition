import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
import hashlib

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://www.kilotons.ru/"
OUTPUT_DIR = os.path.join(BASE_DIR, "pages")
MAP_FILE = os.path.join(BASE_DIR, "site_map.json")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

visited = set()
queue = [BASE_URL]
site_map = {}  # URL -> list of links found on that page

def get_filename(url):
    """Generates a safe filename from a URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    
    # Replace slashes with underscores or create directories
    safe_name = path.replace("/", "_")
    
    # Add hash to ensure uniqueness for long paths or query params
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    
    return f"{safe_name}_{url_hash}.html"

def crawl():
    print(f"Starting crawl of {BASE_URL}...")
    
    while queue:
        current_url = queue.pop(0)
        
        if current_url in visited:
            continue
            
        visited.add(current_url)
        print(f"Processing: {current_url}")
        
        try:
            response = requests.get(current_url, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch {current_url}: Status {response.status_code}")
                continue
                
            # Save HTML
            filename = get_filename(current_url)
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            # Parse links
            soup = BeautifulSoup(response.text, "html.parser")
            links = []
            
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                full_url = urljoin(current_url, href)
                
                # Normalize URL (remove fragment)
                parsed_url = urlparse(full_url)
                clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                if parsed_url.query:
                    clean_url += "?" + parsed_url.query
                
                # Check if internal link
                if BASE_URL in clean_url or urlparse(BASE_URL).netloc in clean_url:
                    links.append(clean_url)
                    if clean_url not in visited and clean_url not in queue:
                        queue.append(clean_url)
            
            site_map[current_url] = links
            
            # Be polite
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing {current_url}: {e}")

    # Save site map
    print("Saving site map...")
    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(site_map, f, indent=2, ensure_ascii=False)
    
    print("Crawl completed!")

if __name__ == "__main__":
    crawl()

