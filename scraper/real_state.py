import requests
from bs4 import BeautifulSoup
import re

class RealEstateScraper:
    def __init__(self, headers=None):
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "fa-IR,fa;q=0.9",
        }

    def scrape_ad(self, url):
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code != 200:
                print(f"⛔ The ad did not open: {url}")
                return None

            soup = BeautifulSoup(res.text, "html.parser")

            area, built_year, room_count = self.extract_area_room_year(soup)

            data = {
                "url": url,
                "title": self.extract_title(soup),
                "address": self.extract_address(soup),
                "price_total": self.extract_any_price(soup),
                "area": area,
                "room_count": room_count,
                "built_year": built_year,
                "features": self.extract_features(soup),
                "images": self.extract_images(soup)
            }

            return data

        except Exception as e:
            print(f"❌ Error in extracting the ad {url}: {e}")
            return None

    def extract_title(self, soup):
        tag = soup.find("h1", class_="kt-page-title__title")
        return tag.get_text(strip=True) if tag else None

    def extract_address(self, soup):
        subtitle = soup.find("div", class_="kt-page-title__subtitle")
        if not subtitle:
            return None
        text = subtitle.get_text(strip=True)
        if " در " in text:
            return text.split(" در ", 1)[1]
        return text

    def extract_area_room_year(self, soup):
        table = soup.find("table", class_="kt-group-row")
        if not table:
            return None, None, None
        try:
            tds = table.find_all("td")
            area = tds[0].text.strip() if len(tds) > 0 else None
            built_year = tds[1].text.strip() if len(tds) > 1 else None
            room_count = tds[2].text.strip() if len(tds) > 2 else None
            return area, built_year, room_count
        except:
            return None, None, None

    def extract_any_price(self , soup):
        rows = soup.find_all("div", class_="kt-base-row")
        for row in rows:
            value = row.find("p", class_="kt-unexpandable-row__value")
            if value:
                text = value.text.strip()
                if "تومان" in text:
                    return text
        return None

    def extract_features(self , soup):
        tables = soup.find_all("table", class_="kt-group-row")
        if len(tables) < 2:
            return []
        try:
            feature_table = tables[1]
            features = [td.text.strip() for td in feature_table.find_all("td")]
            return features
        except:
            return []

    def extract_images(self , soup):
        image_tags = soup.find_all("img")
        image_links = []
        for img in image_tags:
            src = img.get("src")
            if src and "divarcdn.com" in src:
                image_links.append(src)
        return list(set(image_links))
