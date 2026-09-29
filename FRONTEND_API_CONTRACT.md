# ReviewLens AI — Frontend API Contract

Base URL during local development:

```text
http://127.0.0.1:8000
```

## 1. Upload and analyze

`POST /api/analyze`

Content-Type: `multipart/form-data`

Fields:

- `file`: CSV file
- `text_column`: `review_text`
- `date_column`: `date` (optional; send an empty value if unavailable)
- `n_themes`: `6`

Example response:

```json
{
  "analysis_id": "uuid",
  "filename": "reviews.csv",
  "summary": {
    "total_reviews": 10000,
    "sentiment": {
      "positive": 4200,
      "negative": 3900,
      "neutral": 1900
    },
    "sentiment_percentage": {
      "positive": 42.0,
      "negative": 39.0,
      "neutral": 19.0
    },
    "average_sentiment": -0.04,
    "theme_count": 6,
    "complaint_count": 4,
    "top_complaint": "delivery, delay, order"
  },
  "themes": []
}
```

## 2. Dashboard

`GET /api/dashboard/{analysis_id}`

Returns:

- summary metrics
- prioritized themes
- weekly sentiment drift

## 3. Reviews

`GET /api/reviews/{analysis_id}`

Query parameters:

```text
?page=1&page_size=20
&sentiment=negative
&theme_id=2
&search=delivery
```

## 4. Theme evidence

`GET /api/themes/{analysis_id}/{theme_id}`

The response contains:

- keywords
- count
- average sentiment
- priority rank
- priority score
- severity
- representative review verbatims

## 5. Validation

`GET /api/validation`

Returns VADER accuracy and the classification report for the bundled labelled sample.

## Frontend flow

```text
User selects CSV
       ↓
POST /api/analyze
       ↓
Receive analysis_id
       ↓
GET /api/dashboard/{analysis_id}
       ↓
Render cards/charts/themes
       ↓
GET /api/reviews/{analysis_id}
       ↓
Render searchable review table
```
