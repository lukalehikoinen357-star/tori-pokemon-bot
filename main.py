import cloudscraper
from bs4 import BeautifulSoup
import time
import json
import os

# Configuration
SEARCH_URL = "https://tori.fi"
DB_FILE = "seen_listings.json"
CHECK_INTERVAL = 300  # Check every 5 minutes
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1510984092123004979/nd58I_eU5LqY6TL0Xc9yn12kHHaiuC-bOMz7GrxWs4iDtioJGsaRYZ-VCYnz2tfgCkt3" # Put your link here!

def load_seen_listings():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            try: return set(json.load(f))
            except: return set()
    return set()

def save_seen_listings(seen_ids):
    with open(DB_FILE, 'w') as f:
        json.dump(list(seen_ids), f)

def send_discord_alert(title, price, url):
    # Standard request for Discord webhook doesn't get blocked
    import requests
    payload = {
        "content": f"🚨 **New Pokémon Card Listing!** 🚨\n**Title:** {title}\n**Price:** {price}\n**Link:** {url}"
    }
    try: requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e: print(f"Discord error: {e}")

def check_tori():
    print("Checking Tori.fi safely for new items...")
    
    # Creates a session that automatically bypasses basic bot walls
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        response = scraper.get(SEARCH_URL)
        if response.status_code != 200:
            print(f"Blocked by Tori server. Error code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        seen_ids = load_seen_listings()
        is_first_run = len(seen_ids) == 0
        
        # Look for listing cards in Tori's modern web structure
        articles = soup.find_all(['article', 'div'], class_=lambda c: c and ('ad-card' in c or 'item' in c or 'listing' in c))
        
        # If the custom class query yields nothing, fallback to searching all item links
        if not articles:
            articles = soup.find_all('a', href=lambda h: h and '/ilmoitus/' in h)

        for article in articles:
            try:
                # Find the link
                if article.name == 'a':
                    url = article['href']
                else:
                    link_el = article.find('a', href=lambda h: h and '/ilmoitus/' in h)
                    if not link_el: continue
                    url = link_el['href']
                
                # Turn relative link into full URL
                if url.startswith('/'):
                    url = "https://www.tori.fi" + url
                    
                listing_id = url.split('/')[-1].split('?')[0]

                # Find title text
                title_el = article.find(['h2', 'h3', 'p'])
                title = title_el.text.strip() if title_el else "Pokémon Items"

                # Find price text
                price = "Check site"
                for text_node in article.find_all(text=True):
                    if '€' in text_node:
                        price = text_node.strip()
                        break

                if listing_id not in seen_ids:
                    seen_ids.add(listing_id)
                    if not is_first_run:
                        print(f"New item spotted: {title}")
                        send_discord_alert(title, price, url)
            except Exception:
                continue
                
        save_seen_listings(seen_ids)
        
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    print("Starting Tori Pokémon alert bot...")
    while True:
        check_tori()
        time.sleep(CHECK_INTERVAL)
