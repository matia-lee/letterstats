import requests
import streamlit as st

def valid_letterboxd_username(username):
    url = f"https://letterboxd.com/{username}/"
    response = requests.get(url)

    if response.status_code == 200:
        return username
    else:
        st.write("Hmmmm, are you sure the username is correct?")