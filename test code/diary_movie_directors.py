import requests
from bs4 import BeautifulSoup

def grab_diary_movie_director(diary_df):
    for index, row in diary_df.iterrows():
        title_slug = row["title_slug"]
        url = f"https://letterboxd.com/film/{title_slug}/genres/"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            genre_main_container = soup.find("div", {"id": "tab-crew"})
            if genre_main_container:
                genre_container = genre_main_container.find("div", class_="text-sluglist")
                if genre_container:
                    directors = genre_container.find_all("a", class_="text-slug")
                    if directors:
                        diary_df.at[index, "director"] = ", ".join(director.text for director in directors)
                
    return diary_df