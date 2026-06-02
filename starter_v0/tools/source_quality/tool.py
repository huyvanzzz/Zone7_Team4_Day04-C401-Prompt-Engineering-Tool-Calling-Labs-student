from __future__ import annotations

from typing import Any

from tools._shared import domain, terms


TYPE_WEIGHTS = {
    "official": 35,
    "paper": 32,
    "news": 24,
    "blog": 12,
    "social": 8,
    "unknown": 10,
}

STRONG_DOMAINS = {
    "arxiv.org",
    "openai.com",
    "anthropic.com",
    "deepmind.google",
    "microsoft.com",
    "nature.com",
    "science.org",
    "acm.org",
    "ieee.org",
}


def source_quality(
    url: str = "",
    title: str = "",
    snippet: str = "",
    source_type: str = "unknown",
) -> dict[str, Any]:
    host = domain(url)
    normalized_type = source_type if source_type in TYPE_WEIGHTS else "unknown"
    score = TYPE_WEIGHTS[normalized_type]
    signals: list[str] = [f"type:{normalized_type}"]
    cautions: list[str] = []

    if host in STRONG_DOMAINS or any(host.endswith(f".{item}") for item in STRONG_DOMAINS):
        score += 20
        signals.append("recognized_domain")
    elif host:
        score += 5
        signals.append("has_domain")
    else:
        cautions.append("missing_url_or_domain")

    text_terms = terms(" ".join([title, snippet]))
    if len(text_terms) >= 8:
        score += 15
        signals.append("substantive_snippet")
    elif len(text_terms) >= 3:
        score += 8
        signals.append("limited_snippet")
    else:
        cautions.append("thin_snippet")

    lower_url = url.lower()
    if lower_url.startswith("https://"):
        score += 5
        signals.append("https")
    elif lower_url:
        cautions.append("non_https")

    if normalized_type in {"social", "blog", "unknown"}:
        cautions.append("needs_corroboration")

    score = max(0, min(100, score))
    if score >= 75:
        rating = "strong"
    elif score >= 50:
        rating = "usable"
    elif score >= 30:
        rating = "weak"
    else:
        rating = "poor"

    return {
        "tool": "source_quality",
        "url": url,
        "source": host,
        "source_type": normalized_type,
        "score": score,
        "rating": rating,
        "signals": signals,
        "cautions": cautions,
    }
