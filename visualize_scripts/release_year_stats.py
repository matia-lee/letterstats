import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def prepare_histogram(final_df):
    final_df['release_year'] = pd.to_numeric(final_df['release_year'], errors='coerce')
    final_df = final_df.dropna(subset=['release_year']).copy()
    final_df['release_year'] = final_df['release_year'].astype(int)
    release_year_movies = final_df.groupby('release_year')['title'].apply(list).reset_index(name='Movies')

    release_year_count = final_df['release_year'].value_counts().reset_index()
    release_year_count.columns = ["Release Year", "Count"]
    release_year_count = release_year_count.merge(release_year_movies, left_on="Release Year", right_on="release_year", how="left").drop(columns=["release_year"])
    
    return final_df, release_year_count

def plot_histogram(data, hover_data=None):
    def concise_hover_text(movies_list):
        if len(movies_list) <= 5:
            return "<br>".join(movies_list)
        else:
            more_count = len(movies_list) - 5
            displayed_movies = movies_list[:5]
            return "<br>".join(displayed_movies) + f"<br>and {more_count} more..."
        
    if hover_data is not None:
        data = data.copy()
        data['hover_text'] = hover_data.apply(concise_hover_text)
    else:
        data['hover_text'] = ""

    min_year = data['release_year'].min()
    max_year = data['release_year'].max()
    year_range = max_year - min_year + 1 

    year_range = int(year_range)

    fig = px.histogram(
        data, x='release_year', 
        nbins=year_range, 
        title="Distribution of Movie Release Years",
        hover_data=["hover_text"],
        labels={'release_year': 'Release Year', 'count': 'Count'}
    )

    # fig.update_traces(hovertemplate="%{customdata[0]}", textposition="outside")
    fig.update_traces(hovertemplate="<b>Year:</b> %{x}<br><b>Count:</b> %{y}<br>")

    fig.update_layout(bargap=0.2)
    fig.update_layout(
        yaxis=dict(ticks="outside", tickcolor="#101010", ticklen=10, tickfont=dict(size=14, color="#9b9b9b"), title=dict(font=dict(color="#9b9b9b"))), 
        xaxis=dict(ticks="outside", tickcolor="#101010", ticklen=10, tickfont=dict(size=14, color="#9b9b9b"), title=dict(font=dict(color="#9b9b9b"))),
        title={"text": "Distribution of Watched Movies' Release Years", "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b"), "pad": {"t": 20}},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
def prepare_average_rating(final_df):
    final_df['release_year'] = pd.to_numeric(final_df['release_year'], errors='coerce')
    final_df = final_df.dropna(subset=['release_year']).copy()
    final_df['release_year'] = final_df['release_year'].astype(int)
    final_df['rating'] = pd.to_numeric(final_df['rating'], errors='coerce')
    final_df = final_df.dropna(subset=['rating']).copy()
    
    avg_rating_by_release_year = final_df.groupby('release_year')['rating'].mean().reset_index(name='mean_rating')
    avg_rating_by_release_year['mean_rating'] = avg_rating_by_release_year['mean_rating'].round(1)

    release_year_movies = final_df.groupby('release_year')['title'].apply(list).reset_index(name='Movies')
    avg_rating_by_release_year = avg_rating_by_release_year.merge(release_year_movies, on="release_year", how="left")

    return avg_rating_by_release_year

def plot_average_rating(data):
    def concise_hover_text(movies_list):
        if len(movies_list) <= 5:
            return "<br>".join(movies_list)
        else:
            more_count = len(movies_list) - 5
            displayed_movies = movies_list[:5]
            return "<br>".join(displayed_movies) + f"<br>and {more_count} more..."
        
    if 'Movies' in data.columns:
        data['hover_text'] = data['Movies'].apply(concise_hover_text)
    else:
        data['hover_text'] = ""
    
    fig = px.bar(
        data_frame=data,
        x='release_year',
        y='mean_rating',
        title="Average Rating per Movie Release Year",
        hover_data=["hover_text"],
        labels={'release_year': 'Release Year', 'mean_rating': 'Rating'},
        color_discrete_sequence=["rgb(239, 135, 51)"]
    )

    fig.update_traces(hovertemplate="<b>Year:</b> %{x} <br> <b>Rating:</b> %{y} <br> <b>Movies:</b> %{customdata[0]}")
    
    fig.update_layout(bargap=0.2)
    fig.update_layout(
        yaxis=dict(ticks="outside", tickcolor="#101010", ticklen=10, tickfont=dict(size=14, color="#9b9b9b"), title=dict(font=dict(color="#9b9b9b"))),
        xaxis=dict(ticks="outside", tickcolor="#101010", ticklen=10, tickfont=dict(size=14, color="#9b9b9b"), title=dict(font=dict(color="#9b9b9b"))),
        title={"text": "Average Rating per Movie Release Year", "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b"), "pad": {"t": 20}},
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def release_year_stats(final_df):
    with st.expander("Release Year Stats"):
        release_year_df = final_df.copy()

        st.markdown("""
            <style>
            .fig-one-release-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-top: 30px !important;
                margin-bottom: -100px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="fig-one-release-font">Your watched movies and their release years:</p>
            """, unsafe_allow_html=True)
        fig1, release_year_count = prepare_histogram(release_year_df)
        plot_histogram(fig1, hover_data=release_year_count["Movies"])

        st.markdown("""
            <style>
            .fig-two-release-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-top: 0px !important;
                margin-bottom: -80px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="fig-two-release-font">Your watched movies sorted by release date and their average ratings:</p>
            """, unsafe_allow_html=True)
        fig2 = prepare_average_rating(release_year_df)
        plot_average_rating(fig2)
        