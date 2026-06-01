import cloudscraper
from bs4 import BeautifulSoup
import time
import requests

# Configuration
# UPDATED: Using Tori's modern recommerce search domain layout
SEARCH_URL = "https://tori.fi"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1510984092123004979/nd58I_eU5LqY6TL0Xc9yn12kHHaiuC-bOMz7GrxWs4iDtioJGsaRYZ-VCYnz2tfgCkt3" # Make sure your link is here!

def send_discord_alert(title, price, url, image_url=None):
    payload = {
        "content": f"🚨 **New Pokémon Card Listing!** 🚨\n**Title:** {title}\n**Price:** {price}\n**Link:** {url}"
    }
    if image_url:
        payload["embeds"] = [{"image": {"url": image_url}}]
        
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"Alert sent successfully for: {title}")
        else:
            print(f"Discord API returned status code: {response.status_code}")
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")

def check_tori():
    print("Scanning Tori.fi's new layout structure...")
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    try:
        response = scraper.get(SEARCH_URL)
        if response.status_code != 200:
            print(f"Tori wall block. HTTP Status: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # New target element layouts for Tori's updated search grid
        listings = soup.find_all(['article', 'div', 'a'], href=lambda h: h and '/ilmoitus/' in h)
        print(f"Found {len(listings)} raw tracking structures on page.")

        for item in listings:
            try:
                # Extract URL securely
                url = item['href'] if item.name == 'a' else item.find('a', href=True)['href']
                if url.startswith('/'):
                    url = "https://www.tori.fi" + url
                
                # Fetch text segments
                title_el = item.find(['h2', 'h3', 'p', 'span'], class_=lambda c: c and ('title' in c or 'subject' in c))
                title = title_el.text.strip() if title_el else "New Pokémon Listing"
                
                # Fallback title if element selector changes
                if title == "New Pokémon Listing" and item.text:
                    title = item.text.strip().split('\n')[0]

                # Price tracking locator
                price = "Check site"
                for text_node in item.find_all(text=True):
                    if '€' in text_node:
                        price = text_node.strip()
                        break

                # Since GitHub forgets database history, we force alert the top fresh items
                print(f"Processing listing: {title} - {price}")
                send_discord_alert(title, price, url)
                
                # We only want to process the absolute newest item on top to avoid spam loops
                break 
                
            except Exception as inner_e:
                print(f"Skip structural row error: {inner_e}")
                continue
                
    except Exception as e:
        print(f"Scraper core issue: {e}")

if __name__ == "__main__":
    check_tori()
