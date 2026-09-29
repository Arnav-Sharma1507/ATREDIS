"""Sentiment scoring using VADER with domain-aware review rules."""

import re
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


_analyzer = SentimentIntensityAnalyzer()


NEGATIVE_PHRASES = [
    "never replies",
    "never reply",
    "no reply",
    "no response",
    "still waiting",
    "way too fast",
    "drains way too fast",
    "drained my battery",
    "very frustrating",
    "extremely slow",
    "very slow",
    "unacceptable",
    "not working",
    "doesn't work",
    "does not work",
    "keeps crashing",
    "crashes every time",
    "waste of time",
]

POSITIVE_PHRASES = [
    "exactly what i wanted",
    "exactly what i need",
    "very helpful",
    "fixed my issue",
    "looks so clean",
    "nice improvement",
    "easy to navigate",
    "simple, fast, and reliable",
]


def score_sentiment(text: str) -> float:
    """Return a VADER compound sentiment score."""
    return _analyzer.polarity_scores(str(text))["compound"]


def label_sentiment(text: str, score: float) -> str:
    """Assign sentiment using VADER plus domain-aware phrase rules."""

    text_lower = str(text).lower()
    normalized = re.sub(r"\s+", " ", text_lower).strip()

    for phrase in NEGATIVE_PHRASES:
        if phrase in normalized:
            return "negative"

    for phrase in POSITIVE_PHRASES:
        if phrase in normalized:
            return "positive"

    if score >= 0.05:
        return "positive"

    if score <= -0.05:
        return "negative"

    return "neutral"


def analyze_reviews(
    df: pd.DataFrame,
    text_column: str = "review_text"
) -> pd.DataFrame:
    """Add sentiment score and sentiment label columns."""

    df = df.copy()

    df["sentiment_score"] = df[text_column].apply(score_sentiment)

    df["sentiment_label"] = df.apply(
        lambda row: label_sentiment(
            row[text_column],
            row["sentiment_score"]
        ),
        axis=1
    )

    return df