import requests
from bs4 import BeautifulSoup
import multiprocessing
import pandas as pd

# def update_liked_movies_with_slugs(username, liked_df):
#     url = f"https://letterboxd.com/{username}/likes/films/"
#     response = requests.get(url)
#     new_rows = []

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "lxml")
#         film_posters = soup.find_all("div", class_="film-poster")
        
#         for poster in film_posters:
#             film_slug = poster.get("data-film-slug", None)
#             img = poster.find("img")
            
#             if film_slug and img and img.has_attr("alt"):
#                 title = img["alt"].strip()
#                 if not ((liked_df['title'] == title) & (liked_df['title_slug'] == film_slug)).any():
#                     new_row = {
#                         "title": title,
#                         "watched_date": pd.NA,
#                         "release_year": pd.NA,
#                         "title_slug": film_slug,
#                         "url": pd.NA,
#                         "genres": pd.NA,
#                         "director": pd.NA,
#                         "cast": pd.NA,
#                         "rating": pd.NA,
#                         "liked": True
#                     }
#                     new_rows.append(new_row)

#     if new_rows:
#         liked_df = pd.concat([liked_df, pd.DataFrame(new_rows)], ignore_index=True)
    
#     return liked_df

def process_liked_page(username, page_number):
    new_rows = []
    if page_number == 1:
        url = f"https://letterboxd.com/{username}/likes/films/"
    else:
        url = f"https://letterboxd.com/{username}/likes/films/page/{page_number}/"

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        film_posters = soup.find_all("div", class_="film-poster")
        
        for poster in film_posters:
            film_slug = poster.get("data-film-slug", None)
            img = poster.find("img")
            
            if film_slug and img and img.has_attr("alt"):
                title = img["alt"].strip()
                new_row = {
                    "title": title,
                    "watched_date": pd.NA,
                    "release_year": pd.NA,
                    "title_slug": film_slug,
                    "url": pd.NA,
                    "genres": pd.NA,
                    "director": pd.NA,
                    "cast": pd.NA,
                    "rating": pd.NA,
                    "liked": True
                }
                new_rows.append(new_row)
    return new_rows

from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_pages_in_batch(username, start_page, end_page):
    session = requests.Session()
    entries = []
    for page_number in range(start_page, end_page + 1):
        url = f"https://letterboxd.com/{username}/likes/films/page/{page_number}/"
        response = session.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            film_posters = soup.find_all("div", class_="film-poster")
            if not film_posters:
                return entries, False

            for poster in film_posters:
                film_slug = poster.get("data-film-slug", None)
                img = poster.find("img")
                if film_slug and img and img.has_attr("alt"):
                    title = img["alt"].strip()
                    new_row = {
                        "title": title,
                        "watched_date": pd.NA,
                        "release_year": pd.NA,
                        "title_slug": film_slug,
                        "url": pd.NA,
                        "genres": pd.NA,
                        "director": pd.NA,
                        "cast": pd.NA,
                        "rating": pd.NA,
                        "liked": True
                    }
                    entries.append(new_row)
        else:
            return entries, False
    return entries, True

def update_liked_movies_with_slugs(username, liked_df):
    batch_size = 10  
    new_rows = []
    batch_start = 1
    more_data = True

    while more_data:
        workers = multiprocessing.cpu_count() * 5
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for start_page in range(batch_start, batch_start + batch_size):
                futures.append(executor.submit(fetch_pages_in_batch, username, start_page, start_page))
            
            more_data = False 
            for future in as_completed(futures):
                entries, has_more_data = future.result()
                new_rows.extend(entries)
                if has_more_data:
                    more_data = True 
            
            batch_start += batch_size  
    
    if new_rows:
        liked_df = pd.concat([liked_df, pd.DataFrame(new_rows)], ignore_index=True)

    return liked_df