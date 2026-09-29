"""Analysis endpoint."""

import io
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.services.pipeline import make_summary, run_analysis
from backend.services.store import save_analysis

router = APIRouter(tags=["Analysis"])


@router.post("/analyze")
async def analyze_reviews_api(
    file: UploadFile = File(...),
    text_column: str = Form("review_text"),
    date_column: str = Form("date"),
    n_themes: int = Form(6),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    if not 2 <= n_themes <= 12:
        raise HTTPException(status_code=400, detail="n_themes must be between 2 and 12.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded CSV is empty.")

    try:
        df, themes = run_analysis(
            io.BytesIO(contents),
            text_column=text_column,
            date_column=date_column,
            n_themes=n_themes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    analysis_id = str(uuid.uuid4())
    summary = make_summary(df, themes)

    save_analysis(
        analysis_id,
        df,
        themes,
        {
            "filename": file.filename,
            "text_column": text_column,
            "date_column": date_column,
            "n_themes": n_themes,
        },
    )

    return {
        "analysis_id": analysis_id,
        "filename": file.filename,
        "summary": summary,
        "themes": themes,
        "message": "Analysis completed successfully.",
    }
