import requests
from bs4 import BeautifulSoup
import re

def format_title_to_url_slug(title):
    slug = title.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    return slug

def grab_diary_movie_genres(diary_df):
    for index, row in diary_df.iterrows():
        title_slug = format_title_to_url_slug(row['title'])
        url = f"https://letterboxd.com/film/{title_slug}/genres/"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            genre_main_container = soup.find("div", {"id": "tab-genres"})
            if genre_main_container:
                genre_container = genre_main_container.find("div", class_="text-sluglist")
                if genre_container:
                    genres = [a.text for a in genre_container.find_all("a", class_="text-slug")]
                    diary_df.at[index, 'genres'] = ", ".join(genres)
    return diary_df