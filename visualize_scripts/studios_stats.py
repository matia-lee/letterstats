import networkx as nx
import plotly.express as px
from itertools import combinations
import pandas as pd
import matplotlib.pyplot as plt
from community import community_louvain
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st
import numpy as np

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
    # avg_rating_by_studios = avg_rating_by_studios.sort_values('mean_rating', ascending=True)

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

def build_studio_collaboration_network(final_df):
    G = nx.Graph()

    for index, row in final_df.iterrows():
        if pd.notna(row['studios']):
            studios = row['studios'].split(', ')
            for studio_pair in combinations(studios, 2):
                if G.has_edge(*studio_pair):
                    G[studio_pair[0]][studio_pair[1]]['weight'] += 1
                else:
                    G.add_edge(studio_pair[0], studio_pair[1], weight=1)

    return G

def iterative_adjust_positions(pos, min_distance=0.1, max_iterations=100):
    pos_np = np.array(list(pos.values()))
    n = len(pos_np)
    for _ in range(max_iterations):
        adjustments = np.zeros_like(pos_np)
        for i in range(n):
            for j in range(i + 1, n):
                vector = pos_np[j] - pos_np[i]
                distance = np.linalg.norm(vector)
                if distance < min_distance:
                    adjustment = vector * (min_distance - distance) / distance
                    adjustments[i] -= adjustment / 2
                    adjustments[j] += adjustment / 2
        pos_np += adjustments
        if np.linalg.norm(adjustments) < 1e-4: 
            break
    adjusted_pos = {node: pos for node, pos in zip(pos.keys(), pos_np)}
    return adjusted_pos

def visualize_studio_network(G):
    partition = community_louvain.best_partition(G)
    community_colors = {node: partition[node] for node in G.nodes()}
    
    colors = [
        '#b9d9dc', '#a8dadc', '#95d0d3', '#82c5ca', '#6fbac1',
        '#9de2d0', '#b5e4ca', '#cce7c4', '#d7e8bc',
        '#f1d1a9', '#f4b880', '#f79e6d', '#ffb35c', '#ffbf70', '#ffcb85'
    ]
    custom_cmap = LinearSegmentedColormap.from_list("custom_expanded", colors, N=256)
    
    pos = nx.spring_layout(G, k=0.6, iterations=50)

    adjusted_pos = iterative_adjust_positions(pos, min_distance=0.4, max_iterations=100)
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.set_facecolor("#0F1116")
    ax.set_facecolor("#ffffff")
    nx.draw_networkx_nodes(G, adjusted_pos, node_color=list(community_colors.values()), cmap=custom_cmap, alpha=0.8, node_size=[G.degree(node) * 200 for node in G.nodes()])
    nx.draw_networkx_edges(G, adjusted_pos, alpha=0.3, edge_color="#9b9b9b")
    nx.draw_networkx_labels(G, adjusted_pos, font_size=6, font_weight="400", font_color="#ffffff")
    
    plt.title("Studio Collaboration Network", fontsize=16, fontweight="bold", color="#9b9b9b")
    plt.axis('off')
    st.pyplot(plt.gcf())

def prepare_studio_like_data(final_df):
    final_df = final_df.copy()
    final_df['studios'] = final_df['studios'].str.split(", ")
    final_df = final_df.explode('studios')

    studio_stats = final_df.groupby('studios').agg(
        total_movies=('studios', 'size'),
        liked_movies=('liked', lambda x: x.sum())
    ).reset_index()

    studio_stats['liked_percentage'] = ((studio_stats['liked_movies'] / studio_stats['total_movies']) * 100).round(0)

    top_studios = studio_stats.nlargest(15, 'total_movies')

    return top_studios

def plot_studio_liked_percentage(top_studios):
    top_studios = top_studios.sort_values(by='liked_percentage', ascending=False)
    
    fig = px.bar(
        top_studios, 
        x='studios', 
        y='liked_percentage',
        color='liked_percentage',  
        labels={'liked_percentage': '% of Liked Movies', 'studios': 'Studio'},
    )

    fig.update_traces(hovertemplate="%{x}: %{y}%", textposition="outside")
    
    fig.update_layout(
        yaxis_title="% of Liked Movies", 
        xaxis_title="Studios",
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9b9b9b", size=12),
        yaxis=dict(tickfont=dict(size=12, color="#9b9b9b"), titlefont=dict(color="#9b9b9b")),
        xaxis=dict(categoryorder='total descending', tickfont=dict(size=12, color="#9b9b9b"), titlefont=dict(color="#9b9b9b")),
        legend=dict(font=dict(size=12, color="#9b9b9b")),
        title={"text": "Percentage of Liked Movies in Top 15 Most Watched Studios", "y":0.9, "x":0.5, "xanchor": "center", "yanchor": "top", "font": dict(size=20, color="#9b9b9b"), "pad": {"t": -20}},
    )
    
    fig.update_xaxes(tickangle=-45)
    
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
        
        st.markdown("""
        <p style="font-size: 25px; font-weight: 700; margin-bottom: 20px; position: relative; z-index: 1000;">Film Studio's Network in Your Top Rated Movies:</p>
        """, unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size: 15px; margin-top: -10px; z-index: 410; position: absolute;">(Shows film studios that collaborated in your top 10 rated movies. Bigger node size = more connections)</p>
        """, unsafe_allow_html=True)
        top_rated_df = final_df.sort_values(by='rating', ascending=False).head(10)
        top_rated_df['studios'] = top_rated_df['studios'].apply(lambda x: ', '.join(x.split(', ')[:5]) if isinstance(x, str) else x)
        grab_connections = build_studio_collaboration_network(top_rated_df)
        visualize_studio_network(grab_connections)

        st.markdown("""
            <style>
            .percentage-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: -55px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="percentage-font">Percentage of movies you've liked per film studio:</p>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <style>
            .percentage-small-font {
                font-size:15px !important;
                margin-top: 30px !important;
                z-index: 410 !important;
                position: absolute !important;
            }
            </style>
            <p class="percentage-small-font">(From your 15 most watched film studios)</p>
            """, unsafe_allow_html=True)
        fig5 = prepare_studio_like_data(final_df)
        plot_studio_liked_percentage(fig5)