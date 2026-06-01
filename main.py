import cloudscraper
import requests
import time

# Direct API endpoint for 'pokemon kortit' sorted by newest
API_URL = "https://tori.fi"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1510984092123004979/nd58I_eU5LqY6TL0Xc9yn12kHHaiuC-bOMz7GrxWs4iDtioJGsaRYZ-VCYnz2tfgCkt3" # Put your webhook link here!

def send_discord_alert(title, price, url, image_url=None):
    embed = {
        "title": "🚨 New Pokémon Card Listing! 🚨",
        "description": f"**Item:** {title}\n**Price:** {price}\n\n[👉 Open Listing on Tori.fi]({url})",
        "color": 16711680 # Red color block
    }
    if image_url:
        embed["image"] = {"url": image_url}

    payload = {"embeds": [embed]}
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print(f"Discord responded with status: {res.status_code}")
    except Exception as e:
        print(f"Discord error: {e}")

def check_tori():
    print("Fetching directly from Tori.fi API network...")
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    try:
        response = scraper.get(API_URL)
        if response.status_code != 200:
            print(f"API Blocked. Status: {response.status_code}")
            return

        data = response.json()
        listings = data.get('listings', [])
        print(f"Successfully retrieved {len(listings)} listings from API.")

        if not listings:
            print("No items found in the current API feed.")
            return

        # Grab the absolute newest listing sitting on top of the pile
        newest_item = listings[0]
        
        title = newest_item.get('title', 'Pokémon Card Bundle')
        
        # Safely parse the price structure
        price_info = newest_item.get('price', {})
        amount = price_info.get('amount')
        price = f"{amount}€" if amount else "Check price on site"
        
        # Build full clean listing URL
        url = newest_item.get('url', '')
        if url.startswith('/'):
            url = "https://tori.fi" + url

        # Safely pull the main display picture if it exists
        image_url = None
        images = newest_item.get('images', [])
        if images:
            image_url = images[0].get('url')

        print(f"Sending top item to Discord: {title} - {price}")
        send_discord_alert(title, price, url, image_url)

    except Exception as e:
        print(f"Core execution error: {e}")

if __name__ == "__main__":
    check_tori()
