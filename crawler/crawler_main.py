import re
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, date
import random

HUB_URL = "https://en.wikipedia.org/wiki/List_of_K-pop_artists"

def get_allowed_urls():
    """Fetches the hub page and returns a set of all valid artist URLs."""
    try:
        response = requests.get(HUB_URL, headers=headers, timeout=10)
        hub_soup = BeautifulSoup(response.text, "html.parser")
        allowed = set()
        
        for div in hub_soup.find_all("div", class_="div-col"):
            for a in div.select("li a"):
                href = a.get("href")
                if href and href.startswith("/wiki/"):
                    if not any(x in href for x in [":", "#", "Main_Page", "List_of", "Category"]):
                        allowed.add("https://en.wikipedia.org" + href)
        return allowed
    except Exception:
        return set()
    
def get_random_artist():
    allowed_links = get_allowed_urls()
    if not allowed_links:
        return None
    return random.choice(list(allowed_links))

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}
nationalities = ['Korean','South Korean','Japanese','Thai','Chinese','American','Canadian','Australian','British','Taiwanese','Hong Kong','Filipino']

nationality_pattern = r"\b(" + "|".join(nationalities) + r")\b"


def clean_text(text):
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    return text.strip()


def clean_year(text):
    text = re.sub(r"\[\s*\d+\s*\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def crawl(url=None,randomize=False):
    allowed_links = get_allowed_urls()
    if randomize:
        url = get_random_artist()
    print("Crawling:", url, 'randomize:', randomize)
    if url not in allowed_links:
        # Return a specific error structure that React can detect
        return {"error_goofed": "Invalid Link", "message": "This link is not in the official K-pop artist list."}
    
    ARTIST_URL = url
    
    response_artist = requests.get(ARTIST_URL, headers=headers,timeout=30)
    soup_artist = BeautifulSoup(response_artist.text, "html.parser")

    infobox = soup_artist.select_one("table.infobox")

    if infobox is None:
        exit()

    # --- FIRST PARAGRAPH ---
    p_html = None
    p_block = None

    for p in soup_artist.find_all("p"):
        if p.text.strip():
            p_block = p
            p_html = str(p)
            break


    # --- STAGE NAME ---
    stage_name_match = re.search(r"<title>(.*?) - Wikipedia", response_artist.text)

    if stage_name_match:
        name = stage_name_match.group(1)


    # --- FULL NAME ---
    full_name_match = infobox.find("div", class_="nickname")

    if full_name_match is None:
        if p_html:
            full_name_match = re.search(r"<b>(.*?)</b>", p_html)
            if full_name_match:
                full_name_match = full_name_match.group(1)
    else:
        full_name_match = full_name_match.text.strip()
    if full_name_match:
        full_name_match = clean_text(full_name_match)



    # --- GENDER ---
    gender = "Unknown"

    if p_block:
        p_text = p_block.get_text(" ", strip=True)

        if re.search(r"\b(he|his)\b", p_text, re.IGNORECASE):
            gender = "Male"
        elif re.search(r"\b(she|her)\b", p_text, re.IGNORECASE):
            gender = "Female"




    # --- BIRTH YEAR ---
    birth_match = infobox.find("span", class_="bday")
    birth_year = None

    if birth_match:
        birth_year = birth_match.get_text(strip=True)
    else:
        born_row = infobox.find("th", string=lambda x: x and "Born" in x)

        if born_row:
            born_data = born_row.find_next("td")
            born_text = born_data.get_text(" ", strip=True)

            year_match = re.search(r"\b(19|20)\d{2}\b", born_text)

            if year_match:
                birth_year = year_match.group(0)



    # --- AGE ---
    if birth_year:

        if re.match(r"^\d{4}$", birth_year):
            birth_year = f"{birth_year}-01-01"

        birth_date = datetime.strptime(birth_year, "%Y-%m-%d").date()

        today = date.today()

        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    else:
        age = "Unknown"



    # --- NATIONALITY ---
    nationality = "Not Found"

    if p_html:
        match = re.search(nationality_pattern, p_html)

        if match:
            nationality = match.group(1)



    # --- OCCUPATION ---
    occupations = "Not found"

    for row in infobox.find_all("tr"):
        label = row.find("th", class_="infobox-label")

        if label and "Occupation" in label.text:
            data_cell = row.find("td")

            if data_cell:
                items = data_cell.find_all("li")
                occupations = ", ".join([clean_text(i.text.strip()) for i in items])

            break

    #group name
    group_name = "None"
    if p_block:
        for a in p_block.find_all("a"):
            group_url = a.get("href")
            if not group_url or not group_url.startswith("/wiki/"):
                continue
            group_url = "https://en.wikipedia.org" + group_url
            
            try:
                time.sleep(2)
                group_response = requests.get(group_url, headers=headers)
                group_soup = BeautifulSoup(group_response.text, "html.parser")
                members_exists = False
                is_active = False
                infobox = group_soup.select_one("table.infobox")
                if infobox:
                    for row in infobox.find_all("tr"):
                        label = row.find("th", class_="infobox-label")
                        if not label:
                            continue
                        # --- Check members box ---
                        if "Members" in label.text:
                            members_cell = row.find("td")

                            if members_cell:
                                for li in members_cell.find_all("li"):
                                    href = li.find("a").get("href")
                                    if 'https://en.wikipedia.org' + href == ARTIST_URL:
                                        members_exists = True
                                        break

                                # --- Check years active ---
                        if "Years active" in label.text:
                            years_cell = row.find("td")
                            if years_cell and "present" in years_cell.text.lower():
                                is_active = True

                discography_exists = group_soup.find(id="Discography") is not None

                if members_exists and discography_exists and is_active:
                    group_name = a.get_text(strip=True)
                    break

            except:
                continue

    # --- GENRE ---
    genre = "K-Pop"

    for row in infobox.find_all("tr"):
        label = row.find("th", class_="infobox-label")

        if label and "Genres" in label.text:
            data_cell = row.find("td")

            if data_cell:

                items = data_cell.find_all("li")

                if items:
                    genre = ", ".join([clean_text(i.get_text(strip=True)) for i in items])

                else:
                    links = data_cell.find_all("a")
                    genre = ", ".join([clean_text(link.get_text(strip=True)) for link in links])

            break

    return {
        "stage name": name,
        "full name": full_name_match,
        "gender": gender,
        "birth year": birth_year,
        "age": age,
        "nationality": nationality,
        "occupations": occupations,
        "group name": group_name,
        "genre": genre
    }
