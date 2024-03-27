import streamlit as st
import plotly.express as px

def create_bar_graph(data, x, y, title, color="skyblue", hover_data=None, ccs=None):
    def concise_hover_text(movies_list):
        if len(movies_list) <= 5:
            return "<br>".join(movies_list)
        else:
            more_count = len(movies_list) - 5
            displayed_movies = movies_list[:5]
            return "<br>".join(displayed_movies) + f"<br>and {more_count} more..."

    if hover_data is not None:
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

        fig1 = create_bar_graph(top_10_common_studios, x="Count", y="Studio", title="Most Watched Film Studios", color="rgb(102, 221, 103)", hover_data=top_10_common_studios["Movies"])
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

        fig2 = create_bar_graph(bottom_10_common_studios, x="Count", y="Studio", title="Least Watched Film Studios", color="rgb(101, 186, 239)", hover_data=bottom_10_common_studios["Movies"])
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})