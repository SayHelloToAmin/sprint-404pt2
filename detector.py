import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

BASE_URL = "https://divar.ir/s/tehran/real-estate"
HEADERS = {"User-Agent": UserAgent().random}
LINKS_FILE = "ad_links.json"

def get_new_links():
    print("Loading the new ads - wait!")
    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    ad_links = set()
    for tag in soup.find_all("a", href=True):
        href = tag['href']
        if href.startswith("/v/"):
            ad_links.add("https://divar.ir" + href)

    return ad_links

print(get_new_links())
