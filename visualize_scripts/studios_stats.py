import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

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
        data['hover_text'] = hover_data.apply(concise_hover_text)
    else:
        data['hover_text'] = ""

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

def studio_with_rating(final_df):
    final_df["studios"] = final_df["studios"].apply(lambda x: [studios.strip().lower() for studios in x.split(",")] if isinstance(x, str) else x)
    df_exploded = final_df.explode("studios")
    df_exploded = df_exploded[~df_exploded["studios"].str.contains("show", case=False, na=False)]
    studios_counts = df_exploded["studios"].value_counts().reset_index(name="count").rename(columns={"index": "studios"})
    top20_studios = studios_counts.nlargest(20, "count")
    df_filtered = df_exploded.merge(top20_studios[["studios"]], on="studios")
    df_filtered["rating"] = pd.to_numeric(df_filtered["rating"], errors="coerce")
    avg_rating_by_studios = df_filtered.groupby("studios")["rating"].mean().reset_index(name="mean_rating")
    avg_rating_by_studios["mean_rating"] = avg_rating_by_studios["mean_rating"].round(1)
    avg_rating_by_studios["studios"] = avg_rating_by_studios["studios"].str.capitalize()
    
    return avg_rating_by_studios

def create_avg_rating_by_studios_graph_horizontal(avg_rating_by_studios, title, color, ccs=None):
    fig = px.bar(
        avg_rating_by_studios, 
        y="studios", x="mean_rating", orientation="h",
        text="mean_rating",  
        color_discrete_sequence=[color] if ccs is None else [ccs] * len(avg_rating_by_studios),
        title="Average Rating per Studios"
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

def studio_stats(final_df):
    with st.expander("Studio Stats"):
        studio_df = final_df.copy()
        studio_df['studios'] = studio_df['studios'].str.split(", ")
        studio_df = studio_df.explode('studios')
        studio_df = studio_df[~studio_df['studios'].str.contains("show", case=False, na=False)]
        studio_movies = studio_df.groupby('studios')['title'].apply(list).reset_index(name='Movies')
        
        studio_count = studio_df['studios'].value_counts().reset_index()
        studio_count.columns = ["Studio", "Count"]
        studio_count = studio_count.merge(studio_movies, left_on="Studio", right_on="studios", how="left").drop(columns=["studios"])

        top_10_common_studios = studio_count.head(10).sort_values(by="Count", ascending=True)
        bottom_10_common_studios = studio_count.tail(10)

        liked_movies_df = final_df[final_df["liked"] == True].copy()
        liked_movies_df["studios"] = liked_movies_df["studios"].str.split(", ")
        liked_movies_df = liked_movies_df.explode("studios")
        liked_movies_df = liked_movies_df[~liked_movies_df["studios"].str.contains(r"^Jr\.$", case=False, na=False)]
        liked_movies_df = liked_movies_df[~liked_movies_df["studios"].str.contains("show", case=False, na=False)]
        liked_studios_movies = liked_movies_df.groupby("studios")["title"].apply(list).reset_index(name="Movies")
        studios_counted = liked_movies_df["studios"].value_counts().reset_index()
        studios_counted.columns = ["Studio", "Count"]
        studios_counted = studios_counted.merge(liked_studios_movies, left_on="Studio", right_on="studios", how="left").drop(columns=["studios"])
        top_studios_high_rated = studios_counted.head(10).sort_values(by='Count', ascending=True)

        st.markdown("""
            <style>
            .big-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: -20px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="big-font">Most watched studios:</p>
            """, unsafe_allow_html=True)
        fig1 = create_bar_graph(top_10_common_studios, x="Count", y="Studio", title="Most Watched Film Studios", color="rgb(102, 221, 103)", hover_data=top_10_common_studios["Movies"])
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
            <style>
            .studios-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: -20px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="studios-font">Least watched studios</p>
            """, unsafe_allow_html=True)
        fig2 = create_bar_graph(bottom_10_common_studios, x="Count", y="Studio", title="Least Watched Film Studios", color="rgb(101, 186, 239)", hover_data=bottom_10_common_studios["Movies"])
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
            <style>
            .studios-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: -20px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="studios-font">Top studios from your liked movies:</p>
            """, unsafe_allow_html=True)
        fig3 = create_bar_graph(top_studios_high_rated, x="Count", y="Studio", title="Common Film Studios from Movies you've Liked", color="rgb(239, 135, 51)", hover_data=top_studios_high_rated["Movies"])
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
            <style>
            .studios-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: -70px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="studios-font">Average rating per film studio:</p>
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
            <p class="small-font">(From your 20 most watched film studios)</p>
            """, unsafe_allow_html=True)
        fig4 = studio_with_rating(studio_df)
        create_avg_rating_by_studios_graph_horizontal(fig4, title="Average Rating per Most Watched Film Studios", color="#ff6961")