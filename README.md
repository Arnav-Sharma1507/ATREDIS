# Review Analyzer — "10,000 Reviews, No Time to Read Them"

A tool that ingests a batch of app-store / survey reviews and surfaces the
main themes, common complaints, and overall sentiment through a simple
Streamlit dashboard — no API key required (sentiment runs locally via VADER).

## How it works

1. **Load** — `src/data_loader.py` reads a CSV of reviews into a DataFrame.
2. **Redact** — `src/redact.py` strips emails/phone numbers from the text
   before anything else touches it, so PII never reaches the model or the
   dashboard.
3. **Score sentiment** — `src/sentiment.py` uses VADER (a free, local lexicon-based
   sentiment analyzer — no API key, no internet call) to score each review
   as positive / negative / neutral.
4. **Extract themes** — `src/theming.py` clusters reviews with TF-IDF +
   KMeans, labels each cluster by its top keywords, and keeps a handful of
   **real example verbatims per theme** so every theme is traceable back to
   actual reviews (not just a label).
5. **Validate** — `src/validate.py` (+ `scripts/validate_cli.py`) checks
   sentiment accuracy against a small hand-labelled sample, so you can prove
   the analyzer is actually working before trusting it on 10,000 reviews.
6. **Dashboard** — `app.py` (Streamlit) ties it all together: upload a CSV,
   see sentiment breakdown, expandable themes with verbatims, and (if a date
   column exists) a **drift-over-time** chart showing whether sentiment is
   getting better or worse week over week.

## Project structure

```
review-analyzer/
├── README.md
├── requirements.txt
├── .gitignore
├── app.py                     # Streamlit dashboard (entry point)
├── src/
│   ├── __init__.py
│   ├── data_loader.py         # CSV loading + validation
│   ├── redact.py              # PII redaction (emails, phone numbers)
│   ├── sentiment.py           # VADER sentiment scoring
│   ├── theming.py             # TF-IDF + KMeans theme extraction
│   └── validate.py            # Accuracy check against labelled data
├── scripts/
│   └── validate_cli.py        # CLI wrapper: python scripts/validate_cli.py data/labeled_sample.csv
├── data/
│   ├── sample_reviews.csv     # Small demo dataset to try the app with
│   └── labeled_sample.csv     # Tiny hand-labelled set for validate.py
└── tests/
    └── test_sentiment.py      # Basic pytest sanity checks
```

## Setup

```bash
git clone <your-repo-url>
cd review-analyzer
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
```

## Run the dashboard

```bash
streamlit run app.py
```

Then upload `data/sample_reviews.csv` (or your own CSV with a text column)
in the browser tab that opens.

## Run the accuracy check

```bash
python scripts/validate_cli.py data/labeled_sample.csv
```

This prints overall accuracy plus a per-class precision/recall report,
comparing VADER's labels against the `true_sentiment` column you provide.

## Run tests

```bash
pytest
```

## Notes on the "enterprise-grade" asks

- **Traceable themes** → each theme in `theming.py` carries an `examples`
  list of real review text pulled from that cluster; the dashboard shows
  them under each theme's expander.
- **Validated sentiment** → `validate.py` / `validate_cli.py` scores VADER
  against a labelled sample and reports accuracy — rerun it whenever you
  swap in new data to make sure accuracy hasn't drifted.
- **Redaction** → `redact.py` runs before sentiment/theming, so raw PII
  never gets stored or clustered.
- **Drift over time** → if your CSV has a date column, the dashboard groups
  sentiment by week and plots the trend line.
