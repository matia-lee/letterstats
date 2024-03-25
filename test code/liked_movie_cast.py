import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_cast(title_slug):
    url = f"https://letterboxd.com/film/{title_slug}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        cast_main_container = soup.find("div", class_="cast-list text-sluglist")
        if cast_main_container:
            cast_members = [a.text.strip() for a in cast_main_container.find_all("a", class_="text-slug")]
            return ", ".join(cast_members)
    return None

from concurrent.futures import ThreadPoolExecutor, as_completed

def grab_liked_movie_cast(liked_df):
    future_to_index = {}

    with ThreadPoolExecutor(max_workers=50) as executor: 
        for index, row in liked_df.iterrows():
            if pd.notna(row["title_slug"]):
                future = executor.submit(fetch_cast, row["title_slug"])
                future_to_index[future] = index

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            cast = future.result()
            if cast:
                liked_df.at[index, "cast"] = cast

    return liked_df
