"""Core orchestration contracts for the local Somatic scaffold."""

from somatic.contracts import REQUIRED_WORKFLOW_FIELDS, SUPPORTED_WORKFLOW_MODES


def load_workflow(*args, **kwargs):
    from somatic.workflow_loader import load_workflow as _load_workflow

    return _load_workflow(*args, **kwargs)


def run_mock_workflow(*args, **kwargs):
    from somatic.mock_runtime import run_mock_workflow as _run_mock_workflow

    return _run_mock_workflow(*args, **kwargs)


def write_run_artifacts(*args, **kwargs):
    from somatic.run_writer import write_run_artifacts as _write_run_artifacts

    return _write_run_artifacts(*args, **kwargs)


__all__ = [
    "REQUIRED_WORKFLOW_FIELDS",
    "SUPPORTED_WORKFLOW_MODES",
    "load_workflow",
    "run_mock_workflow",
    "write_run_artifacts",
]
