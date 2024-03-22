import requests
from bs4 import BeautifulSoup
import re
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
                rating_text = re.sub(r'\s+', '', rating.text)
                numerical_rating = rating_conversion.get(rating_text, "")
                diary_df.at[index, "rating"] = numerical_rating

    return diary_df

# import requests
# from bs4 import BeautifulSoup
# import re
# from parsing_scripts.diary_movie_genres import format_title_to_url_slug

# def grab_diary_movie_rating(username, diary_df):
#     rating_conversion = {
#         "½": "1",
#         "★": "2",
#         "★½": "3",
#         "★★": "4",
#         "★★½": "5",
#         "★★★": "6",
#         "★★★½": "7",
#         "★★★★": "8",
#         "★★★★½": "9",
#         "★★★★★": "10"
#     }

#     for index, row in diary_df.iterrows():
#         title_slug = format_title_to_url_slug(row["title"])
#         url = f"https://letterboxd.com/{username}/film/{title_slug}/"
#         print(f"Fetching URL: {url}")  # Debug 1: URL being fetched
#         response = requests.get(url)

#         if response.status_code == 200:
#             soup = BeautifulSoup(response.text, "lxml")
#             rating = soup.find("span", class_="rating")
#             if rating:
#                 print(f"Found rating element for {title_slug}: {rating}")  # Debug 2: Found rating element
#                 rating_text = re.sub(r'\s+', '', rating.text)
#                 print(f"Cleaned rating text: '{rating_text}'")  # Debug 3: Cleaned rating text

#                 if rating_text in rating_conversion:
#                     numerical_rating = rating_conversion.get(rating_text, "")
#                     print(f"Converted '{rating_text}' to '{numerical_rating}'")  # Debug 4: Conversion result
#                     diary_df.at[index, "rating"] = numerical_rating
#                 else:
#                     print(f"Unhandled rating text '{rating_text}' for {title_slug}. URL: {url}")  # Debug 5: Unhandled text
#             else:
#                 print(f"Rating not found for {title_slug}. URL: {url}")  # Debug 6: Rating element not found
#                 # Optional: Write the page HTML to a file for manual inspection
#                 with open(f"{title_slug}_debug.html", "w", encoding="utf-8") as file:
#                     file.write(soup.prettify())
#         else:
#             print(f"Failed to fetch URL: {url} with status code {response.status_code}")  # Debug 7: Fetching failed

#     return diary_df