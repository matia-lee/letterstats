import requests
from bs4 import BeautifulSoup
from parsing_scripts.diary_movie_genres import format_title_to_url_slug


def grab_diary_movie_rating(username, diary_df):
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

    for index, row in diary_df.iterrows():
        title_slug = format_title_to_url_slug(row["title"])
        url = f"https://letterboxd.com/{username}/film/{title_slug}/"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            rating = soup.find("span", class_="rating")
            if rating:
                rating_text = rating.text.strip()
                numerical_rating = rating_conversion.get(rating_text, "")

                diary_df.at[index, "rating"] = numerical_rating

    return diary_df