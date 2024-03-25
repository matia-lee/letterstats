import pandas as pd
import streamlit as st
import multiprocessing
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from parsing_scripts.valid_username_check import valid_letterboxd_username
from parsing_scripts.dates_from_diary import grab_date_info
from parsing_scripts.grab_title_details import grab_title_details
from parsing_scripts.diary_movie_info import grab_diary_movie_info_async
from parsing_scripts.liked_movie_info import grab_liked_movie_info_async
from parsing_scripts.update_liked_df import update_liked_movies_with_slugs

from visualize_scripts.genre_stats import calculate_total_watched_time
from visualize_scripts.genre_stats import genre_stats

st.set_page_config(page_title="LetterStats", page_icon="🍿")

# st.markdown("""
# <style>
# button {
#     top: 20px;
#     right: 10px;
# }
# </style>
# """, unsafe_allow_html=True)

if 'refresh_trigger' not in st.session_state:
    st.session_state['refresh_trigger'] = 0

if st.button("↻", key="refresh_button", help="Refresh Cache (warning: this will cause it to gather the data again)"):
    st.session_state['refresh_trigger'] += 1
    st.rerun()

if 'diary_df' not in st.session_state:
    st.session_state['diary_df'] = pd.DataFrame()
if 'liked_df' not in st.session_state:
    st.session_state['liked_df'] = pd.DataFrame()

pd.set_option('future.no_silent_downcasting', True)

def run_asyncio_tasks(username, diary_df, liked_df):
    async def async_wrapper():
        async with aiohttp.ClientSession() as session:
            diary_task = asyncio.create_task(grab_diary_movie_info_async(diary_df, session))
            liked_task = asyncio.create_task(grab_liked_movie_info_async(username, liked_df, session))
            updated_diary_df, updated_liked_df = await asyncio.gather(diary_task, liked_task)
            return updated_diary_df, updated_liked_df
    with ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, async_wrapper())
        updated_diary_df, updated_liked_df = future.result()
        updated_liked_df.replace("", pd.NA, inplace=True)
        liked_titles_set = set(updated_liked_df['title'])
        updated_diary_df['liked'] = updated_diary_df['title'].apply(lambda title: title in liked_titles_set)
        final_df = pd.merge(updated_diary_df, updated_liked_df, on=['title', 'watched_date', 'release_year', 'title_slug', 'url', 'genres', 'director', 'cast', 'countries', 'studios', 'primary_language', 'spoken_languages', 'runtime', 'rating'], how='outer', suffixes=('', '_liked'))
        final_df['liked'] = final_df.apply(lambda row: True if pd.notna(row.get('liked_liked')) else row['liked'], axis=1)
        final_df.drop(columns=['liked_liked'], inplace=True)
        # final_df.drop_duplicates(subset=['title', 'release_year', 'title_slug', 'genres', 'director', 'cast', 'countries', 'studios', 'primary_language', 'spoken_languages', 'runtime', 'liked'], inplace=True)


        # final_df.drop_duplicates(subset=['title', 'release_year', 'genres', 'director', 'cast', 'countries', 'studios', 'primary_language', 'spoken_languages', 'runtime', 'liked'], inplace=True)
        duplicate_marker = final_df.duplicated(subset=[
            "title", "release_year", "genres", "director", "cast",
            "countries", "studios", "primary_language", "spoken_languages",
            "runtime", "liked"
        ], keep=False) 
        final_df.drop_duplicates(subset=['title', 'watched_date', 'release_year', 'title_slug', 'url', 'genres', 'director', 'cast', 'countries', 'studios', 'primary_language', 'spoken_languages', 'runtime', 'rating', 'liked'], inplace=True)
        duplicate_marker = duplicate_marker & final_df['watched_date'].isna()
        final_df = final_df[~duplicate_marker]
        final_df.reset_index(drop=True, inplace=True)
        return final_df
    
@st.cache_data
def construct_final_df(username, diary_df, liked_df, refresh_trigger):
    diary_df = grab_date_info(username, diary_df)
    diary_df = grab_title_details(username, diary_df)
    liked_df = update_liked_movies_with_slugs(username, liked_df)

    final_df = run_asyncio_tasks(username, diary_df, liked_df)
    return final_df

def fetch_and_display_films(username):
    is_valid = valid_letterboxd_username(username)
    if not is_valid:
        return
    
    if 'final_df' not in st.session_state:
        st.session_state['final_df'] = pd.DataFrame()

    if username and username != st.session_state.get('last_username', ''):
        st.session_state['last_username'] = username

        loading_message = st.empty()
        loading_message.info("This may take a couple mins depending on how many movies you've watched...")

        # diary_df = st.session_state['diary_df']
        # liked_df = st.session_state['liked_df']

        final_df = construct_final_df(username, st.session_state['diary_df'], st.session_state['liked_df'], st.session_state['refresh_trigger'])

        # diary_df = grab_date_info(username, diary_df)
        # diary_df = grab_title_details(username, diary_df)
        # liked_df = update_liked_movies_with_slugs(username, liked_df)

        # final_df = run_asyncio_tasks(username, diary_df, liked_df)

        st.session_state['final_df'] = final_df

        loading_message.empty()

        if not final_df.empty:
            # st.write(final_df.to_html(escape=False), unsafe_allow_html=True)
            st.write(f"<h1><i>{username}</i>'s LetterStats 🍿</h1>", unsafe_allow_html=True)
            calculate_total_watched_time(st.session_state['final_df'])
            genre_stats(st.session_state['final_df'])
        else:
            st.write("Can't seem to find any entries...")
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