import requests
from bs4 import BeautifulSoup
import multiprocessing
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_page_combined(username, page_number):
    entries = []
    if page_number == 1:
        url = f"https://letterboxd.com/{username}/films/diary/"
    else:
        url = f"https://letterboxd.com/{username}/films/diary/page/{page_number}/"

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        diary_entries_raw = soup.find_all("tr", class_="diary-entry-row")
        for movie_entry in diary_entries_raw:
            movie_info = {}
            title_container = movie_entry.find("td", class_="td-film-details")
            if title_container:
                title_element = title_container.find("h3", class_="headline-3").find("a")
                if title_element:
                    movie_info["title"] = title_element.text.strip()

            date_info = movie_entry.find("td", class_="td-calendar")
            if date_info:
                month = date_info.find("a")
                year = date_info.find("small")
                if month and year:
                    current_month = month.text.strip()
                    current_year = year.text.strip()

            day_info = movie_entry.find("td", class_="td-day")
            if day_info:
                day = day_info.find("a").text.strip()

            movie_info["watched_date"] = f"{day} {current_month} {current_year}"

            release_year_container = movie_entry.find("td", class_="td-released")
            if release_year_container:
                movie_info["release_year"] = release_year_container.find("span").text.strip()

            if "title" in movie_info and "watched_date" in movie_info and "release_year" in movie_info:
                entries.append(movie_info)
    return entries

def grab_date_info(username, diary_df):
    url = f"https://letterboxd.com/{username}/films/diary/"
    response = requests.get(url)
    last_page = 1
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        finding_last_page = soup.find_all("li", class_="paginate-page")
        if finding_last_page:
            last_page_li = finding_last_page[-1]
            last_page = int(last_page_li.find("a").text.strip())

    entries = []
    workers = multiprocessing.cpu_count() * 5
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_page = {executor.submit(process_page_combined, username, page_number): page_number for page_number in range(1, last_page + 1)}
        for future in as_completed(future_to_page):
            entries.extend(future.result())

    diary_df = pd.DataFrame(entries)
    return diary_df
