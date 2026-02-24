import re
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, date
import random

url = "https://en.wikipedia.org/wiki/List_of_K-pop_artists"

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
 "Accept-Language": "en-US,en;q=0.9"
}

response = requests.get(url, headers=headers)
print(response.status_code)

html = response.text
hub_soup = BeautifulSoup(html, "html.parser")

artist_urls = []

MAX_ARTISTS = 4000

time_start = time.time()
elapsed_time_list = []

with open("link_tester.txt", "w", encoding="utf-8") as file:

    for div in hub_soup.find_all("div", class_="div-col"):

        for a in div.select("li a"):

            href = a.get("href")

            if not href or not href.startswith("/wiki/"):
                continue

            if any(x in href for x in [":", "#", "Main_Page", "List_of", "Category"]):
                continue

            full_url = "https://en.wikipedia.org" + href

            artist_urls.append(full_url)

            file.write(full_url + "\n")   # <-- write link to file immediately
            file.flush()                 # <-- force save instantly

            if len(artist_urls) >= MAX_ARTISTS:
                break

