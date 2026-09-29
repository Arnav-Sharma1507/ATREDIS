import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.sentiment import analyze_reviews

df = pd.read_csv("data/labeled_sample.csv")

result = analyze_reviews(df, "review_text")

print("\nSENTIMENT VALIDATION")
print("=" * 80)

for _, row in result.iterrows():
    correct = row["true_sentiment"] == row["sentiment_label"]

    print(f"\nReview: {row['review_text']}")
    print(f"Actual:    {row['true_sentiment']}")
    print(f"Predicted: {row['sentiment_label']}")
    print(f"Score:     {row['sentiment_score']}")
    print(f"Correct:   {correct}")

accuracy = (
    result["true_sentiment"] == result["sentiment_label"]
).mean()

print("\n" + "=" * 80)
print(f"Accuracy: {accuracy:.2%}")