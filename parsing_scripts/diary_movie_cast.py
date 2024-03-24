import requests
from bs4 import BeautifulSoup

def grab_diary_movie_cast(diary_df):
    for index, row in diary_df.iterrows():
        title_slug = row["title_slug"]
        url = f"https://letterboxd.com/film/{title_slug}/"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            cast_main_container = soup.find("div", class_="cast-list text-sluglist")
            if cast_main_container:
                cast = [a.text for a in cast_main_container.find_all("a", class_="text-slug")]
                diary_df.at[index, "cast"] = ", ".join(cast)

    return diary_df

# async def grab_diary_movie_cast_async(diary_df, session):
#     tasks = []
#     for index, row in diary_df.iterrows():
#         title_slug = row["title_slug"]
#         url = f"https://letterboxd.com/film/{title_slug}/"
#         tasks.append(asyncio.create_task(fetch_url(session, url)))
    
#     responses = await asyncio.gather(*tasks)
    
#     for response, (index, row) in zip(responses, diary_df.iterrows()):
#         if response:
#             soup = BeautifulSoup(response, "lxml")
#             cast_main_container = soup.find("div", class_="cast-list text-sluglist")
#             if cast_main_container:
#                 cast = [a.text for a in cast_main_container.find_all("a", class_="text-slug")]
#                 diary_df.at[index, "cast"] = ", ".join(cast)
#     return diary_df

# async def grab_diary_movie_director_async(diary_df, session):
#     tasks = []
#     for index, row in diary_df.iterrows():
#         title_slug = row["title_slug"]
#         url = f"https://letterboxd.com/film/{title_slug}/genres/"
#         tasks.append(asyncio.create_task(fetch_url(session, url)))
    
#     responses = await asyncio.gather(*tasks)
    
#     for response, (index, row) in zip(responses, diary_df.iterrows()):
#         if response:
#             soup = BeautifulSoup(response, "lxml")
#             director_main_container = soup.find("div", {"id": "tab-crew"})
#             if director_main_container:
#                 director_container = director_main_container.find("div", class_="text-sluglist")
#                 if director_container:
#                     directors = director_container.find_all("a", class_="text-slug")
#                     if directors:
#                         diary_df.at[index, "director"] = ", ".join(director.text for director in directors)

#             genre_main_container = soup.find("div", {"id": "tab-genres"})
#             if genre_main_container:
#                 genre_container = genre_main_container.find("div", class_="text-sluglist")
#                 if genre_container:
#                     genres = genre_container.find_all("a", class_="text-slug")
#                     if genres:
#                         diary_df.at[index, "genre"] = ", ".join(genre.text for genre in genres)
                
#     return diary_df














# import requests
# from bs4 import BeautifulSoup
# from concurrent.futures import ThreadPoolExecutor, as_completed

# def fetch_movie_cast_for_row(row):
#     title_slug = row["title_slug"]
#     url = f"https://letterboxd.com/film/{title_slug}/"
#     response = requests.get(url)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "lxml")
#         cast_main_container = soup.find("div", class_="cast-list text-sluglist")
#         if cast_main_container:
#             cast = [a.text for a in cast_main_container.find_all("a", class_="text-slug")]
#             return row.name, ", ".join(cast)
#     return row.name, None

# def grab_diary_movie_cast(diary_df):
#     with ThreadPoolExecutor(max_workers=200) as executor:
#         futures = [executor.submit(fetch_movie_cast_for_row, row) for index, row in diary_df.iterrows()]
        
#         for future in as_completed(futures):
#             index, cast = future.result()
#             if cast:
#                 diary_df.at[index, "cast"] = cast
#             else:
#                 diary_df.at[index, "cast"] = ""

#     return diary_df
