import streamlit as st
from parsing_scripts.dates_from_diary import grab_dates_from_diaries
from parsing_scripts.diary_movie_genres import grab_diary_movie_genres

def fetch_and_display_films(username):

    if username != st.session_state.get('last_username', ''):
        for key in ['diary_entries', 'last_username']:
            if key in st.session_state:
                del st.session_state[key]

    if username:
        if 'diary_entries' not in st.session_state:
            st.session_state.diary_entries = []

        st.session_state['last_username'] = username
        
        st.session_state.diary_entries = grab_dates_from_diaries(username, st.session_state.diary_entries)
        st.session_state.diary_entries = grab_diary_movie_genres(st.session_state.diary_entries)
        
        if st.session_state.diary_entries:
            message_placeholder.empty()
            st.write(f"{username} has logged these films on the following dates:")
            for entry in st.session_state.diary_entries:
                st.write(entry)
        else:
            st.write("Can't seem to find any entries...")
    else:
        st.write("Please enter a username.")

st.title('Advanced Letterboxd Stats')
message_placeholder = st.empty()

username = st.text_input('Enter Letterboxd username, please:', key="username_input").strip()

if st.button('Fetch Films') or username:
    fetch_and_display_films(username)