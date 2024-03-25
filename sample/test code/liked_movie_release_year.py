import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_release_year(title_slug):
    url = f"https://letterboxd.com/film/{title_slug}/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        year_container = soup.find("small", class_ = "number")

        if year_container:
            return year_container.find("a").text
    
    return None

def grab_liked_movie_release_year(liked_df):
    future_to_index = {}

    with ThreadPoolExecutor(max_workers = 50) as executor:
        for index, row in liked_df.iterrows():
            if pd.notna(row["title_slug"]):
                future = executor.submit(fetch_release_year, row["title_slug"])
                future_to_index[future] = index

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            year = future.result()
            if year:
                liked_df.at[index, "release_year"] = year

    return liked_df