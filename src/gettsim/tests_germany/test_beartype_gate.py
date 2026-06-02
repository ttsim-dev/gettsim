"""`GETTSIM_BEARTYPE_CLAW=0` must also opt out of ttsim's runtime checking.

GEP 9: the opt-out should restore pre-GEP behaviour for a gettsim user via a
single env var. gettsim's own package claw is gated by `GETTSIM_BEARTYPE_CLAW`,
but the perimeter `@beartype` decorators and the synthesized forwarder live in
ttsim and follow `TTSIM_BEARTYPE_CLAW`. `gettsim/__init__` therefore propagates
`GETTSIM_BEARTYPE_CLAW=0` to `TTSIM_BEARTYPE_CLAW`, without overriding an
explicit value. The propagation runs at import time, so each case uses a fresh
subprocess.
"""

import os
import subprocess
import sys

_PROBE = (
    "import gettsim, os; "  # importing gettsim runs the propagation
    "print(os.environ.get('TTSIM_BEARTYPE_CLAW', '<unset>'))"
)


def _ttsim_value_after_import(
    *,
    gettsim_claw: str | None,
    ttsim_claw: str | None,
) -> str:
    """Report `TTSIM_BEARTYPE_CLAW` after importing gettsim under the given env.

    Args:
        gettsim_claw: Value for `GETTSIM_BEARTYPE_CLAW`, or `None` to unset it.
        ttsim_claw: Value for `TTSIM_BEARTYPE_CLAW`, or `None` to unset it.

    Returns:
        The child process's `TTSIM_BEARTYPE_CLAW` value, or `"<unset>"`.
    """
    drop = {"GETTSIM_BEARTYPE_CLAW", "TTSIM_BEARTYPE_CLAW"}
    env = {key: value for key, value in os.environ.items() if key not in drop}
    if gettsim_claw is not None:
        env["GETTSIM_BEARTYPE_CLAW"] = gettsim_claw
    if ttsim_claw is not None:
        env["TTSIM_BEARTYPE_CLAW"] = ttsim_claw
    proc = subprocess.run(  # noqa: S603
        [sys.executable, "-c", _PROBE],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


def test_opt_out_propagates_to_ttsim() -> None:
    """`GETTSIM_BEARTYPE_CLAW=0` turns ttsim's checking off too."""
    assert _ttsim_value_after_import(gettsim_claw="0", ttsim_claw=None) == "0"


def test_explicit_ttsim_setting_wins() -> None:
    """An explicit `TTSIM_BEARTYPE_CLAW` is not overridden by the propagation."""
    assert _ttsim_value_after_import(gettsim_claw="0", ttsim_claw="1") == "1"


def test_no_propagation_when_gettsim_claw_on() -> None:
    """With gettsim's claw on (default), `TTSIM_BEARTYPE_CLAW` stays untouched."""
    assert _ttsim_value_after_import(gettsim_claw=None, ttsim_claw=None) == "<unset>"
