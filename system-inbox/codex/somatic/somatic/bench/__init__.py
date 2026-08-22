"""Benchmark lane: sandbox runner plus metadata scaffold."""

from .runner import BenchScore, load_bench_task, run_bench

STATUS = "scaffolded"

__all__ = ["BenchScore", "STATUS", "load_bench_task", "run_bench"]
