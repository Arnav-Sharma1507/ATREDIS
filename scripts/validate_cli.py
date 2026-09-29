"""Run: python scripts/validate_cli.py data/labeled_sample.csv"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.validate import validate_against_labels


def main():
    parser = argparse.ArgumentParser(description="Validate sentiment accuracy.")
    parser.add_argument("labeled_csv", help="Path to a CSV with a true_sentiment column")
    parser.add_argument("--text-column", default="review_text")
    parser.add_argument("--label-column", default="true_sentiment")
    args = parser.parse_args()

    result = validate_against_labels(args.labeled_csv, args.text_column, args.label_column)

    print(f"Accuracy: {result['accuracy']:.2%}\n")
    print(json.dumps(result["report"], indent=2))


if __name__ == "__main__":
    main()
