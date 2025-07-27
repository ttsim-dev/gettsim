"""Kinderbonus (child bonus)."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(start_date="2020-01-01", end_date="2021-12-31")
def betrag_y(kindergeld__betrag_y: float, satz: float) -> float:
    """Calculate Kinderbonus for an individual child.

    (one-time payment, non-allowable against transfer payments)

    """
    if kindergeld__betrag_y > 0:
        out = satz
    else:
        out = 0.0

    return out
