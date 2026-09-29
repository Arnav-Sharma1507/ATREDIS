# ReviewLens AI — FastAPI Backend

This backend sits between the frontend and the existing ReviewLens AI NLP pipeline.

## Architecture

Frontend → FastAPI → PII redaction → VADER sentiment → TF-IDF/KMeans themes → complaint prioritization → JSON

## Run

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn backend.main:app --reload
```

API docs:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/api/health

## Main endpoints

### Upload + analyze

`POST /api/analyze`

Multipart form fields:

- `file`: CSV file
- `text_column`: default `review_text`
- `date_column`: default `date`
- `n_themes`: 2–12, default 6

Returns an `analysis_id`, summary metrics, and prioritized themes.

### Dashboard

`GET /api/dashboard/{analysis_id}`

Returns summary, themes, and weekly sentiment drift.

### Reviews

`GET /api/reviews/{analysis_id}?page=1&page_size=20`

Optional filters:

- `sentiment=positive|negative|neutral`
- `theme_id=<id>`
- `search=<text>`

### Theme evidence

`GET /api/themes/{analysis_id}/{theme_id}`

Returns keywords, count, sentiment, priority, severity, and representative verbatims.

### Validation

`GET /api/validation`

Runs VADER against `data/labeled_sample.csv`.

## Frontend integration

Your frontend only needs the API base URL. During local development:

```text
http://127.0.0.1:8000
```

Upload example:

```javascript
const formData = new FormData();
formData.append("file", file);
formData.append("text_column", "review_text");
formData.append("date_column", "date");
formData.append("n_themes", "6");

const response = await fetch("http://127.0.0.1:8000/api/analyze", {
  method: "POST",
  body: formData
});

const result = await response.json();
```

Then use `result.analysis_id` to call the dashboard and review endpoints.

## Storage note

The hackathon MVP stores analysis results in process memory. Restarting the backend clears them. For deployment, replace `backend/services/store.py` with Redis, PostgreSQL, or Azure storage.
