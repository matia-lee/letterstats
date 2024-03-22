import requests
from bs4 import BeautifulSoup
from parsing_scripts.diary_movie_genres import format_title_to_url_slug

def grab_diary_movie_cast(diary_df):
    for index, row in diary_df.iterrows():
        title_slug = format_title_to_url_slug(row["title_slug"])
        url = f"https://letterboxd.com/film/{title_slug}/"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            cast_main_container = soup.find("div", class_="cast-list text-sluglist")
            if cast_main_container:
                cast = [a.text for a in cast_main_container.find_all("a", class_="text-slug")]
                diary_df.at[index, "cast"] = ", ".join(cast)

    return diary_df