"""Sonstige Einkünfte according to § 22 EStG."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def betrag_m(
    alle_weiteren_m: float,
    rente__betrag_m: float,
) -> float:
    """Total sonstige Einkünfte."""
    return alle_weiteren_m + rente__betrag_m
