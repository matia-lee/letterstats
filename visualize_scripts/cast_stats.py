import streamlit as st
import plotly.express as px

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

def cast_stats(final_df):
    with st.expander("Cast Stats"):
        all_actors = final_df["cast"].str.split(", ").explode()
        all_actors = all_actors[~all_actors.str.contains("show", case=False, na=False)]
        actor_count = all_actors.value_counts().reset_index()
        actor_count.columns = ["Actor", "Count"]

        top_10_common_actors = actor_count.head(10).sort_values(by="Count", ascending=True)

        liked_movies_df = final_df[final_df["liked"] == True]
        high_rated_actors = liked_movies_df["cast"].str.split(", ").explode()
        high_rated_actors = high_rated_actors[~high_rated_actors.str.contains("show", case=False, na=False)]
        high_rated_actors = high_rated_actors.value_counts().reset_index()
        high_rated_actors.columns = ["Actor", "Count"]
        top_actors_high_rated = high_rated_actors.head(10).sort_values(by="Count", ascending=True)

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
            <p class="big-font">Most watched actors:</p>
            """, unsafe_allow_html=True)
        fig1 = create_bar_graph(top_10_common_actors, x="Count", y="Actor", title="Most Watched Actors", color="rgb(102, 221, 103)")
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
            <p class="big-font">Top actors from your liked movies:</p>
            """, unsafe_allow_html=True)
        fig3 = create_bar_graph(top_actors_high_rated, x="Count", y="Actor", title="Common Actors from Movies you've Liked", color="rgb(239, 135, 51)")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

