"""Core ReviewLens AI analysis pipeline."""

from typing import Tuple

import pandas as pd

from src.data_loader import load_reviews
from src.redact import redact_series
from src.sentiment import analyze_reviews
from src.theming import extract_themes
from backend.services.prioritization import prioritize_themes


def run_analysis(
    file_or_buffer,
    text_column: str = "review_text",
    date_column: str = "date",
    n_themes: int = 6,
) -> Tuple[pd.DataFrame, list]:
    """Run ingestion, redaction, sentiment, themes and prioritization."""
    df = load_reviews(file_or_buffer, text_column)

    # PII is removed before sentiment/theme processing.
    df[text_column] = redact_series(df[text_column])

    df = analyze_reviews(df, text_column)
    df, themes = extract_themes(df, text_column, n_themes=n_themes)
    themes = prioritize_themes(themes)

    # Stable review IDs make frontend traceability easy.
    df.insert(0, "review_id", range(1, len(df) + 1))

    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

    return df, themes


def make_summary(df: pd.DataFrame, themes: list) -> dict:
    total = len(df)
    counts = df["sentiment_label"].value_counts().to_dict()

    positive = int(counts.get("positive", 0))
    negative = int(counts.get("negative", 0))
    neutral = int(counts.get("neutral", 0))

    complaints = [theme for theme in themes if theme.get("complaint")]

    return {
        "total_reviews": total,
        "sentiment": {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
        },
        "sentiment_percentage": {
            "positive": round(positive / total * 100, 2) if total else 0,
            "negative": round(negative / total * 100, 2) if total else 0,
            "neutral": round(neutral / total * 100, 2) if total else 0,
        },
        "average_sentiment": round(float(df["sentiment_score"].mean()), 4) if total else 0,
        "theme_count": len(themes),
        "complaint_count": len(complaints),
        "top_complaint": complaints[0]["label"] if complaints else None,
    }


def make_drift(df: pd.DataFrame, date_column: str = "date") -> list:
    if date_column not in df.columns:
        return []

    temp = df.dropna(subset=[date_column]).copy()
    if temp.empty:
        return []

    drift = (
        temp.groupby(pd.Grouper(key=date_column, freq="W"))["sentiment_score"]
        .agg(["mean", "count"])
        .reset_index()
    )

    return [
        {
            "period": row[date_column].strftime("%Y-%m-%d"),
            "average_sentiment": round(float(row["mean"]), 4),
            "review_count": int(row["count"]),
        }
        for _, row in drift.iterrows()
    ]
