"""Dashboard summary endpoint."""

from fastapi import APIRouter, HTTPException

from backend.services.pipeline import make_drift, make_summary
from backend.services.store import get_analysis

router = APIRouter(tags=["Dashboard"])


def _get(analysis_id: str):
    analysis = get_analysis(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis


@router.get("/dashboard/{analysis_id}")
def dashboard(analysis_id: str):
    analysis = _get(analysis_id)
    df = analysis["df"]
    themes = analysis["themes"]
    date_column = analysis["metadata"]["date_column"]

    return {
        "analysis_id": analysis_id,
        "summary": make_summary(df, themes),
        "themes": themes,
        "drift": make_drift(df, date_column),
    }
