import requests
import streamlit as st

def valid_letterboxd_username(username):
    url = f"https://letterboxd.com/{username}/"
    response = requests.get(url)

    if response.status_code == 200:
        return username
    else:
        st.error("Hmmmm couldn't find anything, are you sure the username is correct?")
        return False