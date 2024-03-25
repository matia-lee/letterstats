import requests
from bs4 import BeautifulSoup
import re

def grab_liked_movie_rating(username, liked_df):
    rating_conversion = {
        "½": "1",
        "★": "2",
        "★½": "3",
        "★★": "4",
        "★★½": "5",
        "★★★": "6",
        "★★★½": "7",
        "★★★★": "8",
        "★★★★½": "9",
        "★★★★★": "10"
    }

    url = f"https://letterboxd.com/{username}/likes/films/"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        ratings_elements = soup.find_all("span", class_="rating") 
        numerical_ratings = []
        for rating in ratings_elements:
            rating_text = re.sub(r'\s+', '', rating.text.strip())
            numerical_rating = rating_conversion.get(rating_text, "")
            numerical_ratings.append(numerical_rating)
        
        for index, numerical_rating in enumerate(numerical_ratings[:len(liked_df)]):
            liked_df.at[index, "rating"] = numerical_rating

    return liked_df