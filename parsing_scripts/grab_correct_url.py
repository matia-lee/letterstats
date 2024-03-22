import requests
import pandas as pd
from parsing_scripts.diary_movie_genres import format_title_to_url_slug

def grab_correct_url(username, diary_df):
    for index, row in diary_df.iterrows():
        title = format_title_to_url_slug(row['title'])
        release_year = row['release_year']
   
        url = f"https://letterboxd.com/{username}/film/{title}/"
        response = requests.get(url)
        if response.status_code == 200:
            diary_df.at[index, 'url'] = url
            continue
        
        title_slug_with_year = f"{title}-{release_year}"
        url_with_year = f"https://letterboxd.com/{username}/film/{title_slug_with_year}/"
        response_with_year = requests.get(url_with_year)
        if response_with_year.status_code == 200:
            diary_df.at[index, 'url'] = url_with_year
            continue

        diary_df.at[index, 'url'] = pd.NA

    return diary_df