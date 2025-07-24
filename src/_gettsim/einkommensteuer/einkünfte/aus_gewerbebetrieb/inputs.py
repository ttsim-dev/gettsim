"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def betrag_m() -> float:
    """Monthly business income."""
