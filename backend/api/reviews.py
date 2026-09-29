"""Review and theme evidence endpoints."""

from fastapi import APIRouter, HTTPException, Query

from backend.services.store import get_analysis

router = APIRouter(tags=["Reviews"])


def _get(analysis_id: str):
    analysis = get_analysis(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis


@router.get("/reviews/{analysis_id}")
def reviews(
    analysis_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sentiment: str | None = Query(None),
    theme_id: int | None = Query(None),
    search: str | None = Query(None),
):
    analysis = _get(analysis_id)
    df = analysis["df"].copy()
    text_column = analysis["metadata"]["text_column"]

    if sentiment:
        sentiment = sentiment.lower()
        if sentiment not in {"positive", "negative", "neutral"}:
            raise HTTPException(status_code=400, detail="Invalid sentiment filter.")
        df = df[df["sentiment_label"] == sentiment]

    if theme_id is not None:
        df = df[df["theme_id"] == theme_id]

    if search:
        mask = df[text_column].str.contains(search, case=False, na=False)
        df = df[mask]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end].copy()

    columns = [
        "review_id",
        text_column,
        "sentiment_score",
        "sentiment_label",
        "theme_id",
    ]

    if analysis["metadata"]["date_column"] in page_df.columns:
        columns.append(analysis["metadata"]["date_column"])

    page_df = page_df[columns]
    page_df = page_df.rename(columns={text_column: "review_text"})

    records = page_df.to_dict(orient="records")

    for record in records:
        for key, value in list(record.items()):
            if hasattr(value, "isoformat"):
                record[key] = value.isoformat()
            elif hasattr(value, "item"):
                record[key] = value.item()

    return {
        "analysis_id": analysis_id,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
        "reviews": records,
    }


@router.get("/themes/{analysis_id}/{theme_id}")
def theme_details(analysis_id: str, theme_id: int):
    analysis = _get(analysis_id)

    theme = next(
        (item for item in analysis["themes"] if item["theme_id"] == theme_id),
        None,
    )

    if theme is None:
        raise HTTPException(status_code=404, detail="Theme not found.")

    return {
        "analysis_id": analysis_id,
        "theme": theme,
    }
