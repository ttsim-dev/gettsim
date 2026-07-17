"""Unterhalt (child support)."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def kind_festgelegter_zahlbetrag_m(
    anspruch_m: float,
    kindergeld__betrag_m: float,
    familie__volljährig: bool,
    abzugsrate_kindergeld: dict[str, float],
) -> float:
    """Monthly actual child alimony payments to be received by the child after
    deductions.
    """
    if familie__volljährig:
        abzugsrate = abzugsrate_kindergeld["volljährig"]
    else:
        abzugsrate = abzugsrate_kindergeld["minderjährig"]

    return anspruch_m - abzugsrate * kindergeld__betrag_m
