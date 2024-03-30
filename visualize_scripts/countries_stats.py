import streamlit as st
import plotly.express as px
import pycountry
import pandas as pd

def get_iso_alpha_3(country_name):
    special_cases = {
        "UK": "GBR",
        "USSR": "RUS",
        "Turkey": "TUR",
        "Ivory Coast": "CIV",
        "State of Palestine": "PSE"
    }
    
    if country_name in special_cases:
        return special_cases[country_name]
    
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_3
    except LookupError:
        # print(f"Country not found: {country_name}")
        return None

def prepare_world_map(final_df):
    final_df["countries"] = final_df["countries"].str.split(", ")
    final_df = final_df.explode("countries")
    final_df = final_df[~final_df["countries"].str.contains("show", case=False, na=False)]
    final_df["iso_alpha"] = final_df["countries"].apply(get_iso_alpha_3)
    country_movies = final_df.groupby("iso_alpha")["title"].apply(list).reset_index(name="Movies")

    country_counts = final_df["iso_alpha"].value_counts().reset_index()
    country_counts.columns = ["iso_alpha", "movies_watched"]
    country_counts = country_counts.merge(country_movies, on="iso_alpha", how="left")

    country_counts["country_name"] = country_counts["iso_alpha"].apply(lambda x: pycountry.countries.get(alpha_3=x).name if x else "Unknown")

    return country_counts

def create_bar_graph(data, x, y, title, color="skyblue", hover_data=None, ccs=None):
    def concise_hover_text(movies_list):
        if len(movies_list) <= 5:
            return "<br>".join(movies_list)
        else:
            more_count = len(movies_list) - 5
            displayed_movies = movies_list[:5]
            return "<br>".join(displayed_movies) + f"<br>and {more_count} more..."

    if hover_data is not None:
        data = data.copy()
        data["hover_text"] = hover_data.apply(concise_hover_text)
    else:
        data["hover_text"] = ""

    fig = px.bar(
        data, y=y, x=x, orientation="h",
        color_discrete_sequence=[color] if ccs is None else [ccs] * len(data),
        text=x,
        hover_data=["hover_text"]
    )

    fig.update_traces(hovertemplate="%{customdata[0]}", textposition="outside")

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

def plot_world_map(data, hover_data=None):
    def concise_hover_text(movies_list):
        if len(movies_list) <= 5:
            return "<br>".join(movies_list)
        else:
            more_count = len(movies_list) - 5
            displayed_movies = movies_list[:5]
            return "<br>".join(displayed_movies) + f"<br>and {more_count} more..."

    if hover_data is not None:
        data = data.copy()
        data["hover_text"] = hover_data.apply(concise_hover_text)
    else:
        data["hover_text"] = ""

    colour_scale = [
        [0, "rgb(255, 224, 189)"],
        [1, "rgb(255, 140, 0)"]
    ]

    data["Movies"] = data["Movies"].apply(lambda x: [str(i) for i in x])

    data["hover_text"] = data["Movies"].apply(concise_hover_text)

    fig = px.choropleth(
        data_frame=data,
        locations="iso_alpha",
        locationmode="ISO-3",
        color="movies_watched",
        hover_name="country_name",
        hover_data={
            "iso_alpha": False,  
            "movies_watched": ":.2s",  
            "country_name": False,  
            "hover_text": True 
        },
        color_continuous_scale=colour_scale,
        title="Movies Watched by Country"
    )

    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br><b>Count: </b>%{customdata[1]}<br>%{customdata[3]}<extra></extra>")

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",  
        paper_bgcolor="rgba(0,0,0,0)", 
        geo=dict(
            bgcolor="rgba(0,0,0,0)" 
        ),
        title={"text": "Movies Watched by Country", "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b"), "pad": {"t": 20}},
        legend=dict(font=dict(color="#9b9b9b"))
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def countries_with_rating(final_df):
    final_df["countries"] = final_df["countries"].apply(lambda x: [countries.strip().lower() for countries in x.split(",")] if isinstance(x, str) else x)
    df_exploded = final_df.explode("countries")
    df_exploded = df_exploded[~df_exploded["countries"].str.contains("show", case=False, na=False)]

    countries_counts = df_exploded["countries"].value_counts().reset_index(name="count").rename(columns={"index": "countries"})
    top20_countriess = countries_counts.nlargest(20, "count")
    df_exploded = df_exploded.merge(top20_countriess[["countries"]], on="countries")

    df_exploded["rating"] = pd.to_numeric(df_exploded["rating"], errors="coerce")
    avg_rating_by_countries = df_exploded.groupby("countries")["rating"].mean().reset_index(name="mean_rating")
    avg_rating_by_countries["mean_rating"] = avg_rating_by_countries["mean_rating"].round(1)
    avg_rating_by_countries["countries"] = avg_rating_by_countries["countries"].str.capitalize()
    
    return avg_rating_by_countries

def create_avg_rating_by_countries_graph_horizontal(avg_rating_by_countries):
    # avg_rating_by_countries = avg_rating_by_countries.sort_values("mean_rating", ascending=True)

    fig = px.bar(
        avg_rating_by_countries, 
        y="countries", x="mean_rating", orientation="h",
        text="mean_rating",  
        color_discrete_sequence=["skyblue"] * len(avg_rating_by_countries),
        title="Average Rating per countries"
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
        title={"text": "Average Rating per Countries", "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b")},
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def countries_stats(final_df):
    with st.expander("Countries Stats"):
        countries_df = final_df.copy()

        st.markdown("""
            <style>
            .world-map-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-top: 50px !imporant;
                margin-bottom: -200px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="world-map-font">Your movies from across the world:</p>
            """, unsafe_allow_html=True)
        fig1 = prepare_world_map(countries_df)
        plot_world_map(fig1)
        
        fig2df = final_df.copy()
        fig2df["countries"] = fig2df["countries"].str.split(", ")
        fig2df = fig2df.explode("countries")
        fig2df = fig2df[~fig2df["countries"].str.contains("show", case=False, na=False)]
        countries_movies = fig2df.groupby("countries")["title"].apply(list).reset_index(name="Movies")

        countries_count = fig2df["countries"].value_counts().reset_index()
        countries_count.columns = ["Countries", "Count"]
        countries_count = countries_count.merge(countries_movies, left_on="Countries", right_on="countries", how="left").drop(columns=["countries"])

        top_10_common_countries = countries_count.head(10).sort_values(by="Count", ascending=True)

        st.markdown("""
            <style>
            .fig2-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-top: 50px !imporant;
                margin-bottom: 0px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="fig2-font">The countries that your most watched movies are from:</p>
            """, unsafe_allow_html=True)
        fig2 = create_bar_graph(top_10_common_countries, x="Count", y="Countries", title="Most Watched Countries", color="rgb(102, 221, 103)", hover_data=top_10_common_countries["Movies"])
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        liked_movies_df = final_df[final_df["liked"] == True].copy()
        liked_movies_df["countries"] = liked_movies_df["countries"].str.split(", ")
        liked_movies_df = liked_movies_df.explode("countries")
        liked_movies_df = liked_movies_df[~liked_movies_df["countries"].str.contains("show", case=False, na=False)]
        liked_countries_movies = liked_movies_df.groupby("countries")["title"].apply(list).reset_index(name="Movies")
        countries_counted = liked_movies_df["countries"].value_counts().reset_index()
        countries_counted.columns = ["Countries", "Count"]
        countries_counted = countries_counted.merge(liked_countries_movies, left_on="Countries", right_on="countries", how="left").drop(columns=["countries"])
        top_countries_high_rated = countries_counted.head(10).sort_values(by="Count", ascending=True)

        st.markdown("""
            <style>
            .fig2-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-top: 50px !imporant;
                margin-bottom: 0px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="fig2-font">The countries that your liked movies are from:</p>
            """, unsafe_allow_html=True)
        fig3 = create_bar_graph(top_countries_high_rated, x="Count", y="Countries", title="Countries of the Movies You've Liked", color="rgb(239, 135, 51)", hover_data=top_countries_high_rated["Movies"])
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        
        st.markdown("""
            <style>
            .fig4-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-top: 90px !imporant;
                margin-bottom: -80px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="fig4-font">Average rating per country:</p>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <style>
            .fig4-small-font {
                font-size:15px !important;
                margin-top: 40px !important;
                z-index: 410 !important;
                position: absolute !important;
            }
            </style>
            <p class="fig4-small-font">(From your 20 most watched countries in order)</p>
            """, unsafe_allow_html=True)
        fig4df = final_df.copy()
        fig4 = countries_with_rating(fig4df)
        create_avg_rating_by_countries_graph_horizontal(fig4)