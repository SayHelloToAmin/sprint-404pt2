
import os
import json
from bs4 import BeautifulSoup

LINKS_FILE = "data/ad_links.json"

class BaseDetector:
    def __init__(self, city="tehran" , category="real-estate",  save_file=LINKS_FILE):
        self.city = city
        self.category = category
        self.base_url = f"https://divar.ir/s/{city}/{category}?page="
        self.save_file = save_file
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": f"https://divar.ir/s/{city}/{category}",
            "Accept": "text/html",
            "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive"
        }
        self.links = self.load_links()

    def load_links(self):
        if not os.path.exists(self.save_file):
            return set()
        with open(self.save_file, "r", encoding="utf-8") as f:
            return set(json.load(f))

    def save_links(self):
        with open(self.save_file, "w", encoding="utf-8") as f:
            json.dump(list(self.links) , f , ensure_ascii=False , indent=2)

    def extract_links_from_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        ads = soup.find_all("a" , href=True)
        page_links = set()
        for ad in ads:
            href = ad['href']
            if href.startswith("/v/"):
                full_link = "https://divar.ir" + href
                page_links.add(full_link)
        return page_links
