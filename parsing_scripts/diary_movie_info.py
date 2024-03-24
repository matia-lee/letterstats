# import requests
# import multiprocessing
# from bs4 import BeautifulSoup
# import re
# from concurrent.futures import ThreadPoolExecutor, as_completed

# def fetch_movie_data_for_row(session, row, rating_conversion):
#     title_slug = row["title_slug"]
#     genre_url = f"https://letterboxd.com/film/{title_slug}/genres/"
#     director_cast_url = f"https://letterboxd.com/film/{title_slug}/"
#     details_url = f"https://letterboxd.com/film/{title_slug}/details/"
#     rating_url = row["url"] 
#     genre_response = session.get(genre_url)
#     director_cast_response = session.get(director_cast_url)
#     details_response = session.get(details_url)
#     rating_response = session.get(rating_url)
#     genres, directors, cast, countries, studios, primary_language, spoken_languages, rating = None, None, None, None, None, None, None, ""

#     if genre_response.status_code == 200:
#         soup = BeautifulSoup(genre_response.text, "lxml")
#         genre_main_container = soup.find("div", {"id": "tab-genres"})
#         if genre_main_container:
#             genre_container = genre_main_container.find("div", class_="text-sluglist")
#             if genre_container:
#                 genres = ", ".join(a.text for a in genre_container.find_all("a", class_="text-slug"))

#     if director_cast_response.status_code == 200:
#         soup = BeautifulSoup(director_cast_response.text, "lxml")
#         director_main_container = soup.find("div", {"id": "tab-crew"})
#         if director_main_container:
#             director_container = director_main_container.find("div", class_="text-sluglist")
#             if director_container:
#                 directors = ", ".join(director.text for director in director_container.find_all("a", class_="text-slug"))

#         cast_main_container = soup.find("div", class_="cast-list text-sluglist")
#         if cast_main_container:
#             cast = ", ".join(a.text for a in cast_main_container.find_all("a", class_="text-slug"))

#     if details_response.status_code == 200:
#         soup = BeautifulSoup(details_response.text, "lxml")
#         country_containers = soup.find_all("a", class_="text-slug", href=lambda value: value and value.startswith("/films/country/"))
#         if country_containers:
#             countries = ", ".join(country.text for country in country_containers)

#         studios_container = soup.find_all("a", href=lambda value: value and value.startswith("/studio/"))
#         if studios_container:
#             studios = ", ".join(studios.text for studios in studios_container)

#         language_containers = soup.find_all("a", href=lambda value: value and value.startswith("/films/language/"))
#         if language_containers:
#             primary_language = language_containers[0].text if language_containers else None
#             spoken_languages = ", ".join(language.text for language in language_containers[1:]) if len(language_containers) > 1 else ""


#     if rating_response.status_code == 200:
#         soup = BeautifulSoup(rating_response.text, "lxml")
#         rating_element = soup.find("span", class_="rating")
#         if rating_element:
#             rating_text = re.sub(r'\s+', '', rating_element.text)
#             rating = rating_conversion.get(rating_text, "")

#     return row.name, genres, directors, cast, countries, studios, primary_language, spoken_languages, rating

# def grab_diary_movie_data_all_inclusive(diary_df):
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

#     session = requests.Session()

#     workers = multiprocessing.cpu_count() * 5
#     with ThreadPoolExecutor(max_workers=workers) as executor:
#         futures = [executor.submit(fetch_movie_data_for_row, session, row, rating_conversion) for index, row in diary_df.iterrows()]
        
#         for future in as_completed(futures):
#             index, genres, directors, cast, countries, studios, primary_language, spoken_languages, rating = future.result()
#             diary_df.at[index, "genres"] = genres if genres else ""
#             diary_df.at[index, "director"] = directors if directors else ""
#             diary_df.at[index, "cast"] = cast if cast else ""
#             diary_df.at[index, "countries"] = countries if countries else ""
#             diary_df.at[index, "studios"] = studios if studios else ""
#             diary_df.at[index, "primary_language"] = primary_language if primary_language else ""
#             diary_df.at[index, "spoken_languages"] = spoken_languages if spoken_languages else ""
#             diary_df.at[index, "rating"] = rating if rating else ""
#             diary_df.at[index, "rating"] = rating

#     return diary_df

import re
from bs4 import BeautifulSoup
import asyncio
import pandas as pd
import pycountry

def get_iso_alpha_3(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_3
    except LookupError:
        return None

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()
    
async def grab_diary_movie_info_async(diary_df, session):
    tasks = []
    for index, row in diary_df.iterrows():
        title_slug = row["title_slug"]
        main_url = f"https://letterboxd.com/film/{title_slug}/"
        rating_url = row["url"] 

        main_task = asyncio.create_task(fetch_url(session, main_url))
        rating_task = asyncio.create_task(fetch_url(session, rating_url))
        
        tasks.append((index, "main", main_task))
        tasks.append((index, "rating", rating_task))


    responses = await asyncio.gather(*[task for _, _, task in tasks])

    for (index, task_type, _), response in zip(tasks, responses):
        if response:
            soup = BeautifulSoup(response, "lxml")

            if task_type == "main":
                genre_main_container = soup.find("div", {"id": "tab-genres"})
                if genre_main_container:
                    genre_container = genre_main_container.find("div", class_="text-sluglist")
                    if genre_container:
                        genres = genre_container.find_all("a", class_="text-slug")
                        if genres:
                            diary_df.at[index, "genres"] = ", ".join(genre.text for genre in genres)

                cast_main_container = soup.find("div", class_="cast-list text-sluglist")
                if cast_main_container:
                    cast = [a.text for a in cast_main_container.find_all("a", class_="text-slug")]
                    diary_df.at[index, "cast"] = ", ".join(cast)

                director_main_container = soup.find("div", {"id": "tab-crew"})
                if director_main_container:
                    director_container = director_main_container.find("div", class_="text-sluglist")
                    if director_container:
                        directors = director_container.find_all("a", class_="text-slug")
                        if directors:
                            diary_df.at[index, "director"] = ", ".join(director.text for director in directors)

                country_containers = soup.find_all("a", class_="text-slug", href=lambda value: value and value.startswith("/films/country/"))
                if country_containers:
                    # diary_df.at[index, "countries"] = ", ".join(country.text for country in country_containers)
                    countries_iso = []
                    for country in country_containers:
                        country_name = country.text
                        iso_alpha_3 = get_iso_alpha_3(country_name)
                        if iso_alpha_3: 
                            countries_iso.append(iso_alpha_3)
                    diary_df.at[index, "countries"] = ", ".join(countries_iso)

                studios_container = soup.find_all("a", href=lambda value: value and value.startswith("/studio/"))
                if studios_container:
                    diary_df.at[index, "studios"] = ", ".join(studios.text for studios in studios_container)

                language_containers = soup.find_all("a", href=lambda value: value and value.startswith("/films/language/"))
                if language_containers:
                    diary_df.at[index, "primary_language"] = language_containers[0].text if language_containers else pd.NA
                    if len(language_containers) > 1:
                        primary_language = language_containers[0].text
                        spoken_languages = [language.text for language in language_containers if language.text != primary_language]
                        diary_df.at[index, "spoken_languages"] = ", ".join(spoken_languages)
                    else:
                        diary_df.at[index, "spoken_languages"] = pd.NA

                runtime_container = soup.find("p", class_="text-footer")
                if runtime_container:
                    runtime_text = runtime_container.get_text()
                    match = re.search(r'\d+', runtime_text)
                    if match:
                        runtime_minutes = int(match.group())
                        diary_df.at[index, "runtime"] = runtime_minutes

            elif task_type == "rating":
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
                rating_element = soup.find("span", class_="rating")
                if rating_element:
                    rating_text = re.sub(r'\s+', '', rating_element.text)
                    diary_df.at[index, "rating"] = rating_conversion.get(rating_text, "")

    return diary_df