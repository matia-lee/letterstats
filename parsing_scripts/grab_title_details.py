import requests
import pandas as pd
import multiprocessing
from unidecode import unidecode
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def format_title_to_url_slug(title):
    if pd.isnull(title):
        return ""
    else:
        fractions = ['½', '⅓', '⅔', '¼', '¾', '⅕', '⅖', '⅗', '⅘', '⅙', '⅚', '⅐', '⅛', '⅜', '⅝', '⅞', '⅑', '⅒']
        for frac in fractions:
            title = title.replace(frac, '')
        
        title = re.sub(r'(\b\d+\/\d+\b)', lambda m: m.group(0).replace('/', '-'), title)
        title = re.sub(r'[^\x00-\x7F\u00C0-\u024F\u1E00-\u1EFF]', '', title)
        title = re.sub(r'(\d+)\s*\d+/\d+', r'\1', title)
        slug = unidecode(title.lower())
        slug = slug.replace(" ", "-").replace("/", "-").replace(":", "-")
        slug = re.sub(r"[^a-z0-9\-]", "", slug)
        slug = re.sub(r"-+", "-", slug)
        slug = slug.strip('-')

        return(slug)

def fetch_details_for_row(args):
    username, index, row = args
    title = format_title_to_url_slug(row['title'])
    release_year = row['release_year']

    url_with_year = f"https://letterboxd.com/{username}/film/{title}-{release_year}/"
    base_url = f"https://letterboxd.com/{username}/film/{title}/"

    response_with_year = requests.get(url_with_year)
    if response_with_year.status_code == 200:
        final_slug, final_url = f"{title}-{release_year}", url_with_year
    else:
        response = requests.get(base_url)
        if response.status_code == 200:
            final_slug, final_url = title, base_url
        else:
            final_slug, final_url = "peepee", "poopoo"
            for i in range(1, 10):
                url_with_suffix = f"{base_url}{i}/"
                response_with_suffix = requests.get(url_with_suffix)
                if response_with_suffix.status_code == 200:
                    final_slug, final_url = title, url_with_suffix
                    break
                else:
                    url_with_year_and_suffix = f"{url_with_year}{i}/"
                    response_with_url_and_suffix = requests.get(url_with_year_and_suffix)
                    if response_with_url_and_suffix.status_code == 200:
                        final_slug, final_url = title, url_with_year_and_suffix
                        break
                    else:
                        url_with_double_suffix = f"https://letterboxd.com/{username}/film/{title}-{release_year}-{i}/"
                        response_with_double_suffix = requests.get(url_with_double_suffix)
                        if response_with_double_suffix.status_code == 200:
                            final_slug, final_url = title, url_with_double_suffix
                            break
            else:
                return index, None, None
    
    return index, final_slug, final_url


def grab_title_details(username, diary_df):
    workers = multiprocessing.cpu_count() * 5
    keep_indices = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fetch_details_for_row, (username, index, row)) for index, row in diary_df.iterrows()]
        
        for future in as_completed(futures):
            index, final_slug, final_url = future.result()
            if final_slug is not None and final_url is not None:
                keep_indices.append(index)
                diary_df.at[index, 'title_slug'] = final_slug
                diary_df.at[index, "url"] = final_url
                
    filtered_diary_df = diary_df.loc[keep_indices]
    return filtered_diary_df
