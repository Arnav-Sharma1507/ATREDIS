"""Streamlit dashboard: upload reviews, see sentiment + themes + drift."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_reviews
from src.redact import redact_series
from src.sentiment import analyze_reviews
from src.theming import extract_themes

st.set_page_config(page_title="Review Analyzer", layout="wide")
st.title("10,000 Reviews, No Time to Read Them")
st.caption("Upload a batch of reviews and get themes, complaints, and sentiment in seconds.")

with st.sidebar:
    st.header("Settings")
    text_col = st.text_input("Review text column", value="review_text")
    date_col = st.text_input("Date column (optional)", value="date")
    n_themes = st.slider("Number of themes", 3, 12, 6)

uploaded = st.file_uploader("Upload a CSV of reviews", type="csv")

if uploaded is not None:
    df = load_reviews(uploaded, text_col)
    df[text_col] = redact_series(df[text_col])

    df = analyze_reviews(df, text_col)
    df, themes = extract_themes(df, text_col, n_themes=n_themes)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total reviews", len(df))
    col2.metric("Positive %", f"{(df['sentiment_label'] == 'positive').mean() * 100:.1f}%")
    col3.metric("Negative %", f"{(df['sentiment_label'] == 'negative').mean() * 100:.1f}%")

    st.subheader("Sentiment distribution")
    fig = px.histogram(df, x="sentiment_label", color="sentiment_label")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top themes")
    for theme in sorted(themes, key=lambda t: -t["count"]):
        avg_sent = theme["avg_sentiment"]
        avg_sent_str = f"{avg_sent:.2f}" if avg_sent is not None else "n/a"
        with st.expander(f"{theme['label']}  —  {theme['count']} reviews, avg sentiment {avg_sent_str}"):
            st.write("**Keywords:**", ", ".join(theme["keywords"]))
            st.write("**Example verbatims:**")
            for ex in theme["examples"]:
                st.markdown(f"> {ex}")

    if date_col in df.columns:
        st.subheader("Sentiment drift over time")
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        drift = (
            df.dropna(subset=[date_col])
            .groupby(pd.Grouper(key=date_col, freq="W"))["sentiment_score"]
            .mean()
            .reset_index()
        )
        if not drift.empty:
            fig2 = px.line(drift, x=date_col, y="sentiment_score", title="Weekly average sentiment")
            st.plotly_chart(fig2, use_container_width=True)

    st.download_button(
        "Download analyzed data (CSV)",
        df.to_csv(index=False),
        "analyzed_reviews.csv",
        "text/csv",
    )
else:
    st.info("Upload a CSV to get started, or try `data/sample_reviews.csv` from the repo.")
