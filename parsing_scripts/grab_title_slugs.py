import requests
from parsing_scripts.diary_movie_genres import format_title_to_url_slug

def grab_title_slug(username, diary_df):
    for index, row in diary_df.iterrows():
        title = format_title_to_url_slug(row['title'])
        release_year = row['release_year']
   
        url = f"https://letterboxd.com/{username}/film/{title}/"
        response = requests.get(url)
        if response.status_code == 200:
            final_slug = title
        else:
            url_with_year = f"https://letterboxd.com/{username}/film/{title}-{release_year}/"
            response_with_year = requests.get(url_with_year)

            if response_with_year.status_code == 200:
                final_slug = f"{title}-{release_year}"
            else:
                for i in range(1, 10):
                    url_with_suffix = f"{url}{i}/"
                    response_with_suffix = requests.get(url_with_suffix)
                    if response_with_suffix.status_code == 200:
                        final_slug = title
                    else:
                        break

        diary_df.at[index, 'title_slug'] = final_slug

    return diary_df