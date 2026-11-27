"""Kinderbonus (child bonus)."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(
    start_date="2020-01-01", end_date="2022-12-31", unit=TTSIMUnit.CURRENCY.PER_YEAR
)
def betrag_y(kindergeld__betrag_y: float, satz_y: float) -> float:
    """Calculate Kinderbonus for an individual child.

    (one-time payment, non-allowable against transfer payments)

    Reference:
        - § 66 Abs. 1 Satz 2 EStG idF Art. 1 G. v. 29.06.2020 BGBl. I S. 1512
        - § 66 Abs. 1 Satz 2 EStG idF Art. 1 G. v. 10.03.2021 BGBl. I S. 330
        - § 66 Abs. 1 Satz 2 EStG idF Art. 2 G. v. 23.05.2022 BGBl. I S. 749
    """
    return satz_y if kindergeld__betrag_y > 0 else 0.0
