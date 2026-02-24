import re
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, date
import random

# Single artist page for debugging
url = "https://en.wikipedia.org/wiki/Hongseok"

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
 "Accept-Language": "en-US,en;q=0.9"
}

with open("nationalities.txt") as f:
    nationalities = [line.strip() for line in f]

nationality_pattern = r"\b(" + "|".join(nationalities) + r")\b"

# Only crawl this single artist
artist_urls = [url]

file = open("dataset_test.txt", "w", encoding="utf-8")

#--------------------------------------------------------------------------------------------------------------
def clean_text(text):
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    return text.strip()
#--------------------------------------------------------------------------------------------------------------

for url in artist_urls:

    print("Testing:", url)

    response_artist = requests.get(url, headers=headers)
    soup_artist = BeautifulSoup(response_artist.text, "html.parser")

    print_string = ''

    infobox = soup_artist.select_one("table.infobox")

    p_html = None
    p_block = None
    for p in soup_artist.find_all("p"):
        if p.text.strip():
            p_block = p
            p_html = str(p)
            break

#--------------------------------------------------------------------------------------------------------------
    stage_name_match = re.search(r"<title>(.*?) - Wikipedia", response_artist.text)

    if stage_name_match:
        name = stage_name_match.group(1)
        print_string += f"Stage Name: {name} | "
    else:
        print_string += "Stage Name: Not found | "

#--------------------------------------------------------------------------------------------------------------
    full_name_match = infobox.find("div", class_="nickname") if infobox else None
    if full_name_match is None:
        if p_html:
            full_name_match = re.search(r"<b>(.*?)</b>", p_html)
            if full_name_match:
                full_name_match = full_name_match.group(1)

    else:
        full_name_match = full_name_match.text.strip()

        if re.search(r"[^A-Za-z\- ]", full_name_match):
            if p_html:
                alt_match = re.search(r"<b>(.*?)</b>", p_html)
                if alt_match:
                    full_name_match = alt_match.group(1)
    if full_name_match:
        full_name_match = clean_text(full_name_match)
        print_string += f"Full Name: {full_name_match} | "
    else:
        print_string += "Full Name: Not found | "

#--------------------------------------------------------------------------------------------------------------
    birth_match = infobox.find("span", class_="bday") if infobox else None
    birth_year = None

    if birth_match:
        birth_year = birth_match.get_text(strip=True)

    else:
        if infobox:
            born_row = infobox.find("th", string=lambda x: x and "Born" in x)

            if born_row:
                born_data = born_row.find_next("td")
                born_text = born_data.get_text(" ", strip=True)

                year_match = re.search(r"\b(19|20)\d{2}\b", born_text)
                if year_match:
                    birth_year = year_match.group(0)

    if birth_year:
        print_string += f"Birth Year: {birth_year} | "
    else:
        print_string += "Birth Year: Not found | "

#--------------------------------------------------------------------------------------------------------------
    if birth_year:
        if re.match(r"^\d{4}$", birth_year):
            birth_year = f"{birth_year}-01-01"
        elif re.match(r"^\d{4}-\d{2}$", birth_year):
            birth_year = f"{birth_year}-01"

        birth_date = datetime.strptime(birth_year, "%Y-%m-%d").date()
        today = date.today()

        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    else:
        age = "Unknown"

    print_string += f"Age: {age} | "

#--------------------------------------------------------------------------------------------------------------
    bplace_match = infobox.find("div", class_="birthplace") if infobox else None

    if bplace_match:
        birth_place = bplace_match.text.strip()
        birth_place = clean_text(birth_place)
        print_string += f"Birth Place: {birth_place} | "
    else:
        print_string += "Birth Place: Unknown | "

#--------------------------------------------------------------------------------------------------------------
    if p_html:
        nationality = 'Not Found'
        paragraph_text = p_html
        match = re.search(nationality_pattern, paragraph_text)

        if match:
            nationality = match.group(1)

        print_string += f"Nationality: {nationality} | "

#--------------------------------------------------------------------------------------------------------------
    occupations = "Not found"

    if infobox:
        for row in infobox.find_all("tr"):
            label = row.find("th", class_="infobox-label")

            if label and "Occupation" in label.text:
                data_cell = row.find("td", class_="infobox-data")

                if data_cell:
                    items = data_cell.find_all("li")
                    occupations = ", ".join([clean_text(item.text.strip()) for item in items])

                break

    print_string += f"Occupation(s): {occupations} | "

#--------------------------------------------------------------------------------------------------------------
    years_active = "Not found"

    if infobox:
        for row in infobox.find_all("tr"):
            label = row.find("th", class_="infobox-label")

            if label:
                label_text = label.get_text(strip=True).replace("\xa0", " ")

                if "Years active" in label_text:
                    data_cell = row.find("td", class_="infobox-data")

                    if data_cell:
                        years_active = data_cell.get_text(" ", strip=True)

                    break

    print_string += f"Years Active: {years_active} | "

#--------------------------------------------------------------------------------------------------------------
    group_name = "None"

    if p_block:
        for a in p_block.find_all("a"):

            group_url = a.get("href")

            if not group_url or not group_url.startswith("/wiki/"):
                continue

            group_url = "https://en.wikipedia.org" + group_url

            try:
                group_response = requests.get(group_url, headers=headers)
                group_soup = BeautifulSoup(group_response.text, "html.parser")

                # Check for "Members" in infobox
                members_exists = False
                infobox = group_soup.select_one("table.infobox")

                if infobox:
                    for row in infobox.find_all("tr"):
                        label = row.find("th", class_="infobox-label")
                        if label and "Members" in label.text:
                            members_exists = True
                            break

                # Check if Discography section exists
                discography_exists = group_soup.find(id="Discography") is not None

                # If both conditions satisfied → this is a group
                if members_exists and discography_exists:
                    group_name = a.get_text(strip=True)
                    break

            except:
                continue

    print_string += f"Group: {group_name} | "

#--------------------------------------------------------------------------------------------------------------
    genre = "Not found"

    if infobox:
        for row in infobox.find_all("tr"):
            label = row.find("th", class_="infobox-label")

            if label and "Genres" in label.text:
                data_cell = row.find("td", class_="infobox-data")

                if data_cell:
                    items = data_cell.find_all("li")
                    genre = ", ".join([clean_text(item.text.strip()) for item in items])

                break

    print_string += f"Genre: {genre} | "

#--------------------------------------------------------------------------------------------------------------
print(print_string)
file.write(print_string + "\n")

time.sleep(random.uniform(0.5,0.7))

file.close()