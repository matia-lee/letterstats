import streamlit as st
import requests
from bs4 import BeautifulSoup

def fetch_user_films(username):
    url = f"https://letterboxd.com/{username}/films/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text 
    return None

def grab_user_watched_films(html_content):
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        film_titles = []
        parent_films = soup.find_all('li', class_='poster-container')
        
        for film_element in parent_films:
            img = film_element.find('img')
            if img and img.has_attr('alt'):
                film_titles.append(img['alt'])
        
        if not film_titles:
            print("No film titles found. Check selectors.")
            return []
        return film_titles
    except Exception as e:
        print(f"An error occurred while parsing HTML: {e}")
        return []


st.title('Advanced Letterboxd Stats')

username = st.text_input('Enter Letterboxd username, please:', '')

message_placeholder = st.empty()

if st.button('Fetch Films'):
    if username:
        message_placeholder.text(f"Fetching films watched by {username}...")
        html_content = fetch_user_films(username)
        if html_content:
            film_titles = grab_user_watched_films(html_content)
            if film_titles:
                message_placeholder.empty() 
                st.write(f"{username} has watched the following films:")
                for title in film_titles:
                    st.write("- ", title)
            else:
                message_placeholder.text(f"Hmm, we can't seem to find the movies that {username} watched.")
        else:
            message_placeholder.text("Failed to fetch data. Please check the username or try again later.")
    else:
        message_placeholder.text("Please enter a username.")
