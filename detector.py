import requests
import json
import os


class DetectorBase:
    def __init__(self, city="tehran", category="real-estate", save_file="ad_links.json"):
        self.city = city
        self.category = category
        self.save_file = save_file
        self.base_url = f"https://api.divar.ir/v8/web-search/{self.city}/{self.category}"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }
        self.old_links = self.load_old_links()

    def load_old_links(self):
        if not os.path.exists(self.save_file):
            return set()
        with open(self.save_file,"r") as f:
            return set(json.load(f))

    def save_links(self, links):
        with open(self.save_file,"w") as f:
            json.dump(list(links),f, ensure_ascii=False,indent=2)

    def extract_links_from_page(self,page):
        try:
            url = f"{self.base_url}?page={page}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"i cant find this page ! {page}")
                return set()

            data = response.json()
            posts = data.get("web_widgets", {}).get("post_list", {}).get("items", [])
            links = set()
            for post in posts:
                token = post.get("data", {}).get("token")
                if token:
                    links.add(f"https://divar.ir/v/{token}")
            return links
        except Exception as e:
            print("unspected error !", e)
            return set()