import streamlit as st
import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from community import community_louvain
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

def build_actor_network(final_df):
    G = nx.Graph()

    for index, row in final_df.iterrows():
        actors = row['cast'].split(', ')
        for actor_pair in combinations(actors, 2):
            if G.has_edge(*actor_pair):
                G[actor_pair[0]][actor_pair[1]]['weight'] += 1
            else:
                G.add_edge(actor_pair[0], actor_pair[1], weight=1)

    return G

def adjust_positions(pos, G, min_distance=0.1):
    pos_np = np.array(list(pos.values()))
    adjustments = np.zeros(pos_np.shape)
    for i in range(len(pos_np)):
        for j in range(len(pos_np)):
            if i != j:
                vector = pos_np[j] - pos_np[i]
                distance = np.linalg.norm(vector)
                if distance < min_distance:
                    adjustment = vector * (min_distance - distance) / distance
                    adjustments[i] -= adjustment / 2
                    adjustments[j] += adjustment / 2
    adjusted_pos = {node: pos + adjustment for (node, pos), adjustment in zip(pos.items(), adjustments)}
    return adjusted_pos

def visualize_network(G):
    partition = community_louvain.best_partition(G)
    community_colors = {node: partition[node] for node in G.nodes()}
    
    colors = [
        '#b9d9dc', '#a8dadc', '#95d0d3', '#82c5ca', '#6fbac1',
        '#9de2d0', '#b5e4ca', '#cce7c4', '#d7e8bc',
        '#f1d1a9', '#f4b880', '#f79e6d', '#ffb35c', '#ffbf70', '#ffcb85'
    ]
    custom_cmap = LinearSegmentedColormap.from_list("custom_expanded", colors, N=256)
    
    pos = nx.spring_layout(G, k=0.6, iterations=50)
    adjusted_pos = iterative_adjust_positions(pos, min_distance=0.2, max_iterations=100)

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.set_facecolor("#0F1116")
    ax.set_facecolor("#ffffff")
    nx.draw_networkx_nodes(G, adjusted_pos, node_color=list(community_colors.values()), cmap=custom_cmap, alpha=0.8, node_size=[G.degree(node) * 200 for node in G.nodes()])
    nx.draw_networkx_edges(G, adjusted_pos, alpha=0.3, edge_color="#9b9b9b")
    nx.draw_networkx_labels(G, adjusted_pos, font_size=6, font_weight="400", font_color="#ffffff")
    
    plt.title("Actor Network Visualization", fontsize=16, fontweight="bold", color="#9b9b9b")
    plt.axis('off')
    st.pyplot(plt.gcf())

def cast_stats(final_df):
    with st.expander("Cast Stats"):
        cast_df = final_df.copy()
        cast_df["cast"] = cast_df["cast"].str.split(", ")
        cast_df = cast_df.explode("cast")
        cast_df = cast_df[~cast_df["cast"].str.contains(r"^Jr\.$", case=False, na=False)]
        cast_df = cast_df[~cast_df["cast"].str.contains("show", case=False, na=False)]
        cast_movies = cast_df.groupby("cast")["title"].apply(list).reset_index(name="Movies")

        cast_count = cast_df["cast"].value_counts().reset_index()
        cast_count.columns = ["Cast", "Count"]
        cast_count = cast_count.merge(cast_movies, left_on="Cast", right_on="cast", how="left").drop(columns = ["cast"])

        top_10_common_actors = cast_count.head(10).sort_values(by="Count", ascending=True)

        liked_movies_df = cast_df[cast_df["liked"] == True].copy()
        liked_movies_df["cast"] = liked_movies_df["cast"].str.split(", ")
        liked_movies_df = liked_movies_df.explode("cast")
        liked_movies_df = liked_movies_df[~liked_movies_df["cast"].str.contains("show", case=False, na=False)]
        liked_movies_df = liked_movies_df[~liked_movies_df["cast"].str.contains(r'^Jr\.$', case=False, na=False)]
        liked_high_rated_actors = liked_movies_df.groupby("cast")["title"].apply(list).reset_index(name="Movies")
        high_rated_actors_counted = liked_movies_df["cast"].value_counts().reset_index()
        high_rated_actors_counted.columns = ["Cast", "Count"]
        high_rated_actors_counted = high_rated_actors_counted.merge(liked_high_rated_actors, left_on="Cast", right_on="cast", how="left").drop(columns=["cast"])
        top_actors_high_rated = high_rated_actors_counted.head(10).sort_values(by="Count", ascending=True)

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
        fig1 = create_bar_graph(top_10_common_actors, x="Count", y="Cast", title="Most Watched Actors", color="rgb(102, 221, 103)", hover_data=top_10_common_actors["Movies"])
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
        fig3 = create_bar_graph(top_actors_high_rated, x="Count", y="Cast", title="Common Actors from Movies you've Liked", color="rgb(239, 135, 51)",  hover_data=top_actors_high_rated["Movies"])
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
            <style>
            .special-font {
                font-size:25px !important;
                font-weight: 700 !important;
                margin-bottom: 20px !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            <p class="special-font">Actor Network in Your Top Rated Movies:</p>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <style>
            .speciall-font {
                font-size:15px !important;
                margin-top: -10px !important;
                z-index: 410 !important;
                position: absolute !important;
            }
            </style>
            <p class="speciall-font">(Shows actors that have acted together in your top 10 rated movies. Bigger node size = more connections)</p>
            """, unsafe_allow_html=True)
        top_rated_df = final_df.sort_values(by='rating', ascending=False).head(10)
        top_rated_df['cast'] = top_rated_df['cast'].apply(lambda x: ', '.join(x.split(', ')[:5]))
        grab_connections = build_actor_network(top_rated_df)
        visualize_network(grab_connections)

