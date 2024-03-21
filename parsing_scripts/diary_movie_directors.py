import requests
from bs4 import BeautifulSoup
from parsing_scripts.diary_movie_genres import format_title_to_url_slug

def grab_diary_movie_director(diary_df):
    for index, row in diary_df.iterrows():
        title_slug = format_title_to_url_slug(row["title"])
        url = f"https://letterboxd.com/film/{title_slug}/crew/"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            genre_main_container = soup.find("div", {"id": "tab-crew"})
            if genre_main_container:
                genre_container = genre_main_container.find("div", class_="text-sluglist")
                if genre_container:
                    director = genre_container.find("a", class_="text-slug")
                    diary_df.at[index, "director"] = ", ".join(director)
    return diary_df