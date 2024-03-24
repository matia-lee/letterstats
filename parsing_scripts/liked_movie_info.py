import requests
import multiprocessing
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_liked_movie_info(session, row, username):
    title_slug = row["title_slug"]
    genre_url = f"https://letterboxd.com/film/{title_slug}/genres/"
    movie_page_url = f"https://letterboxd.com/film/{title_slug}/"
    rating_url = f"https://letterboxd.com/{username}/film/{title_slug}/"
    details_url = f"https://letterboxd.com/film/{title_slug}/details/"
    genre_response = session.get(genre_url)
    movie_page_response = session.get(movie_page_url)
    details_response = session.get(details_url)
    rating_url_response = session.get(rating_url)
    release_year, genres, directors, cast, countries, studios, primary_language, spoken_languages, rating = None, None, None, None, None, None, None, None, ""

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

    if genre_response.status_code == 200:
        soup = BeautifulSoup(genre_response.text, "lxml")
        genre_main_container = soup.find("div", {"id": "tab-genres"})
        if genre_main_container:
            genre_container = genre_main_container.find("div", class_="text-sluglist")
            if genre_container:
                genres = ", ".join(a.text for a in genre_container.find_all("a", class_="text-slug"))

    if movie_page_response.status_code == 200:
        soup = BeautifulSoup(movie_page_response.text, "lxml")
        year_container = soup.find("small", class_ = "number")
        if year_container:
            release_year = year_container.find("a").text

        crew_container = soup.find("div", {"id": "tab-crew"})
        if crew_container:
            director_container = crew_container.find("div", class_="text-sluglist")
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

    if rating_url_response.status_code == 200:
        soup = BeautifulSoup(rating_url_response.text, "lxml")
        rating_element = soup.find("span", class_="rating")
        if rating_element:
            rating_text = re.sub(r'\s+', '', rating_element.text.strip())
            rating = rating_conversion.get(rating_text, "")

    return row.name, release_year, genres, directors, cast, countries, studios, primary_language, spoken_languages, rating

def grab_liked_movie_data_all_inclusive(username, liked_df):
    session = requests.Session()
    workers = multiprocessing.cpu_count() * 5
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fetch_liked_movie_info, session, row, username) for index, row in liked_df.iterrows()]

        for future in as_completed(futures):
            index, release_year, genres, directors, cast, countries, studios, primary_language, spoken_languages, rating = future.result()
            liked_df.at[index, "release_year"] = release_year if release_year else ""
            liked_df.at[index, "genres"] = genres if genres else ""
            liked_df.at[index, "director"] = directors if directors else ""
            liked_df.at[index, "cast"] = cast if cast else ""
            liked_df.at[index, "countries"] = countries if countries else ""
            liked_df.at[index, "studios"] = studios if studios else ""
            liked_df.at[index, "primary_language"] = primary_language if primary_language else ""
            liked_df.at[index, "spoken_languages"] = spoken_languages if spoken_languages else ""
            liked_df.at[index, "rating"] = rating if rating else ""

    return liked_df
