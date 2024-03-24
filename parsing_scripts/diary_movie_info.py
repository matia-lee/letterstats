import requests
import multiprocessing
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_movie_data_for_row(session, row, rating_conversion):
    title_slug = row["title_slug"]
    genre_url = f"https://letterboxd.com/film/{title_slug}/genres/"
    director_cast_url = f"https://letterboxd.com/film/{title_slug}/"
    details_url = f"https://letterboxd.com/film/{title_slug}/details/"
    rating_url = row["url"] 
    genre_response = session.get(genre_url)
    director_cast_response = session.get(director_cast_url)
    details_response = session.get(details_url)
    rating_response = session.get(rating_url)
    genres, directors, cast, countries, studios, primary_language, spoken_languages, rating = None, None, None, None, None, None, None, ""

    if genre_response.status_code == 200:
        soup = BeautifulSoup(genre_response.text, "lxml")
        genre_main_container = soup.find("div", {"id": "tab-genres"})
        if genre_main_container:
            genre_container = genre_main_container.find("div", class_="text-sluglist")
            if genre_container:
                genres = ", ".join(a.text for a in genre_container.find_all("a", class_="text-slug"))

    if director_cast_response.status_code == 200:
        soup = BeautifulSoup(director_cast_response.text, "lxml")
        director_main_container = soup.find("div", {"id": "tab-crew"})
        if director_main_container:
            director_container = director_main_container.find("div", class_="text-sluglist")
            if director_container:
                directors = ", ".join(director.text for director in director_container.find_all("a", class_="text-slug"))

        cast_main_container = soup.find("div", class_="cast-list text-sluglist")
        if cast_main_container:
            cast = ", ".join(a.text for a in cast_main_container.find_all("a", class_="text-slug"))

    if details_response.status_code == 200:
        soup = BeautifulSoup(details_response.text, "lxml")
        country_containers = soup.find_all("a", class_="text-slug", href=lambda value: value and value.startswith("/films/country/"))
        if country_containers:
            countries = ", ".join(country.text for country in country_containers)

        studios_container = soup.find_all("a", href=lambda value: value and value.startswith("/studio/"))
        if studios_container:
            studios = ", ".join(studios.text for studios in studios_container)

        language_containers = soup.find_all("a", href=lambda value: value and value.startswith("/films/language/"))
        if language_containers:
            primary_language = language_containers[0].text if language_containers else None
            spoken_languages = ", ".join(language.text for language in language_containers[1:]) if len(language_containers) > 1 else ""


    if rating_response.status_code == 200:
        soup = BeautifulSoup(rating_response.text, "lxml")
        rating_element = soup.find("span", class_="rating")
        if rating_element:
            rating_text = re.sub(r'\s+', '', rating_element.text)
            rating = rating_conversion.get(rating_text, "")

    return row.name, genres, directors, cast, countries, studios, primary_language, spoken_languages, rating

def grab_diary_movie_data_all_inclusive(diary_df):
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

    session = requests.Session()

    workers = multiprocessing.cpu_count() * 5
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fetch_movie_data_for_row, session, row, rating_conversion) for index, row in diary_df.iterrows()]
        
        for future in as_completed(futures):
            index, genres, directors, cast, countries, studios, primary_language, spoken_languages, rating = future.result()
            if genres:
                diary_df.at[index, "genres"] = genres
            else:
                diary_df.at[index, "genres"] = ""
                
            if directors:
                diary_df.at[index, "director"] = directors
            else:
                diary_df.at[index, "director"] = ""
                
            if cast:
                diary_df.at[index, "cast"] = cast
            else:
                diary_df.at[index, "cast"] = ""

            if countries:
                diary_df.at[index, "countries"] = countries
            else:
                diary_df.at[index, "countries"] = ""

            if studios:
                diary_df.at[index, "studios"] = studios
            else:
                diary_df.at[index, "studios"] = ""

            if primary_language:
                diary_df.at[index, "primary_language"] = primary_language
            else:
                diary_df.at[index, "primary_language"] = ""

            if spoken_languages:
                diary_df.at[index, "spoken_languages"] = spoken_languages
            else:
                diary_df.at[index, "spoken_languages"] = ""

            diary_df.at[index, "rating"] = rating

    return diary_df