"""Load review data from CSV into a pandas DataFrame."""

import pandas as pd


def load_reviews(path_or_buffer, text_column: str = "review_text") -> pd.DataFrame:
    """Read a CSV of reviews and make sure the text column exists.

    ``path_or_buffer`` can be a file path (str) or a file-like object,
    e.g. the object Streamlit's file_uploader returns.
    """
    df = pd.read_csv(path_or_buffer)

    if text_column not in df.columns:
        raise ValueError(
            f"Expected a '{text_column}' column, found: {list(df.columns)}"
        )

    df[text_column] = df[text_column].fillna("").astype(str)
    return df
