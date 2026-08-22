SCORE_FIELDS = (
    "evidence_alignment",
    "novelty",
    "feasibility",
    "falsifiability",
    "safety_risk",
    "data_requirements",
)

DEFAULT_WEIGHTS = {
    "evidence_alignment": 0.22,
    "novelty": 0.16,
    "feasibility": 0.17,
    "falsifiability": 0.18,
    "safety_risk": 0.12,
    "data_requirements": 0.15,
}


def final_score(scores, weights=None):
    normalized = _normalized_scores(scores)
    active_weights = weights or DEFAULT_WEIGHTS
    total = 0.0
    for field in SCORE_FIELDS:
        value = normalized[field]
        if field == "safety_risk":
            value = 100 - value
        total += value * active_weights[field]
    return round(total, 2)


def rank_scored_items(items):
    scored = []
    for item in items:
        ranked_item = dict(item)
        ranked_item["scores"] = _normalized_scores(item["scores"])
        ranked_item["final_score"] = final_score(ranked_item["scores"])
        scored.append(ranked_item)

    scored.sort(key=lambda item: (-item["final_score"], item["id"]))
    for index, item in enumerate(scored, start=1):
        item["rank"] = index
    return scored


def _normalized_scores(scores):
    missing = [field for field in SCORE_FIELDS if field not in scores]
    if missing:
        raise ValueError(f"Missing score fields: {', '.join(missing)}")

    normalized = {}
    for field in SCORE_FIELDS:
        value = scores[field]
        if not isinstance(value, int):
            raise TypeError(f"Score field {field!r} must be an integer")
        if value < 0 or value > 100:
            raise ValueError(f"Score field {field!r} must be between 0 and 100")
        normalized[field] = value
    return normalized
