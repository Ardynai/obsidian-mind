from .statistics import to_float


def summarize_dose_response(rows, dose_column="dose", response_column="response"):
    points = _dose_response_points(rows, dose_column, response_column)
    if not points:
        return _unavailable_summary(dose_column, response_column)

    responses = [point["response"] for point in points]
    trend_direction = _trend_direction(responses)
    baseline = points[0]
    highest = points[-1]
    delta = _round(highest["response"] - baseline["response"])
    effect_direction = _effect_direction(delta, trend_direction)
    return {
        "schema_version": 1,
        "dose_column": dose_column,
        "response_column": response_column,
        "points": points,
        "point_count": len(points),
        "trend_direction": trend_direction,
        "baseline_dose": baseline["dose"],
        "baseline_response": baseline["response"],
        "highest_dose": highest["dose"],
        "highest_dose_response": highest["response"],
        "baseline_vs_highest_delta": delta,
        "effect_direction": effect_direction,
        "evidence_quality_score": _quality_score(points),
        "preliminary_sandbox_analysis": True,
        "interpretation": _interpretation(trend_direction, delta),
        "limitations": [
            "Preliminary sandbox analysis only.",
            "No curve fitting, statistical inference, clinical claim, or real scientific "
            "conclusion.",
        ],
        "mock": True,
        "offline": True,
        "research_only": True,
    }


def _dose_response_points(rows, dose_column, response_column):
    points = []
    for row in rows:
        dose = to_float(row.get(dose_column))
        response = to_float(row.get(response_column))
        if dose is None or response is None:
            continue
        points.append({"dose": _round(dose), "response": _round(response)})
    return sorted(points, key=lambda point: (point["dose"], point["response"]))


def _trend_direction(responses):
    if len(responses) < 2:
        return "insufficient"
    deltas = [right - left for left, right in zip(responses, responses[1:], strict=False)]
    if all(delta > 0 for delta in deltas):
        return "increasing"
    if all(delta < 0 for delta in deltas):
        return "decreasing"
    if all(delta == 0 for delta in deltas):
        return "flat"
    return "mixed"


def _effect_direction(delta, trend_direction):
    if trend_direction == "mixed":
        return "mixed"
    if delta > 0:
        return "increase"
    if delta < 0:
        return "decrease"
    return "no_change"


def _quality_score(points):
    return round(min(1.0, len(points) / 6), 2)


def _interpretation(trend_direction, delta):
    if trend_direction == "increasing":
        direction = f"response increases by {delta} from baseline to highest dose"
    elif trend_direction == "decreasing":
        direction = f"response decreases by {abs(delta)} from baseline to highest dose"
    elif trend_direction == "flat":
        direction = "response is unchanged across available doses"
    else:
        direction = "response trend is mixed across available doses"
    return (
        f"This preliminary sandbox dose-response summary says {direction}. "
        "It is not curve fitting, medical advice, or a real scientific conclusion."
    )


def _unavailable_summary(dose_column, response_column):
    return {
        "schema_version": 1,
        "dose_column": dose_column,
        "response_column": response_column,
        "points": [],
        "point_count": 0,
        "trend_direction": "unavailable",
        "baseline_dose": None,
        "baseline_response": None,
        "highest_dose": None,
        "highest_dose_response": None,
        "baseline_vs_highest_delta": None,
        "effect_direction": "unavailable",
        "evidence_quality_score": 0.0,
        "preliminary_sandbox_analysis": True,
        "interpretation": (
            "This preliminary sandbox dose-response summary is unavailable because "
            "numeric dose/response columns were not found."
        ),
        "limitations": [
            "Preliminary sandbox analysis only.",
            "No curve fitting, statistical inference, clinical claim, or real scientific "
            "conclusion.",
        ],
        "mock": True,
        "offline": True,
        "research_only": True,
    }


def _round(value):
    rounded = round(float(value), 6)
    if rounded == 0:
        return 0.0
    return rounded
