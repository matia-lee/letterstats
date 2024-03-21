import requests
from bs4 import BeautifulSoup
import pandas as pd

def grab_dates_from_diaries(username, diary_df):
    entries = []
    current_month = "n/a"
    current_year = "n/a"

    url = f"https://letterboxd.com/{username}/films/diary/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        diary_entries_raw = soup.find_all("tr", class_="diary-entry-row")

        for movie_entry in diary_entries_raw:
            movie_info = {}

            title_container = movie_entry.find("td", class_="td-film-details")
            if title_container:
                title_element = title_container.find("h3", class_="headline-3").find("a")
                if title_element:
                    movie_info["title"] = title_element.text

            date_info = movie_entry.find("td", class_="td-calendar")
            if date_info:
                month = date_info.find("a")
                year = date_info.find("small")
                if month and year:
                    current_month = month.text
                    current_year = year.text

            day_info = movie_entry.find("td", class_="td-day")
            if day_info:
                day = day_info.find("a").text

            movie_info["watched_date"] = f"{day} {current_month} {current_year}"

            if "title" in movie_info and "watched_date" in movie_info:
                entries.append(movie_info)

    diary_df = pd.DataFrame(entries)

    return diary_df