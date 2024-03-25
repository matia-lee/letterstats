import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_directors(title_slug):
    url = f"https://letterboxd.com/film/{title_slug}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        crew_container = soup.find("div", {"id": "tab-crew"})
        if crew_container:
            director_container = crew_container.find("div", class_="text-sluglist")
            if director_container:
                directors = [a.text for a in director_container.find_all("a", class_="text-slug")]
                return ", ".join(directors)
    return None

from concurrent.futures import ThreadPoolExecutor, as_completed

def grab_liked_movie_director(liked_df):
    future_to_index = {}

    with ThreadPoolExecutor(max_workers=50) as executor:  
        for index, row in liked_df.iterrows():
            if pd.notna(row["title_slug"]):
                future = executor.submit(fetch_directors, row["title_slug"])
                future_to_index[future] = index

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            directors = future.result()
            if directors:
                liked_df.at[index, "director"] = directors

    return liked_df
