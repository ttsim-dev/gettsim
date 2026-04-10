"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def tatsächliche_werbungskosten_y() -> float:
    """Actual yearly work-related expenses (Werbungskosten) before comparison with the
    Arbeitnehmer-Pauschbetrag.

    This corresponds to the sum of individually claimed expenses on Anlage N of the
    income tax return (e.g. commuting costs, work equipment, travel expenses).

    Default: 0. When 0, the Arbeitnehmer-Pauschbetrag is used automatically.
    """
