import requests
from bs4 import BeautifulSoup

def grab_diary_movie_release_year(username, diary_df):
    url = f"https://letterboxd.com/{username}/films/diary/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        diary_entries = soup.find_all("tr", class_="diary-entry-row")

        release_years = []

        for entry in diary_entries:
            release_year_container = entry.find("td", class_="td-released")

            if release_year_container:
                release_year = release_year_container.find("span").text.strip()
                release_years.append(release_year)

        diary_df["release_year"] = release_years

    return diary_df