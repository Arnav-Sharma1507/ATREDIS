import pandas as pd
from src.sentiment import score_sentiment, label_sentiment, analyze_reviews
from src.redact import redact_pii


def test_positive_scores_higher_than_negative():
    pos = score_sentiment("I absolutely love this app, it's fantastic!")
    neg = score_sentiment("This app is terrible and crashes constantly.")
    assert pos > neg


def test_label_thresholds():
    assert label_sentiment(0.5) == "positive"
    assert label_sentiment(-0.5) == "negative"
    assert label_sentiment(0.0) == "neutral"


def test_analyze_reviews_adds_columns():
    df = pd.DataFrame({"review_text": ["Great app!", "Worst app ever."]})
    result = analyze_reviews(df)
    assert "sentiment_score" in result.columns
    assert "sentiment_label" in result.columns


def test_redact_pii_strips_email_and_phone():
    text = "Contact me at john.doe@example.com or 987-654-3210."
    redacted = redact_pii(text)
    assert "example.com" not in redacted
    assert "987-654-3210" not in redacted
    assert "[EMAIL]" in redacted
    assert "[PHONE]" in redacted
