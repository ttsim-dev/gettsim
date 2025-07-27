"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def privat_versichert() -> bool:
    """Has (only) a private health insurance contract."""
