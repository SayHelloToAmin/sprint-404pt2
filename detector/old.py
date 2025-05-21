import requests
import time
import random
from .base import BaseDetector

class OldDetector(BaseDetector):
    def run(self , max_pages=200, delay_range=(3, 6), max_empty=5):
        print("📦 OldDetector started working to identify old links.")
        empty_count = 0

        for page in range(max_pages):
            print(f"📄 Page {page}")
            url = self.base_url + str(page)

            try:
                res = requests.get(url, headers=self.headers, timeout=10)
                if res.status_code != 200:
                    print(f"⚠️ Unsuccessful receipt: {res.status_code}")
                    continue

                new_links = self.extract_links_from_html(res.text)
                before = len(self.links)
                self.links.update(new_links)
                added = len(self.links) - before

                if added == 0:
                    empty_count += 1
                    print(f"⛔ There was no new link. ({empty_count})")
                else:
                    empty_count = 0
                    print(f"✅ {added} New Link")

                if empty_count >= max_empty and page >= 20:
                    print("🛑 Stopped: 5 consecutive pages without a new link (after 20 pages)")
                    break

                self.save_links()
                time.sleep(random.uniform(*delay_range))

            except Exception as e:
                print("❌ error:", e)

        print(f"\n🎯 End of OldDetector - all links: {len(self.links)}")
        self.save_links()
