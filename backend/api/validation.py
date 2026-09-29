"""Validation and model-quality endpoint."""

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

from src.validate import validate_against_labels

router = APIRouter(tags=["Validation"])


@router.get("/validation")
def validation():
    labeled_file = Path(__file__).resolve().parents[2] / "data" / "labeled_sample.csv"

    if not labeled_file.exists():
        raise HTTPException(status_code=404, detail="Labelled validation sample not found.")

    try:
        result = validate_against_labels(str(labeled_file))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Validation failed: {exc}") from exc

    return {
        "model": "VADER",
        "sample_file": "data/labeled_sample.csv",
        "sample_size": int(len(pd.read_csv(labeled_file))),
        "accuracy": round(float(result["accuracy"]), 4),
        "report": result["report"],
    }
