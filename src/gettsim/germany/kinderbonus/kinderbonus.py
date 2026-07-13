"""Kinderbonus (child bonus)."""

from __future__ import annotations

from gettsim.tt import Unit, policy_function


@policy_function(
    start_date="2020-01-01", end_date="2021-12-31", unit=Unit.CURRENCY.PER_YEAR
)
def betrag_y(kindergeld__betrag_y: float, satz: float) -> float:
    """Calculate Kinderbonus for an individual child.

    (one-time payment, non-allowable against transfer payments)

    """
    return satz if kindergeld__betrag_y > 0 else 0.0
