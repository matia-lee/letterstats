import streamlit as st
import requests
from bs4 import BeautifulSoup

def grab_user_watched_films(username):

    last_page = 1
    film_titles = []

    url = f"https://letterboxd.com/{username}/films/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        finding_last_page = soup.find_all('li', class_='paginate-page')
        if finding_last_page:
            last_page_li = finding_last_page[-1]
            last_page = int(last_page_li.find('a').text.strip())

        for page_number in range(1, last_page + 1):
            if page_number > 1:
                url = f"https://letterboxd.com/{username}/films/page/{page_number}/"
                response = requests.get(url)
                if response.status_code != 200:
                    print(f"Uh oh sphagetti oh's failed to fetch this page's: {page_number} information")
                    break
                soup = BeautifulSoup(response.text, 'lxml')
            
            parent_films = soup.find_all('li', class_='poster-container')
            for film_element in parent_films:
                img = film_element.find('img')
                if img and img.has_attr('alt'):
                    film_titles.append(img['alt'])
    else:
        print("Failed to fetch first page information")
        return []
    
    if not film_titles:
        print("Recheck html selectors")
        return []
    
    return film_titles

def fetch_and_display_films(username):
    if username:
        film_titles = grab_user_watched_films(username)
        if film_titles:
            message_placeholder.empty() 
            st.write(f"{username} has watched the following films:")
            for title in film_titles:
                st.write("- ", title)
        else:
            st.write(f"Hmm, we can't seem to find the movies that {username} watched.")
    else:
        st.write("Please enter a username.")

st.title('Advanced Letterboxd Stats')
message_placeholder = st.empty()

username = st.text_input('Enter Letterboxd username, please:').strip()

if username:
    st.session_state['username_input'] = username

if st.button('Fetch Films') or 'username_input' in st.session_state:
    fetch_and_display_films(st.session_state.get('username_input'))
