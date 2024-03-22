import requests
from bs4 import BeautifulSoup
import pandas as pd
from parsing_scripts.diary_movie_genres import grab_diary_movie_genres
from parsing_scripts.diary_movie_directors import grab_diary_movie_director
from parsing_scripts.diary_movie_cast import grab_diary_movie_cast
from parsing_scripts.diary_movie_rating import grab_diary_movie_rating

def get_liked_movie_titles(username):
    liked_titles = []
    url = f"https://letterboxd.com/{username}/likes/films/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        parent_container = soup.find_all("li", class_="poster-container")
        for child in parent_container:
            img = child.find("img")
            if img and img.has_attr("alt"):
                liked_titles.append((img["alt"]).strip())
    
    return liked_titles


def update_liked_movies_in_diary_df(username, diary_df):
    liked_titles = get_liked_movie_titles(username)
    new_rows = []  

    for title in liked_titles:
        if title not in diary_df["title"].values:
            new_row = {
                "title": title, 
                "watched_date": pd.NA, 
                "genres": pd.NA,
                "director": pd.NA,
                "cast": pd.NA,
                "rating": pd.NA,
                "liked": True
            }
            new_rows.append(new_row)
        else:
            diary_df.loc[diary_df["title"] == title, "liked"] = True

    if new_rows:
        diary_df = pd.concat([diary_df, pd.DataFrame(new_rows)], ignore_index=True)

    diary_df = grab_diary_movie_genres(diary_df)
    diary_df = grab_diary_movie_director(diary_df)
    diary_df = grab_diary_movie_cast(diary_df)
    diary_df = grab_diary_movie_rating(username, diary_df)

    return diary_df