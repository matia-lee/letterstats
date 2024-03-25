import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_release_years_for_page(username, page_number):
    release_years = []
    if page_number == 1:
        url = f"https://letterboxd.com/{username}/films/diary/"
    else:
        url = f"https://letterboxd.com/{username}/films/diary/page/{page_number}/"
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        diary_entries = soup.find_all("tr", class_="diary-entry-row")
        for entry in diary_entries:
            release_year_container = entry.find("td", class_="td-released")
            if release_year_container:
                release_year = release_year_container.find("span").text.strip()
                release_years.append(release_year)
    
    return release_years

def grab_diary_movie_release_year(username, diary_df):
    url = f"https://letterboxd.com/{username}/films/diary/"
    response = requests.get(url)
    last_page = 1
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        finding_last_page = soup.find_all("li", class_="paginate-page")
        if finding_last_page:
            last_page_li = finding_last_page[-1]
            last_page = int(last_page_li.find("a").text.strip())
    
    all_release_years = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(fetch_release_years_for_page, username, page_number) for page_number in range(1, last_page + 1)]
        for future in as_completed(futures):
            all_release_years.extend(future.result())
    
    if len(all_release_years) == len(diary_df):
        diary_df['release_year'] = all_release_years

    return diary_df
