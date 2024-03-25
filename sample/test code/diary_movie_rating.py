import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_movie_rating_for_row(url, rating_conversion):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        rating = soup.find("span", class_="rating")
        if rating:
            rating_text = re.sub(r'\s+', '', rating.text)
            numerical_rating = rating_conversion.get(rating_text, "")
            return numerical_rating
    return ""

def grab_diary_movie_rating(diary_df):
    rating_conversion = {
        "½": 1,
        "★": 2,
        "★½": 3,
        "★★": 4,
        "★★½": 5,
        "★★★": 6,
        "★★★½": 7,
        "★★★★": 8,
        "★★★★½": 9,
        "★★★★★": 10
    }

    with ThreadPoolExecutor(max_workers=200) as executor:
        future_to_index = {executor.submit(fetch_movie_rating_for_row, row["url"], rating_conversion): index for index, row in diary_df.iterrows()}
        
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            rating = future.result()
            diary_df.at[index, "rating"] = rating

    return diary_df
