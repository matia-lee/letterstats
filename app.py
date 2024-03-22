import pandas as pd
import streamlit as st
from parsing_scripts.dates_from_diary import grab_dates_from_diaries
from parsing_scripts.diary_movie_release_year import grab_diary_movie_release_year
from parsing_scripts.grab_correct_url import grab_correct_url
from parsing_scripts.diary_movie_genres import grab_diary_movie_genres
from parsing_scripts.diary_movie_directors import grab_diary_movie_director
from parsing_scripts.diary_movie_cast import grab_diary_movie_cast
from parsing_scripts.diary_movie_rating import grab_diary_movie_rating
# from parsing_scripts.diary_movie_liked import update_liked_movies_in_diary_df

if 'diary_df' not in st.session_state:
    st.session_state.diary_df = pd.DataFrame(columns=['title', 'watched_date', 'release_year', 'title_slug', 'genres', 'director', 'cast', 'rating', 'liked'])

def fetch_and_display_films(username):
    if username and username != st.session_state.get('last_username', ''):
        st.session_state['last_username'] = username

        st.session_state.diary_df = grab_dates_from_diaries(username, st.session_state.diary_df)
        st.session_state.diary_df = grab_diary_movie_release_year(username, st.session_state.diary_df)
        st.session_state.diary_df = grab_correct_url(username, st.session_state.diary_df)
        st.session_state.diary_df = grab_diary_movie_genres(st.session_state.diary_df)
        st.session_state.diary_df = grab_diary_movie_director(st.session_state.diary_df)
        # st.session_state.diary_df = grab_diary_movie_cast(st.session_state.diary_df)
        # st.session_state.diary_df = grab_diary_movie_rating(username, st.session_state.diary_df)
        # st.session_state.diary_df = update_liked_movies_in_diary_df(username, st.session_state.diary_df)
        
        if not st.session_state.diary_df.empty:
            st.write(f"{username} has logged these films on the following dates:")
            st.write(st.session_state.diary_df.to_html(escape=False), unsafe_allow_html=True)
        else:
            st.write("Can't seem to find any entries...")
    else:
        st.write("Please enter a username.")



col1, col2 = st.columns([5, 7])

with col1:
    st.markdown("""
    <div style='padding-top: 14px;'>
        <span style='color: rgb(102, 221, 103); font-size: 55px; font-weight: 700;'>
        Letter</span><span style='color: rgb(101, 186, 239); font-size: 55px; font-weight: 700; margin-left: -7px;'>
        Stats</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"<div style='margin-top: 59px; margin-left: -20px;'>made by <span style= 'color: rgb(239, 135, 51);'>@mat_lee</span></div>", unsafe_allow_html=True)


st.markdown('<i>the most comprehensive statlines for your Letterboxd account.</i>', unsafe_allow_html=True)

# username = st.text_input("Start by entering your Letterboxd username:", placeholder="Enter username here...", key="username_input").strip()

st.markdown("""
    <style>
    .label-style {
        color: #9b9b9b;
        margin-bottom: -55px;
        margin-top: 10px;
    }
    </style>
    <p class="label-style">Start by entering your Letterboxd username:</p>
""", unsafe_allow_html=True)

username = st.text_input("Enter your Letterboxd username:", placeholder="Enter username here...", key="input", label_visibility="hidden").strip()

if username:
    fetch_and_display_films(username)