import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# def grab_liked_movie_release_year(liked_df):
#     for index, row in liked_df.iterrows():
#         title = row["title_slug"]

#         url = f"https://letterboxd.com/film/{title}/"
#         response = requests.get(url)

#         if response.status_code == 200:
#             soup = BeautifulSoup(response.text, "lxml")
#             year_container = soup.find("small", class_ = "number")
            
#             if year_container:
#                 year = year_container.find("a").text
#                 liked_df.at[index, "release_year"] = year

#     return liked_df


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

# from concurrent.futures import ThreadPoolExecutor, as_completed
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd

# def fetch_release_year(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "lxml")
#         year_container = soup.find("small", class_="number")
#         if year_container:
#             return year_container.find("a").text
#     return None

# def grab_liked_movie_release_year(liked_df):
#     # Create a list of URLs to fetch
#     urls = [f"https://letterboxd.com/film/{slug}/" for slug in liked_df["title_slug"] if pd.notna(slug)]

#     print(urls)

#     # Use ThreadPoolExecutor to fetch data in parallel
#     with ThreadPoolExecutor(max_workers=100) as executor:
#         future_to_url = {executor.submit(fetch_release_year, url): url for url in urls}
#         for future in as_completed(future_to_url):
#             url = future_to_url[future]
#             try:
#                 year = future.result()
#                 if year:
#                     # Find the index in liked_df that corresponds to this URL and update the year
#                     index = liked_df[liked_df["title_slug"] == url.split("/film/")[1].rstrip("/")].index
#                     if not index.empty:
#                         liked_df.at[index[0], "release_year"] = year
#             except Exception as exc:
#                 print(f'{url} generated an exception: {exc}')

#     return liked_df