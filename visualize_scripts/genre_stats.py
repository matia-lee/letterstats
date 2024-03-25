import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta

def calculate_total_watched_time(final_df):
    total_runtime = final_df["runtime"].sum()
    total_runtime_int = int(total_runtime)
    max_index = final_df["title"].idxmax()
    st.write(f"<u>You've watched a total of {total_runtime_int} minutes of cinema!</u>", unsafe_allow_html=True)
    st.write("Check out some stats below: ")
    # st.write(f"That means, you've watched over {max_index} movies")
    return total_runtime_int, max_index

def create_bar_graph(data, x, y, title, color="skyblue", ccs=None):
    fig = px.bar(
        data, y=y, x=x, orientation="h",
        color_discrete_sequence=[color] if ccs is None else [ccs] * len(data),
        text=x  
    )

    fig.update_traces(hovertemplate="%{x} <b>Films</b>", textposition="outside")

    fig.update_layout(
        barmode="stack",
        yaxis_visible=True, yaxis_showticklabels=True,
        xaxis_title=None, yaxis_title=None, xaxis_visible=False,
        plot_bgcolor="rgb(15,17,22)", paper_bgcolor="rgb(15,17,22)",
        font=dict(color="white", size=12),
        margin=dict(b=30),
    )

    fig.update_traces(showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(
        yaxis=dict(ticks="outside", tickcolor="#101010", ticklen=10, tickfont=dict(size=14)), 
        title={"text": title, "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="white"), "pad": {"t": -20}},
    )

    return fig

def create_genre_over_time_graph(most_watched_genre_per_month):
    fig = px.bar(
        most_watched_genre_per_month, 
        x="year_month", y="Count", color="Most Watched Genre", 
        text="Count", 
        title="Most Watched Genre Each Month (Last 12 Months)"
    )

    fig.update_traces(hovertemplate=" ", textposition="outside")

    fig.update_layout(
        plot_bgcolor="rgb(15,17,22)", paper_bgcolor="rgb(15,17,22)",
        font=dict(color="white", size=12),
        yaxis=dict(title="Number of Watches"),
        xaxis=dict(title="Month"),
        legend_title_text="Genre",
        title={"text": "Most Watched Genre Each Month (Last 12 Months)", "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="white"), "pad": {"t": 10}},
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def genre_stats_over_months(final_df):
    final_df["watched_date"] = pd.to_datetime(final_df["watched_date"], errors="coerce", dayfirst=True)

    last_12_months = datetime.now() - timedelta(days=365)
    filtered_df = final_df[final_df["watched_date"] >= last_12_months]

    all_genres = filtered_df.assign(genres=filtered_df["genres"].str.split(", ")).explode("genres")
    all_genres["year_month"] = all_genres["watched_date"].dt.to_period("M")
    monthly_genre_counts = all_genres.groupby(["year_month", "genres"]).size().reset_index(name="counts")
    
    genre_pivot = monthly_genre_counts.pivot(index="year_month", columns="genres", values="counts").fillna(0)
    most_watched_genre_per_month = genre_pivot.idxmax(axis=1).reset_index(name="Most Watched Genre")
    most_watched_counts_per_month = genre_pivot.max(axis=1).reset_index(name="Count")
    most_watched_genre_per_month["Count"] = most_watched_counts_per_month["Count"]

    most_watched_genre_per_month = most_watched_genre_per_month.sort_values(by="year_month", ascending=False)
    most_watched_genre_per_month["year_month"] = most_watched_genre_per_month["year_month"].astype(str)

    return most_watched_genre_per_month

def genre_stats(final_df):
    with st.expander("Genre Stats"):
        all_genres = final_df["genres"].str.split(", ").explode()
        genre_counts = all_genres.value_counts().reset_index()
        genre_counts.columns = ["Genre", "Count"]
        
        top_10_common_genres = genre_counts.head(10).sort_values(by="Count", ascending=True)
        top_10_uncommon_genres = genre_counts.tail(10)

        liked_movies_df = final_df[final_df["liked"] == True]
        high_rated_genres = liked_movies_df["genres"].str.split(", ").explode().value_counts().reset_index()
        high_rated_genres.columns = ["Genre", "Count"]
        top_genres_high_rated = high_rated_genres.head(10).sort_values(by="Count", ascending=True)

        fig1 = create_bar_graph(top_10_common_genres, x="Count", y="Genre", title="Most Watched Genres", color="rgb(102, 221, 103)")
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

        fig2 = create_bar_graph(top_10_uncommon_genres, x="Count", y="Genre", title="Least Watched Genres", color="rgb(101, 186, 239)")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        fig3 = create_bar_graph(top_genres_high_rated, x="Count", y="Genre", title="Common Genres from Movies you've Liked", color="rgb(239, 135, 51)")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        most_watched_genre_per_month = genre_stats_over_months(final_df)
        create_genre_over_time_graph(most_watched_genre_per_month)