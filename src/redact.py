"""Lightweight PII redaction for review text.

Regex-based, so it's not perfect, but it strips the most common
identifiers (emails, phone numbers) before text is stored or clustered.
"""

import re

EMAIL_RE = re.compile(r"[\w\.\-+]+@[\w\-]+\.[\w\.\-]+")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\d{3}[\s.-]?){2}\d{4}\b")


def redact_pii(text: str) -> str:
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    return text


def redact_series(series):
    return series.apply(redact_pii)
