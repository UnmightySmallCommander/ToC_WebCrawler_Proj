import re
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, date
import random

headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",  # Pretend the request comes from a real browser
 "Accept-Language": "en-US,en;q=0.9"
}

# --- 1. Configuration & Setup ---
MAX_ARTISTS = 4000
IN_ORDER = True 
HUB_URL = "https://en.wikipedia.org/wiki/List_of_K-pop_artists" # Replace with your target URL
HEADERS = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
 "Accept-Language": "en-US,en;q=0.9"
}
FILE = open("dataset.txt", "w", encoding="utf-8")
FULL_DETAILS = False
TIME_TELL = True  
# Load nationalities for regex
with open("nationalities.txt") as f:
    nationalities = [line.strip() for line in f]
nationality_pattern = r"\b(" + "|".join(nationalities) + r")\b"

# --- 2. Fetch Hub Page & Collect URLs ---
response = requests.get(HUB_URL, headers=HEADERS)
if response.status_code != 200:
    print(f"Failed to reach hub page. Status: {response.status_code}")
    exit()

hub_soup = BeautifulSoup(response.text, "html.parser")
artist_urls = []  # Using a set to automatically ignore duplicates

for div in hub_soup.find_all("div", class_="div-col"):
    for a in div.select("li a"):
        href = a.get("href")
        
        # Validation
        if href and href.startswith("/wiki/"):
            if not any(x in href for x in [":", "#", "Main_Page", "List_of", "Category"]):
                artist_urls.append("https://en.wikipedia.org" + href)

if not IN_ORDER:
    random.shuffle(artist_urls)

artist_urls = artist_urls[:MAX_ARTISTS]

print(f"Collected {len(artist_urls)} unique artist URLs")
print(f"Estimated time to crawl: {len(artist_urls) * 5} seconds (assuming 5s delay)")

#--------------------------------------------------------------------------------------------------------------
def clean_text(text):
    text = re.sub(r"\[\d+\]", "", text)  # Remove reference numbers like [1]
    text = re.sub(r"\(.*?\)", "", text)  # Remove text inside parentheses
    return text.strip()  # Remove extra whitespace

def clean_year(text):
    text = re.sub(r"\[\s*\d+\s*\]", "", text)  # remove references
    text = re.sub(r"\s+", " ", text)
    return text.strip()
#--------------------------------------------------------------------------------------------------------------
current_artist = 0  # Counter to track how many artists we've processed
elapsed_time_list = [] # List to store elapsed time for each artist for later analysis
time_start = time.time() # Start timer for entire crawling process
#--------------------------------------------------------------------------------------------------------------
for i, url in enumerate(artist_urls, 1):
    elapsed_time = time.time()
    current_artist = i
    response_artist = requests.get(url, headers=headers)  # Request artist page
    soup_artist = BeautifulSoup(response_artist.text, "html.parser")  # Parse the page

    print_string = ''  # String used to store the final output line
    print_string += f"Artist {current_artist}/{len(artist_urls)} | "  # Add progress info to output
    infobox = soup_artist.select_one("table.infobox")  # Find the Wikipedia infobox containing artist info
    if infobox is None: 
        print_string += "Infobox: Not found"
        continue  # Skip if no infobox found, since it likely won't have the needed info
    p_html = None #First paragraph usually has most contents needed
    p_block = None
    for p in soup_artist.find_all("p"):  # Search through paragraphs
        if p.text.strip():  # Skip empty paragraphs
            p_block = p
            p_html = str(p)
            break
#--------------------------------------------------------------------------------------------------------------
    stage_name_match = re.search(r"<title>(.*?) - Wikipedia", response_artist.text)  # Extract page title using regex

    if stage_name_match:
        name = stage_name_match.group(1)  # Extract stage name from regex group
        print_string += f"Stage Name: {name} | "
    else:
        print_string += "Stage Name: Not found | "

#--------------------------------------------------------------------------------------------------------------
    full_name_match = infobox.find("div", class_="nickname") if infobox else None # Try to find full name in infobox first
    if full_name_match is None: # If not found in infobox, try to find it in the first paragraph
        if p_html:
            full_name_match = re.search(r"<b>(.*?)</b>", p_html)
            if full_name_match:
                full_name_match = full_name_match.group(1)
    else: # If full name is found in infobox, check if it contains non-standard characters. If it does, try to find an alternative full name in the first paragraph.
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
    gender = "Unknown"

    if p_block:
        p_text = p_block.get_text(" ", strip=True)

        if re.search(r"\b(he|his)\b", p_text, re.IGNORECASE):
            gender = "Male"
        elif re.search(r"\b(she|her)\b", p_text, re.IGNORECASE):
            gender = "Female"

    print_string += f"Gender: {gender} | "
#--------------------------------------------------------------------------------------------------------------
    birth_match = infobox.find("span", class_="bday") # Try to find birth date in infobox first
    birth_year = None

    if birth_match: # If birth date is found in infobox, extract the year
        birth_year = birth_match.get_text(strip=True) 

    else: # If birth date is not found in infobox, try to find it in the "Born" row of the infobox
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
        if re.match(r"^\d{4}$", birth_year):          # case: "1988"
            birth_year = f"{birth_year}-01-01"        # set month/day to Jan 1
        elif re.match(r"^\d{4}-\d{2}$", birth_year):  # case: "1988-10"
            birth_year = f"{birth_year}-01"           # set day to 1
        birth_date = datetime.strptime(birth_year, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    else:
        age = "Unknown"
    print_string += f"Age: {age} | "
#--------------------------------------------------------------------------------------------------------------
    bplace_match = infobox.find("div", class_="birthplace")  # Locate birth place in infobox

    if bplace_match:
        birth_place = bplace_match.text.strip()  # Extract birth place text
        birth_place = clean_text(birth_place)
        print_string += f"Birth Place: {birth_place} | "
    else:
        print_string += "Birth Place: Unknown | "
#--------------------------------------------------------------------------------------------------------------
    if p_html:
        nationalities = 'Not Found'
        paragraph_text = p_html
        match = re.search(nationality_pattern, paragraph_text)
        if match:
            nationality = match.group(1)
        else:
            nationality = 'Not Found'
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
                        years_active = clean_text(years_active)
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
                time.sleep(random.uniform(0.5,0.7))
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

                    if items:  # Case 1: genres inside <li>
                        genre = ", ".join([clean_text(item.get_text(strip=True)) for item in items])

                    else:  # Case 2: genres are just links
                        links = data_cell.find_all("a")
                        genre = ", ".join([clean_text(link.get_text(strip=True)) for link in links])

                break

    if genre == "Not found" or genre == "":  # If genre not found in infobox, try to find it in the first paragraph
        genre = 'K-pop'  # Default to K-pop if not found, since we're on a K-pop artists page

    print_string += f"Genre: {genre} | "
#--------------------------------------------------------------------------------------------------------------
    FILE.write(print_string + "\n")  # Write data to file
    FILE.flush()
    if not FULL_DETAILS:
       print_string = f"Artist {current_artist}/{len(artist_urls)} | {url} | "
    if TIME_TELL: 
        print_string += f"Elapsed Time: {time.time() - elapsed_time:.2f} seconds"  # Add elapsed time for this artist to output
    elapsed_time_list.append(time.time() - elapsed_time)  # Store elapsed time in list for later analysis
    print(print_string)  # Print collected data
    time.sleep(random.uniform(0.5,0.7))  # Wait 1 second between requests to avoid overloading Wikipedia
FILE.close()
print(f"Crawling completed in {time.time() - time_start:.2f} seconds")  # Print how long the crawling took
print(f"Average time per artist: {sum(elapsed_time_list)/len(elapsed_time_list):.2f} seconds")  # Print average time per artist
