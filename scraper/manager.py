import json
import asyncio
from pathlib import Path
from scraper.real_estate import RealEstateScraper


SCRAPED_FILE = "data/scraped_ads.json"
LINKS_FILE = "data/ad_links.json"

def is_valid_ad(data):
    if not data:
        return False
    return bool(data.get("title") or data.get("price_total"))


def load_scraped_links():
    if not Path(SCRAPED_FILE).exists():
        return set()
    with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return set(item["url"] for item in data)

def save_scraped_data(new_data):
    if Path(SCRAPED_FILE).exists():
        with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
            current = json.load(f)
    else:
        current = []

    current.extend(new_data)
    with open(SCRAPED_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)

async def run_scraper(interval=120, batch_size=35):
    scraper = RealEstateScraper()

    while True:
        try:
            with open(LINKS_FILE, "r", encoding="utf-8") as f:
                all_links = set(json.load(f))
            scraped_links = load_scraped_links()
            new_links = all_links - scraped_links

            print(f"🔎 {len(new_links)} New link for review")

            results = []
            for link in list(new_links)[:batch_size]:
                data = scraper.scrape_ad(link)
                if is_valid_ad(data):
                    results.append(data)
                else:
                    pass
                await asyncio.sleep(2)

            if results:
                save_scraped_data(results)
                print(f"✅ {len(results)} New ad saved")

        except Exception as e:
            print("❌ Error in Scraper:", e)

        await asyncio.sleep(interval)
