import streamlit as st
from parsing_scripts.alltime_watched_films import grab_user_watched_films
from parsing_scripts.dates_from_diary import grab_dates_from_diaries
from parsing_scripts.diary_movie_genres import grab_diary_movie_genres

def fetch_and_display_films(username):
    if username:
        # film_titles = grab_user_watched_films(username)
        diary_entries = grab_dates_from_diaries(username)
        # if film_titles:
        #     message_placeholder.empty() 
        #     st.write(f"{username} has watched the following films:")
        #     for title in film_titles:
        #         st.write("- ", title)
        # else:
        #     st.write(f"Hmm, we can't seem to find the movies that {username} watched.")
        if diary_entries:
            grab_diary_movie_genres()
            message_placeholder.empty()
            st.write(f"{username} has logged these films on the following dates:")
            for entry in diary_entries:
                st.write(entry)
                # st.write(f"- {entry["title"]} on {entry["watched_date"]}")
        else:
            st.write("Can't seem to find any entries...")
    else:
        st.write("Please enter a username.")

st.title('Advanced Letterboxd Stats')
message_placeholder = st.empty()

username = st.text_input('Enter Letterboxd username, please:').strip()

if username:
    st.session_state['username_input'] = username

if st.button('Fetch Films') or 'username_input' in st.session_state:
    fetch_and_display_films(st.session_state.get('username_input'))
