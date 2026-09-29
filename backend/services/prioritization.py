"""Explainable complaint prioritization."""

from typing import List, Dict


def prioritize_themes(themes: List[Dict]) -> List[Dict]:
    """Rank themes using frequency and negative sentiment.

    Priority is intentionally simple and explainable for the hackathon:
    60% frequency + 40% negativity.
    """
    if not themes:
        return themes

    total = sum(theme.get("count", 0) for theme in themes) or 1

    for theme in themes:
        count = theme.get("count", 0)
        avg_sentiment = theme.get("avg_sentiment")
        avg_sentiment = float(avg_sentiment or 0.0)

        frequency_score = count / total
        negativity_score = max(0.0, min(1.0, -avg_sentiment))
        priority_score = 0.6 * frequency_score + 0.4 * negativity_score

        if negativity_score >= 0.50 and frequency_score >= 0.15:
            severity = "high"
        elif negativity_score >= 0.25 or frequency_score >= 0.10:
            severity = "medium"
        else:
            severity = "low"

        theme["frequency_score"] = round(frequency_score, 4)
        theme["negativity_score"] = round(negativity_score, 4)
        theme["priority_score"] = round(priority_score, 4)
        theme["severity"] = severity
        theme["complaint"] = avg_sentiment < -0.05

    themes.sort(key=lambda item: item["priority_score"], reverse=True)

    for rank, theme in enumerate(themes, start=1):
        theme["priority_rank"] = rank

    return themes
