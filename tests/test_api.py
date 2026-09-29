import io

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_sample_csv():
    csv = (
        "review_text,date\n"
        '"Great app and very easy to use",2026-09-01\n'
        '"The app crashes constantly and is terrible",2026-09-02\n'
        '"Support fixed my issue quickly",2026-09-03\n'
        '"Battery drains too fast",2026-09-04\n'
    )

    response = client.post(
        "/api/analyze",
        files={"file": ("reviews.csv", io.BytesIO(csv.encode()), "text/csv")},
        data={"text_column": "review_text", "date_column": "date", "n_themes": "2"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert "analysis_id" in body
    assert body["summary"]["total_reviews"] == 4
    assert len(body["themes"]) == 2

    analysis_id = body["analysis_id"]

    reviews = client.get(f"/api/reviews/{analysis_id}")
    assert reviews.status_code == 200
    assert reviews.json()["total"] == 4

    dashboard = client.get(f"/api/dashboard/{analysis_id}")
    assert dashboard.status_code == 200
    assert "drift" in dashboard.json()


def test_validation_endpoint():
    response = client.get("/api/validation")
    assert response.status_code == 200
    assert "accuracy" in response.json()
