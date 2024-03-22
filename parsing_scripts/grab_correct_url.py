import requests
import pandas as pd
from parsing_scripts.diary_movie_genres import format_title_to_url_slug

def grab_correct_url(username, diary_df):
    for index, row in diary_df.iterrows():
        title = format_title_to_url_slug(row['title'])
        release_year = row['release_year']

        final_slug = title
   
        url = f"https://letterboxd.com/{username}/film/{title}/"
        response = requests.get(url)
        if response.status_code != 200:
            final_slug = f"{title}-{release_year}"

        diary_df.at[index, 'title_slug'] = final_slug

    return diary_df