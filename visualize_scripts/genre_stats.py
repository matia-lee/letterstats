import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
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
        font=dict(color="#9b9b9b", size=12),
        margin=dict(b=30),
    )

    fig.update_traces(showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(
        yaxis=dict(ticks="outside", tickcolor="#101010", ticklen=10, tickfont=dict(size=14, color="#9b9b9b")), 
        title={"text": title, "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b"), "pad": {"t": -20}},
    )

    return fig

def create_genre_over_time_graph(most_watched_genre_per_month):
    fig = px.bar(
        most_watched_genre_per_month, 
        x="year_month", y="Count", color="Most Watched Genre", 
        text="Count", 
        title="Most Watched Genre Each Month (Last 12 Months)"
    )

    fig.update_traces(hovertemplate="%{x}", textposition="outside")

    fig.update_layout(
        plot_bgcolor="rgb(15,17,22)", paper_bgcolor="rgb(15,17,22)",
        font=dict(color="#9b9b9b", size=12),
        yaxis=dict(
            title="Number of Watches",
            titlefont=dict(color="#9b9b9b"),  
            tickfont=dict(color="#9b9b9b"),
        ),
        xaxis=dict(
            title="Month",
            titlefont=dict(color="#9b9b9b"), 
            tickfont=dict(color="#9b9b9b"), 
        ),
        legend_title_text="Genre",
        legend_title_font=dict(color="#9b9b9b"),  
        legend=dict(
            font=dict(color="#9b9b9b") 
        ),
        title={"text": "Most Watched Genre Each Month (Last 12 Months)", "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b"), "pad": {"t": 10}},
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def genre_stats_over_months(final_df):
    final_df["watched_date"] = pd.to_datetime(final_df["watched_date"], format='%d %b %Y')

    last_12_months = datetime.now() - timedelta(days=395)
    filtered_df = final_df[final_df["watched_date"] >= last_12_months]

    all_genres = filtered_df.assign(genres=filtered_df["genres"].str.split(", ")).explode("genres")
    all_genres = all_genres[~all_genres['genres'].str.contains("show", case=False, na=False)]
    all_genres["year_month"] = all_genres["watched_date"].dt.to_period("M")

    monthly_genre_counts = all_genres.groupby(["year_month", "genres"]).size().reset_index(name="counts")

    genre_pivot = monthly_genre_counts.pivot(index="year_month", columns="genres", values="counts").fillna(0)

    most_watched_genre_per_month = genre_pivot.idxmax(axis=1).reset_index(name="Most Watched Genre")

    most_watched_counts_per_month = genre_pivot.max(axis=1).reset_index(name="Count")
    most_watched_genre_per_month["Count"] = most_watched_counts_per_month["Count"]

    most_watched_genre_per_month["year_month"] = most_watched_genre_per_month["year_month"].astype(str)

    return most_watched_genre_per_month.tail(13)

def calculate_diversity(final_df):
    final_df["watched_date"] = pd.to_datetime(final_df["watched_date"], format='%d %b %Y')

    last_12_months = datetime.now() - timedelta(days=395)
    filtered_df = final_df[final_df["watched_date"] >= last_12_months]

    all_genres = filtered_df.assign(genres=filtered_df["genres"].str.split(", ")).explode("genres")
    all_genres = all_genres[~all_genres['genres'].str.contains("show", case=False, na=False)]
    all_genres["year_month"] = all_genres["watched_date"].dt.to_period("M")

    monthly_genre_counts = all_genres.groupby(["year_month", "genres"]).size().reset_index(name="counts")
    monthly_totals = all_genres.groupby("year_month").size().reset_index(name="total_movies")

    monthly_genre_counts['proportion'] = monthly_genre_counts.groupby('year_month')['counts'].transform(lambda x: x / float(x.sum()))
    monthly_genre_counts['shannon_diversity'] = -(monthly_genre_counts['proportion'] * np.log(monthly_genre_counts['proportion']))
    shannon_diversity_index = monthly_genre_counts.groupby('year_month')['shannon_diversity'].sum().reset_index()

    diversity_and_totals = pd.merge(shannon_diversity_index, monthly_totals, on="year_month")
    diversity_and_totals["year_month"] = diversity_and_totals["year_month"].astype(str)

    return diversity_and_totals.tail(13)

def plot_diversity(diversity_and_totals_df):
    bar_color = "#636EFA" 
    line_color = "#c79fef" 

    bar_chart = go.Bar(
        x=diversity_and_totals_df["year_month"], 
        y=diversity_and_totals_df["total_movies"], 
        name="Total Movies",
        marker_color=bar_color,
        yaxis='y',
        hovertemplate='<b>%{y} movies</b> %{x}<extra></extra>',
    )

    line_chart = go.Scatter(
        x=diversity_and_totals_df["year_month"], 
        y=diversity_and_totals_df["shannon_diversity"], 
        name="Shannon Diversity Index", 
        mode='lines+markers',
        marker_color=line_color,
        yaxis='y2',
        hoverinfo='none',
    )

    fig = go.Figure(data=[bar_chart, line_chart])

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9b9b9b"),
        title={"text": "Genre Diversity Compared to Movies Watched per Month", "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b"), "pad": {"t": 10}},
        xaxis=dict(
            title="Month",
            titlefont=dict(color="#9b9b9b"),
            tickfont=dict(color="#9b9b9b")
        ),
        yaxis=dict(
            title="Total Movies Watched",
            titlefont=dict(color="#9b9b9b"),
            tickfont=dict(color="#9b9b9b"),
            showgrid=False,
            color=bar_color
        ),
        yaxis2=dict(
            title="Shannon Diversity Index",
            titlefont=dict(color="#9b9b9b"),
            tickfont=dict(color="#9b9b9b"),
            overlaying="y",
            side="right",
            showgrid=False,
            color=line_color
        ),
        legend=dict(yanchor="top", y=-0.1, xanchor="left", x=0.7, font=dict(color="#9b9b9b"),)
    )

    fig.update_layout(autosize=True)
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def genre_with_rating(final_df):
    final_df['genres'] = final_df['genres'].apply(lambda x: [genre.strip().lower() for genre in x.split(',')] if isinstance(x, str) else x)
    df_exploded = final_df.explode('genres')
    df_exploded = df_exploded[~df_exploded['genres'].str.contains("show", case=False, na=False)]
    df_exploded['rating'] = pd.to_numeric(df_exploded['rating'], errors='coerce')
    avg_rating_by_genre = df_exploded.groupby('genres')['rating'].mean().reset_index(name='mean_rating')
    avg_rating_by_genre['mean_rating'] = avg_rating_by_genre['mean_rating'].round(1)
    avg_rating_by_genre['genres'] = avg_rating_by_genre['genres'].str.capitalize()
    
    return avg_rating_by_genre

def create_avg_rating_by_genre_graph_horizontal(avg_rating_by_genre):
    fig = px.bar(
        avg_rating_by_genre, 
        y="genres", x="mean_rating", orientation="h",
        text="mean_rating",  
        color_discrete_sequence=["skyblue"] * len(avg_rating_by_genre),
        title="Average Rating per Genre"
    )

    fig.update_traces(hovertemplate="%{x:.2f} <b>Avg Rating</b>", textposition="outside")

    fig.update_layout(
        barmode="stack",
        yaxis_visible=True, yaxis_showticklabels=True,
        xaxis_title=None, yaxis_title=None, xaxis_visible=True,
        plot_bgcolor="rgb(15,17,22)", paper_bgcolor="rgb(15,17,22)",
        font=dict(color="#9b9b9b", size=12),
        margin=dict(b=30),
        height=600,
        yaxis = dict(tickfont=dict(color="#9b9b9b")),
    )

    fig.update_traces(showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(
        xaxis=dict(ticks="outside", tickcolor="#101010", ticklen=10, tickfont=dict(size=14, color="#9b9b9b")),
        title={"text": "Average Rating per Genre", "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b")},
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def genre_stats(final_df):
    with st.expander("Genre Stats"):
        all_genres = final_df["genres"].str.split(", ").explode()
        all_genres = all_genres[~all_genres.str.contains("show", case=False, na=False)]

        genre_counts = all_genres.value_counts().reset_index()
        genre_counts.columns = ["Genre", "Count"]

        top_10_common_genres = genre_counts.head(10).sort_values(by="Count", ascending=True)
        top_10_uncommon_genres = genre_counts.tail(10)

        liked_movies_df = final_df[final_df["liked"] == True]
        high_rated_genres = liked_movies_df["genres"].str.split(", ").explode()
        high_rated_genres = high_rated_genres[~high_rated_genres.str.contains("show", case=False, na=False)]
        high_rated_genres = high_rated_genres.value_counts().reset_index()
        high_rated_genres.columns = ["Genre", "Count"]
        top_genres_high_rated = high_rated_genres.head(10).sort_values(by="Count", ascending=True)

        st.markdown("""
            <style>
            .big-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: 20px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="big-font">Most watched genres:</p>
            """, unsafe_allow_html=True)
        fig1 = create_bar_graph(top_10_common_genres, x="Count", y="Genre", title="Most Watched Genres", color="rgb(102, 221, 103)")
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
            <style>
            .big-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: 20px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="big-font">Least watched genres:</p>
            """, unsafe_allow_html=True)
        fig2 = create_bar_graph(top_10_uncommon_genres, x="Count", y="Genre", title="Least Watched Genres", color="rgb(101, 186, 239)")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
            <style>
            .big-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: 20px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="big-font">Top genres from your liked movies:</p>
            """, unsafe_allow_html=True)
        fig3 = create_bar_graph(top_genres_high_rated, x="Count", y="Genre", title="Common Genres from Movies you've Liked", color="rgb(239, 135, 51)")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
            <style>
            .big-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: -40px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="big-font">The most watched genres per month from the past year:</p>
            """, unsafe_allow_html=True)
        most_watched_genre_per_month = genre_stats_over_months(final_df)
        create_genre_over_time_graph(most_watched_genre_per_month)

        st.markdown("""
            <style>
            .big-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: -40px !important;
                z-index: 400 !important;
            }
            </style>
            <p class="big-font">Genre diversity compared to the amount of movies you've watched per month from the past year:</p>
            """, unsafe_allow_html=True)

        st.markdown("""
            <style>
            .small-font {
                font-size:15px !important;
                margin-top: 40px !important;
                z-index: 410 !important;
                position: absolute !important;
            }
            </style>
            <p class="small-font">(The higher the Shannon Diversity Index, the more genres you've explored that month)</p>
            """, unsafe_allow_html=True)
        calculated_diversity = calculate_diversity(final_df)
        plot_diversity(calculated_diversity)

        st.markdown("""
            <style>
            .average {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: -100px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="average">Average Rating per Genre:</p>
            """, unsafe_allow_html=True)
        average_rating_per_genre = genre_with_rating(final_df)
        create_avg_rating_by_genre_graph_horizontal(average_rating_per_genre)