import plotly.express as px
import streamlit as st
import pandas as pd

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

def director_with_rating(final_df):
    final_df['director'] = final_df['director'].apply(lambda x: [director.strip().lower() for director in x.split(',')] if isinstance(x, str) else x)
    df_exploded = final_df.explode('director')
    df_exploded = df_exploded[~df_exploded['director'].str.contains("show", case=False, na=False)]
    director_counts = df_exploded['director'].value_counts().reset_index(name='count').rename(columns={'index': 'director'})
    top20_directors = director_counts.nlargest(20, 'count')
    df_filtered = df_exploded.merge(top20_directors[['director']], on='director')
    df_filtered['rating'] = pd.to_numeric(df_filtered['rating'], errors='coerce')
    avg_rating_by_director = df_filtered.groupby('director')['rating'].mean().reset_index(name='mean_rating')
    avg_rating_by_director['mean_rating'] = avg_rating_by_director['mean_rating'].round(1)
    avg_rating_by_director['director'] = avg_rating_by_director['director'].str.capitalize()
    
    return avg_rating_by_director

def prepare_data_for_boxplot(final_df):
    final_df['director'] = final_df['director'].apply(lambda x: [director.strip().lower() for director in x.split(',')] if isinstance(x, str) else x)
    df_exploded = final_df.explode('director')
    df_exploded = df_exploded[~df_exploded['director'].str.contains("show", case=False, na=False)]
    df_exploded['rating'] = pd.to_numeric(df_exploded['rating'], errors='coerce')
    director_counts = df_exploded['director'].value_counts().reset_index(name='count').rename(columns={'index': 'director'})
    top20_directors = director_counts.nlargest(20, 'count')['director']
    df_filtered = df_exploded[df_exploded['director'].isin(top20_directors)]
    df_filtered['director'] = df_filtered['director'].str.capitalize()
    
    return df_filtered

def lowest_director_with_rating(final_df):
    final_df['director'] = final_df['director'].apply(lambda x: [director.strip().lower() for director in x.split(',')] if isinstance(x, str) else x)
    df_exploded = final_df.explode('director')
    df_exploded = df_exploded[~df_exploded['director'].str.contains("show", case=False, na=False)]
    director_counts = df_exploded['director'].value_counts().reset_index(name='count').rename(columns={'index': 'director'})
    top20_directors = director_counts.nsmallest(20, 'count')
    df_filtered = df_exploded.merge(top20_directors[['director']], on='director')
    df_filtered['rating'] = pd.to_numeric(df_filtered['rating'], errors='coerce')
    avg_rating_by_director = df_filtered.groupby('director')['rating'].mean().reset_index(name='mean_rating')
    avg_rating_by_director['mean_rating'] = avg_rating_by_director['mean_rating'].round(1)
    avg_rating_by_director['director'] = avg_rating_by_director['director'].str.capitalize()
    
    return avg_rating_by_director

def create_avg_rating_by_director_graph_horizontal(avg_rating_by_director, title,  color,ccs=None):
    fig = px.bar(
        avg_rating_by_director, 
        y="director", x="mean_rating", orientation="h",
        text="mean_rating",  
        color_discrete_sequence=[color] if ccs is None else [ccs] * len(avg_rating_by_director),
        title="Average Rating per Director"
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
        title={"text": title, "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b")},
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def top_directors_top_genres(final_df):
    final_df['director'] = final_df['director'].apply(lambda x: [director.strip().lower() for director in x.split(',')] if isinstance(x, str) else x)
    director_df = final_df.explode('director')
    director_df['director'] = director_df['director'].str.strip().str.lower()
    director_df= director_df[~director_df['director'].str.contains(r'^Jr\.$', case=False, na=False)]
    director_df = director_df[~director_df['director'].str.contains("show", case=False, na=False)]

    director_df['genres'] = director_df['genres'].apply(lambda x: [genre.strip().lower() for genre in x.split(',')] if isinstance(x, str) else x)
    director_df = director_df.explode('genres')
    director_df['genres'] = director_df['genres'].str.strip().str.lower()
    director_df = director_df[~director_df['genres'].str.contains("show", case=False, na=False)]

    top_directors = director_df['director'].value_counts().head(10).index.tolist()
    director_genres = []
    
    for director in top_directors:
        director_movies = director_df[director_df['director'] == director]
        genres = director_movies['genres'].value_counts().head(3)
        df = pd.DataFrame({'Director': [director.capitalize()] * len(genres),
                           'Genre': genres.index,
                           'Count': genres.values})
        director_genres.append(df)
    
    return pd.concat(director_genres, ignore_index=True)

def plot_top_directors_top_genres(data):
    fig = px.bar(
        data,
        x="Director",
        y="Count",
        color = "Genre",
        barmode="stack",
        title="Top Directors top Genres",
    )

    fig.update_layout(
        xaxis_title="Director/Genre",
        yaxis_title="Count",
        legend_title="Genre",
        font=dict(color="#9b9b9b", size=12),
        xaxis=dict(
            title_font=dict(color="#9b9b9b"),  
        ),
        yaxis=dict(
            title_font=dict(color="#9b9b9b"), 
        ),
        legend=dict(
            title_font=dict(color="#9b9b9b"), 
            font=dict(color="#9b9b9b")
        ),
        title={"text": "Most Watched Directors and the Genres of Their Movies", "y":0.8, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b"), "pad": {"t": -20}},
    )

    fig.update_xaxes(tickfont=dict(color="#9b9b9b"))
    fig.update_yaxes(tickfont=dict(color="#9b9b9b"))

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def director_stats(final_df):
    with st.expander("Director Stats"):
        director_df = final_df
        all_directors = director_df["director"].str.split(", ").explode()
        all_directors = all_directors[~all_directors.str.contains("show", case=False, na=False)]
        director_count = all_directors.value_counts().reset_index()
        director_count.columns = ["Director", "Count"]

        top_10_common_directors = director_count.head(10).sort_values(by="Count", ascending=True)
        bottom_10_common_directors = director_count.tail(10)

        liked_movies = director_df[director_df["liked"] == True]
        high_rated_directors = liked_movies["director"].str.split(", ").explode()
        high_rated_directors = high_rated_directors[~high_rated_directors.str.contains("show", case=False, na=False)]
        high_rated_directors = high_rated_directors[~high_rated_directors.str.contains(r'^Jr\.$', case=False, na=False)]
        high_rated_directors = high_rated_directors.value_counts().reset_index()
        high_rated_directors.columns = ["Director", "Count"]
        top_directors_high_rated = high_rated_directors.head(10).sort_values(by="Count", ascending=True)

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
            <p class="big-font">Most watched directors:</p>
            """, unsafe_allow_html=True)
        fig1 = create_bar_graph(top_10_common_directors, x="Count", y="Director", title="Most Watched Directors", color="rgb(102, 221, 103)")
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
            <p class="big-font">Least watched directors</p>
            """, unsafe_allow_html=True)
        fig3 = create_bar_graph(bottom_10_common_directors, x="Count", y="Director", title="Least Watched Directors", color="rgb(101, 186, 239)")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

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
            <p class="big-font">Top directors from your liked movies:</p>
            """, unsafe_allow_html=True)
        fig2 = create_bar_graph(top_directors_high_rated, x="Count", y="Director", title="Common Directors from Movies you've Liked", color="rgb(239, 135, 51)")
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
            <p class="big-font">Average rating per director:</p>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <style>
            .small-font {
                font-size:15px !important;
                margin-top: -10px !important;
                z-index: 410 !important;
                position: absolute !important;
            }
            </style>
            <p class="small-font">(From your 20 most watched directors)</p>
            """, unsafe_allow_html=True)
        fig3 = director_with_rating(final_df)
        create_avg_rating_by_director_graph_horizontal(fig3, title="Average Rating per Most Watched Director", color="#967BB6")

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
            <p class="big-font">Average rating per director:</p>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <style>
            .small-font {
                font-size:15px !important;
                margin-top: -10px !important;
                z-index: 410 !important;
                position: absolute !important;
            }
            </style>
            <p class="small-font">(From 20 of your least watched directors) (No data means you've lef their movie unrated)</p>
            """, unsafe_allow_html=True)
        fig4 = lowest_director_with_rating(final_df)
        create_avg_rating_by_director_graph_horizontal(fig4, title="Average Rating per Least Watched Director", color="#E6A9A9")

        st.markdown("""
            <style>
            .big-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: -70px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="big-font">Most watched directors and their genres:</p>
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
            <p class="small-font">(Based on your watched movies)</p>
            """, unsafe_allow_html=True)
        
        fig5 = top_directors_top_genres(final_df)
        plot_top_directors_top_genres(fig5)