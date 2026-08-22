"""Process-wide captured output for tests that assert ``somatic doctor`` status."""

import contextlib
import io

from somatic.cli import main


def _capture_doctor() -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(["doctor"])
    return exit_code, stdout.getvalue()


DOCTOR_RESULT = _capture_doctor()
