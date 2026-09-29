"""Cluster reviews into themes and keep traceable example verbatims."""

from typing import List, Dict, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def extract_themes(
    df: pd.DataFrame,
    text_column: str = "review_text",
    n_themes: int = 6,
    examples_per_theme: int = 3,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, List[Dict]]:
    """Cluster reviews with TF-IDF + KMeans.

    Returns (df_with_theme_id, list_of_theme_summaries). Each theme
    summary includes real example verbatims so the theme is traceable
    back to actual reviews, not just a keyword label.
    """
    texts = df[text_column].fillna("").astype(str).tolist()
    # Keep row count stable even when a review is blank.
    vector_texts = [text if text.strip() else "empty review" for text in texts]

    vectorizer = TfidfVectorizer(
        max_features=2000, stop_words="english", ngram_range=(1, 2), min_df=1
    )
    try:
        X = vectorizer.fit_transform(vector_texts)
    except ValueError:
        # Extremely small/empty datasets still get one traceable theme.
        df = df.copy()
        df["theme_id"] = 0
        examples = df[text_column].head(examples_per_theme).tolist()
        avg_sentiment = (
            df["sentiment_score"].mean()
            if "sentiment_score" in df.columns
            else None
        )
        return df, [{
            "theme_id": 0,
            "label": "general feedback",
            "keywords": ["general", "feedback"],
            "count": len(df),
            "avg_sentiment": avg_sentiment,
            "examples": examples,
        }]

    n_clusters = max(1, min(n_themes, len(texts)))
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_ids = model.fit_predict(X)

    df = df.copy()
    df["theme_id"] = cluster_ids

    terms = vectorizer.get_feature_names_out()
    themes = []
    for cluster_id in range(n_clusters):
        center = model.cluster_centers_[cluster_id]
        top_term_idx = center.argsort()[::-1][:5]
        top_terms = [terms[i] for i in top_term_idx]

        cluster_df = df[df["theme_id"] == cluster_id]
        examples = cluster_df[text_column].head(examples_per_theme).tolist()
        avg_sentiment = (
            cluster_df["sentiment_score"].mean()
            if "sentiment_score" in cluster_df.columns
            else None
        )

        themes.append(
            {
                "theme_id": cluster_id,
                "label": ", ".join(top_terms[:3]),
                "keywords": top_terms,
                "count": len(cluster_df),
                "avg_sentiment": avg_sentiment,
                "examples": examples,
            }
        )

    return df, themes
