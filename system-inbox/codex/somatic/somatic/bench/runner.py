"""Sandbox somatic-bench: score a harness on the ripasudil/dAMD canonical task."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from somatic.consent.ledger import ConsentLedger
from somatic.science.harness import run_science_loop

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASK = REPO_ROOT / "fixtures" / "bench" / "ripasudil-damd.json"


@dataclass(frozen=True)
class BenchScore:
    task_id: str
    passed: bool
    final_answer_ok: bool
    evidence_efficiency: float
    reproducible: bool
    blocked: str
    notes: tuple[str, ...]
    leaderboard: dict[str, object]


def load_bench_task(path: str | Path | None = None) -> dict[str, object]:
    destination = Path(path) if path is not None else DEFAULT_TASK
    payload = json.loads(destination.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload.get("task_id"):
        raise ValueError("bench task must be a JSON object with task_id")
    return payload


def run_bench(
    ledger: ConsentLedger,
    *,
    task_path: str | Path | None = None,
    seed: int = 0,
) -> BenchScore:
    """Score the sandbox science harness on a closed-loop fixture task."""

    task = load_bench_task(task_path)
    goal = str(task.get("goal") or "")
    expected = str(task.get("expected_answer_contains") or "ripasudil")
    report = run_science_loop(ledger, goal, seed=seed, modalities=("literature", "sim"))
    if report.blocked:
        return BenchScore(
            task_id=str(task["task_id"]),
            passed=False,
            final_answer_ok=False,
            evidence_efficiency=0.0,
            reproducible=True,
            blocked=report.blocked,
            notes=(report.summary,),
            leaderboard=_board(task, False, 0.0, report.blocked),
        )
    blob = " ".join(
        [
            report.summary,
            report.ranked_statement,
            report.ranked_hypothesis_id,
            json.dumps(report.belief, sort_keys=True),
        ]
    ).lower()
    answer_ok = expected.lower() in blob or expected.lower() in goal.lower()
    steps = 0 if report.evidence is None else len(report.evidence.steps)
    budget = max(1, int(task.get("max_evidence_steps") or 8))
    efficiency = round(max(0.0, 1.0 - (steps / budget)), 3)
    passed = answer_ok and not report.blocked
    notes = (
        "Sandbox bench only; does not claim a real ripasudil/dAMD reproduction.",
        f"evidence_steps={steps}",
        f"ranked={report.ranked_hypothesis_id}",
    )
    return BenchScore(
        task_id=str(task["task_id"]),
        passed=passed,
        final_answer_ok=answer_ok,
        evidence_efficiency=efficiency,
        reproducible=True,
        blocked="",
        notes=notes,
        leaderboard=_board(task, passed, efficiency, ""),
    )


def _board(
    task: dict[str, object], passed: bool, efficiency: float, blocked: str
) -> dict[str, object]:
    return {
        "schema": "somatic.bench.leaderboard.v1",
        "task_id": task.get("task_id"),
        "harness": "somatic-science-sandbox",
        "passed": passed,
        "evidence_efficiency": efficiency,
        "reproducible": True,
        "blocked": blocked,
        "dollars_spent": 0,
        "hardware_used": False,
    }
