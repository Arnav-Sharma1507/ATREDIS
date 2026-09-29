"""Persistent SQLite storage for ReviewLens AI."""

import pandas as pd

from backend.database import (
    get_analysis as db_get_analysis,
    save_analysis as db_save_analysis,
    delete_analysis as db_delete_analysis,
)


def save_analysis(
    analysis_id: str,
    df: pd.DataFrame,
    themes: list,
    metadata: dict,
) -> None:
    db_save_analysis(
        analysis_id,
        df,
        themes,
        metadata,
    )


def get_analysis(analysis_id: str):
    data = db_get_analysis(analysis_id)

    if data is None:
        return None

    analysis = data["analysis"]

    metadata = {
        "filename": analysis["filename"],
        "text_column": analysis["text_column"],
        "date_column": analysis["date_column"],
        "n_themes": analysis["n_themes"],
    }

    rows = []

    for review in data["reviews"]:
        row = {
            "review_id": review["review_id"],
            metadata["text_column"]: review["review_text"],
            "sentiment_score": review["sentiment_score"],
            "sentiment_label": review["sentiment_label"],
            "theme_id": review["theme_id"],
        }

        if metadata["date_column"]:
            row[metadata["date_column"]] = review["review_date"]

        rows.append(row)

    df = pd.DataFrame(rows)

    if metadata["date_column"] in df.columns:
        df[metadata["date_column"]] = pd.to_datetime(
            df[metadata["date_column"]],
            errors="coerce",
        )

    return {
        "df": df,
        "themes": data["themes"],
        "metadata": metadata,
    }


def delete_analysis(analysis_id: str) -> bool:
    return db_delete_analysis(analysis_id)