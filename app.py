import pandas as pd
import streamlit as st
from parsing_scripts.dates_from_diary import grab_date_info
from parsing_scripts.grab_title_details import grab_title_details
from parsing_scripts.diary_movie_info import grab_diary_movie_data_all_inclusive

from parsing_scripts.update_liked_df import update_liked_movies_with_slugs
from parsing_scripts.liked_movie_info import grab_liked_movie_data_all_inclusive

# from concurrent.futures import ThreadPoolExecutor

# def process_diary_movies(username, diary_df):
#     diary_df = grab_dates_from_diaries(username, diary_df)
#     diary_df = grab_diary_movie_release_year(username, diary_df)
#     diary_df = grab_title_slug(username, diary_df)
#     diary_df = grab_correct_url(username, diary_df)
#     diary_df = grab_diary_movie_genres(diary_df)
#     diary_df = grab_diary_movie_director(diary_df)
#     diary_df = grab_diary_movie_cast(diary_df)
#     diary_df = grab_diary_movie_rating(diary_df)
#     return diary_df

# def process_liked_movies(username, liked_df):
#     liked_df = update_liked_movies_with_slugs(username, liked_df)
#     liked_df = grab_liked_movie_release_year(liked_df)
#     liked_df = grab_liked_movie_genres(liked_df)
#     liked_df = grab_liked_movie_director(liked_df)
#     liked_df = grab_liked_movie_cast(liked_df)
#     liked_df = grab_liked_movie_rating(username, liked_df)
#     return liked_df

if 'diary_df' not in st.session_state:
    st.session_state.diary_df = pd.DataFrame(columns=['title', 'watched_date', 'release_year', 'title_slug', 'url', 'genres', 'director', 'cast', 'rating', 'liked'])

if 'liked_df' not in st.session_state:
    st.session_state.liked_df = pd.DataFrame(columns=['title', 'watched_date', 'release_year', 'title_slug', 'url', 'genres', 'director', 'cast', 'rating', 'liked'])

def fetch_and_display_films(username):
    if username and username != st.session_state.get('last_username', ''):
        st.session_state['last_username'] = username

        st.session_state.liked_df = pd.DataFrame(columns=['title', 'watched_date', 'release_year', 'title_slug', 'url', 'genres', 'director', 'cast', 'rating', 'liked'])

        # diary_df = pd.DataFrame(columns=['title', 'watched_date', 'release_year', 'title_slug', 'url', 'genres', 'director', 'cast', 'rating', 'liked'])
        # liked_df = pd.DataFrame(columns=['title', 'watched_date', 'release_year', 'title_slug', 'url', 'genres', 'director', 'cast', 'rating', 'liked'])

        # with ThreadPoolExecutor(max_workers=10) as executor:
        #     future_diary = executor.submit(process_diary_movies, username, diary_df)
        #     future_liked = executor.submit(process_liked_movies, username, liked_df)

        #     st.session_state.diary_df = future_diary.result()
        #     st.session_state.liked_df = future_liked.result()

        # st.session_state.diary_df = grab_date_info(username, st.session_state.diary_df)
        # st.session_state.diary_df = grab_title_details(username, st.session_state.diary_df)
        # st.session_state.diary_df = grab_diary_movie_data_all_inclusive(st.session_state.diary_df)

        st.session_state.liked_df = update_liked_movies_with_slugs(username, st.session_state.liked_df)
        st.session_state.liked_df = grab_liked_movie_data_all_inclusive(username, st.session_state.liked_df)

        # liked_titles_set = set(st.session_state.liked_df['title'])
        # st.session_state.diary_df['liked'] = st.session_state.diary_df['title'].apply(lambda title: title in liked_titles_set)

        # final_df = pd.merge(st.session_state.diary_df, st.session_state.liked_df, on=['title', 'watched_date', 'release_year', 'title_slug', 'url', 'genres', 'director', 'cast', 'rating'], how='outer', suffixes=('', '_liked'))
        # final_df['liked'] = final_df.apply(lambda row: True if pd.notna(row['liked_liked']) else row['liked'], axis=1)
        # final_df.drop(columns=['liked_liked'], inplace=True)
        # final_df.drop_duplicates(subset=['title', 'release_year', 'title_slug', 'genres', 'director', 'cast', 'liked'], inplace=True)
        # final_df.reset_index(drop=True, inplace=True)

        # if not st.session_state.diary_df.empty:
        #     st.write(f"{username} has logged these films on the following dates:")
        #     st.write(st.session_state.diary_df.to_html(escape=False), unsafe_allow_html=True)
        # else:
        #     st.write("Can't seem to find any entries...")
        if not st.session_state.liked_df.empty:
            st.write(f"{username} has liked these films:")
            st.write(st.session_state.liked_df.to_html(escape=False), unsafe_allow_html=True)
        else:
            st.write("Can't seem to find any entries...")
        # if not final_df.empty:
        #     st.write(final_df.to_html(escape=False), unsafe_allow_html=True)
        # else:
        #     st.write("Can't seem to find any entries...")
    else:
        st.write("Please enter a username.")



col1, col2 = st.columns([5, 7])

with col1:
    st.markdown("""
    <div style='padding-top: 14px;'>
        <span style='color: rgb(102, 221, 103); font-size: 55px; font-weight: 700;'>
        Letter</span><span style='color: rgb(101, 186, 239); font-size: 55px; font-weight: 700; margin-left: -10px;'>
        Stats</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"<div style='margin-top: 59px; margin-left: -25px;'>made by <span style= 'color: rgb(239, 135, 51);'>@mat_lee</span></div>", unsafe_allow_html=True)


st.markdown('<i>the most comprehensive statlines for your Letterboxd account.</i>', unsafe_allow_html=True)

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