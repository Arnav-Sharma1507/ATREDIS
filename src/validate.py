"""Check sentiment accuracy against a small hand-labelled sample."""

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

from .sentiment import analyze_reviews


def validate_against_labels(
    labeled_csv: str,
    text_column: str = "review_text",
    label_column: str = "true_sentiment",
) -> dict:
    df = pd.read_csv(labeled_csv)
    df = analyze_reviews(df, text_column)

    y_true = df[label_column]
    y_pred = df["sentiment_label"]

    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
    }
