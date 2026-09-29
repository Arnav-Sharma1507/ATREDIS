import json
import sqlite3
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "reviewlens.db"


def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_database():
    connection = get_connection()

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            text_column TEXT NOT NULL,
            date_column TEXT,
            n_themes INTEGER NOT NULL,
            total_reviews INTEGER NOT NULL,
            positive_count INTEGER NOT NULL,
            negative_count INTEGER NOT NULL,
            neutral_count INTEGER NOT NULL,
            average_sentiment REAL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT NOT NULL,
            review_id INTEGER NOT NULL,
            review_text TEXT NOT NULL,
            sentiment_score REAL,
            sentiment_label TEXT,
            theme_id INTEGER,
            review_date TEXT,

            FOREIGN KEY (analysis_id)
                REFERENCES analyses(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT NOT NULL,
            theme_id INTEGER NOT NULL,
            label TEXT NOT NULL,
            keywords TEXT,
            review_count INTEGER NOT NULL,
            avg_sentiment REAL,
            examples TEXT,
            frequency_score REAL,
            negativity_score REAL,
            priority_score REAL,
            severity TEXT,
            complaint INTEGER,
            priority_rank INTEGER,

            FOREIGN KEY (analysis_id)
                REFERENCES analyses(id)
                ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_reviews_analysis
        ON reviews(analysis_id);

        CREATE INDEX IF NOT EXISTS idx_reviews_theme
        ON reviews(analysis_id, theme_id);

        CREATE INDEX IF NOT EXISTS idx_themes_analysis
        ON themes(analysis_id);
        """
    )

    connection.commit()
    connection.close()


def save_analysis(
    analysis_id: str,
    df,
    themes: list,
    metadata: dict,
):
    connection = get_connection()

    try:
        counts = df["sentiment_label"].value_counts().to_dict()

        total_reviews = len(df)
        positive_count = int(counts.get("positive", 0))
        negative_count = int(counts.get("negative", 0))
        neutral_count = int(counts.get("neutral", 0))

        average_sentiment = (
            float(df["sentiment_score"].mean())
            if total_reviews
            else 0.0
        )

        from datetime import datetime, timezone

        created_at = datetime.now(timezone.utc).isoformat()

        connection.execute(
            """
            INSERT INTO analyses (
                id,
                filename,
                text_column,
                date_column,
                n_themes,
                total_reviews,
                positive_count,
                negative_count,
                neutral_count,
                average_sentiment,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                analysis_id,
                metadata["filename"],
                metadata["text_column"],
                metadata["date_column"],
                metadata["n_themes"],
                total_reviews,
                positive_count,
                negative_count,
                neutral_count,
                average_sentiment,
                created_at,
            ),
        )

        text_column = metadata["text_column"]
        date_column = metadata["date_column"]

        for _, row in df.iterrows():

            review_date = None

            if date_column in df.columns:
                value = row.get(date_column)

                if value is not None:
                    try:
                        if hasattr(value, "isoformat"):
                            review_date = value.isoformat()
                        else:
                            review_date = str(value)
                    except Exception:
                        review_date = None

            connection.execute(
                """
                INSERT INTO reviews (
                    analysis_id,
                    review_id,
                    review_text,
                    sentiment_score,
                    sentiment_label,
                    theme_id,
                    review_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    int(row["review_id"]),
                    str(row[text_column]),
                    float(row["sentiment_score"]),
                    str(row["sentiment_label"]),
                    int(row["theme_id"]),
                    review_date,
                ),
            )

        for theme in themes:

            connection.execute(
                """
                INSERT INTO themes (
                    analysis_id,
                    theme_id,
                    label,
                    keywords,
                    review_count,
                    avg_sentiment,
                    examples,
                    frequency_score,
                    negativity_score,
                    priority_score,
                    severity,
                    complaint,
                    priority_rank
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    int(theme["theme_id"]),
                    str(theme["label"]),
                    json.dumps(theme.get("keywords", [])),
                    int(theme.get("count", 0)),
                    (
                        float(theme["avg_sentiment"])
                        if theme.get("avg_sentiment") is not None
                        else None
                    ),
                    json.dumps(theme.get("examples", [])),
                    float(theme.get("frequency_score", 0)),
                    float(theme.get("negativity_score", 0)),
                    float(theme.get("priority_score", 0)),
                    str(theme.get("severity", "low")),
                    int(bool(theme.get("complaint", False))),
                    int(theme.get("priority_rank", 0)),
                ),
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_analysis(analysis_id: str):
    connection = get_connection()

    analysis_row = connection.execute(
        """
        SELECT *
        FROM analyses
        WHERE id = ?
        """,
        (analysis_id,),
    ).fetchone()

    if analysis_row is None:
        connection.close()
        return None

    review_rows = connection.execute(
        """
        SELECT *
        FROM reviews
        WHERE analysis_id = ?
        ORDER BY review_id
        """,
        (analysis_id,),
    ).fetchall()

    theme_rows = connection.execute(
        """
        SELECT *
        FROM themes
        WHERE analysis_id = ?
        ORDER BY priority_rank
        """,
        (analysis_id,),
    ).fetchall()

    connection.close()

    return {
        "analysis": dict(analysis_row),
        "reviews": [dict(row) for row in review_rows],
        "themes": [
            {
                **dict(row),
                "keywords": json.loads(row["keywords"] or "[]"),
                "examples": json.loads(row["examples"] or "[]"),
                "complaint": bool(row["complaint"]),
            }
            for row in theme_rows
        ],
    }


def delete_analysis(analysis_id: str) -> bool:
    connection = get_connection()

    cursor = connection.execute(
        """
        DELETE FROM analyses
        WHERE id = ?
        """,
        (analysis_id,),
    )

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted