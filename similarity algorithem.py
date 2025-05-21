import json
import difflib
import sqlite3
from itertools import combinations
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

class RealEstateSimilarityDetector:
    def __init__(self):
        self.weights = {
            'title': 0.15,
            'address': 0.2,
            'area': 0.1,
            'room_count': 0.1,
            'built_year': 0.1,
            'features': 0.15,
            'image_urls': 0.2
        }

    def _text_similarity(self, a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, a, b).ratio()

    def _numerical_similarity(self, a: float, b: float, max_diff=100.0) -> float:
        return 1 - min(abs(a - b) / max_diff, 1.0)

    def _boolean_features_similarity(self, features1: dict, features2: dict) -> float:
        keys = ['parking', 'anbari', 'balcony']
        matches = sum(1 for k in keys if features1.get(k) == features2.get(k))
        return matches / len(keys)

    def _image_similarity(self, imgs1: list, imgs2: list) -> float:
        return 1.0 if set(imgs1) & set(imgs2) else 0.0

    def _to_int(self, val):
        try:
            return int(val)
        except:
            return 0

    def compute_similarity(self, ad1: dict, ad2: dict) -> float:
        area1 = self._to_int(ad1['area'])
        area2 = self._to_int(ad2['area'])
        year1 = self._to_int(ad1['built_year'])
        year2 = self._to_int(ad2['built_year'])
        room1 = self._to_int(ad1['room_count'])
        room2 = self._to_int(ad2['room_count'])

        score = 0
        score += self._text_similarity(ad1['title'], ad2['title']) * self.weights['title']
        score += self._text_similarity(ad1['address'], ad2['address']) * self.weights['address']
        score += self._numerical_similarity(area1, area2, max(area1, area2)) * self.weights['area']
        score += (1.0 if room1 == room2 else 0.0) * self.weights['room_count']
        score += self._numerical_similarity(year1, year2) * self.weights['built_year']
        score += self._boolean_features_similarity(ad1['features'], ad2['features']) * self.weights['features']
        score += self._image_similarity(ad1['image_urls'], ad2['image_urls']) * self.weights['image_urls']

        return round(score * 100, 2)

def save_to_db(records):
    conn = sqlite3.connect("similar_ads.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS similar_ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad1_title TEXT,
            ad1_url TEXT,
            ad2_title TEXT,
            ad2_url TEXT,
            similarity_percent REAL
        )
    ''')

    for r in records:
        cursor.execute('''
            INSERT INTO similar_ads (ad1_title, ad1_url, ad2_title, ad2_url, similarity_percent)
            VALUES (?, ?, ?, ?, ?)
        ''', (r['ad1_title'], r['ad1_url'], r['ad2_title'], r['ad2_url'], r['similarity_percent']))

    conn.commit()
    conn.close()

def print_rich_table(results):
    table = Table(title="Ad Similarity Results", box=box.SIMPLE_HEAVY)
    table.add_column("Similarity (%)", style="magenta", justify="right")
    table.add_column("Ad 1 URL", style="green", overflow="fold")
    table.add_column("Ad 2 URL", style="green", overflow="fold")

    results = sorted(results, key=lambda x: x["similarity_percent"], reverse=True)

    for r in results:
        percent = r['similarity_percent']
        percent_color = "green" if percent > 80 else "yellow" if percent > 50 else "red"
        table.add_row(
            f"[{percent_color}]{percent}[/]",
            f"[link={r['ad1_url']}]Link 1[/]",
            f"[link={r['ad2_url']}]Link 2[/]",
        )

    console.print(table)


def main():
    with open('data/ads_cleaned.json', 'r', encoding='utf-8') as f:
        ads = json.load(f)

    detector = RealEstateSimilarityDetector()
    results = []

    for i, j in combinations(range(len(ads)), 2):
        sim = detector.compute_similarity(ads[i], ads[j])
        results.append({
            "ad1_title": ads[i]['title'],
            "ad1_url": ads[i]['url'],
            "ad2_title": ads[j]['title'],
            "ad2_url": ads[j]['url'],
            "similarity_percent": sim
        })

    print_rich_table(results)
    save_to_db(results)
    console.print("[bold green]Results saved to 'similar_ads.db'[/]")

if __name__ == '__main__':
    main()
