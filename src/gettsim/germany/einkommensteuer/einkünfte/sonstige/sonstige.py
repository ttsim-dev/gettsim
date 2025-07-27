"""Sonstige Einkünfte according to § 22 EStG."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def betrag_y(
    alle_weiteren_y: float,
    rente__betrag_y: float,
) -> float:
    """Total sonstige Einkünfte."""
    return alle_weiteren_y + rente__betrag_y
