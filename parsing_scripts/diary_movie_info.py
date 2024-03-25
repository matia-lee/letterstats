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
    updates = []
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
        update = {'index': index}
        if response:
            soup = BeautifulSoup(response, "lxml")

            if task_type == "main":
                genre_main_container = soup.find("div", {"id": "tab-genres"})
                if genre_main_container:
                    genre_container = genre_main_container.find("div", class_="text-sluglist")
                    if genre_container:
                        genres = genre_container.find_all("a", class_="text-slug")
                        if genres:
                            update["genres"] = ", ".join(genre.text for genre in genres)

                cast_main_container = soup.find("div", class_="cast-list text-sluglist")
                if cast_main_container:
                    cast = [a.text for a in cast_main_container.find_all("a", class_="text-slug")]
                    update["cast"] = ", ".join(cast)

                director_main_container = soup.find("div", {"id": "tab-crew"})
                if director_main_container:
                    director_container = director_main_container.find("div", class_="text-sluglist")
                    if director_container:
                        directors = director_container.find_all("a", class_="text-slug")
                        if directors:
                            update["director"] = ", ".join(director.text for director in directors)

                country_containers = soup.find_all("a", class_="text-slug", href=lambda value: value and value.startswith("/films/country/"))
                if country_containers:
                    # diary_df.at[index, "countries"] = ", ".join(country.text for country in country_containers)
                    countries_iso = []
                    for country in country_containers:
                        country_name = country.text
                        iso_alpha_3 = get_iso_alpha_3(country_name)
                        if iso_alpha_3: 
                            countries_iso.append(iso_alpha_3)
                    update["countries"] = ", ".join(countries_iso)

                studios_container = soup.find_all("a", href=lambda value: value and value.startswith("/studio/"))
                if studios_container:
                    update["studios"] = ", ".join(studios.text for studios in studios_container)

                language_containers = soup.find_all("a", href=lambda value: value and value.startswith("/films/language/"))
                if language_containers:
                    update["primary_language"] = language_containers[0].text if language_containers else pd.NA
                    if len(language_containers) > 1:
                        primary_language = language_containers[0].text
                        spoken_languages = [language.text for language in language_containers if language.text != primary_language]
                        update["spoken_languages"] = ", ".join(spoken_languages)
                    else:
                        update["spoken_languages"] = pd.NA

                runtime_container = soup.find("p", class_="text-footer")
                if runtime_container:
                    runtime_text = runtime_container.get_text()
                    match = re.search(r'(\d+,?)+', runtime_text)
                    if match:
                        runtime_minutes = int(match.group().replace(',', ''))
                        update["runtime"] = runtime_minutes

            elif task_type == "rating":
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
                rating_element = soup.find("span", class_="rating")
                if rating_element:
                    rating_text = re.sub(r'\s+', '', rating_element.text)
                    update['rating'] = rating_conversion.get(rating_text, "")

        if update: 
            updates.append(update)

    for update in updates:
        index = update.pop('index')
        for key, value in update.items():
            diary_df.at[index, key] = value

    return diary_df