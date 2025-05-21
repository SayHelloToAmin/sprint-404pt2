
import asyncio
import requests
from .base import BaseDetector

class NewDetector(BaseDetector):
    async def run_periodically(self, interval=100):
        print("🔁 Start NewDetector for new ads")
        while True:
            try:
                res = requests.get(self.base_url + "0", headers=self.headers, timeout=10)
                if res.status_code != 200:
                    print(f"⚠️ Unsuccessful firstpage: {res.status_code}")
                    await asyncio.sleep(interval)
                    continue

                new_links = self.extract_links_from_html(res.text)
                before = len(self.links)
                self.links.update(new_links)
                added = len(self.links) - before

                if added > 0:
                    print(f"🆕 {added} A new ad has been added!")
                    self.save_links()
                else:
                    print("➖ There was no new ad.")

            except Exception as e:
                print("❌ error in NewDetector:", e)

            await asyncio.sleep(interval)
