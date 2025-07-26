"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def sonstige_private_vorsorge_m() -> float:
    """Monthly payout from private pensions without tax-favored contributions.

    This refers to pension payments from plans where the original
    contributions were not tax-deductible (or tax-exempt).
    """


@policy_input()
def geförderte_private_vorsorge_m() -> float:
    """Monthly payout from private pensions with tax-favored contributions.

    This refers to pension payments from plans where the original
    contributions were tax-deductible (or tax-exempt). Primarily Riesterrente.
    """


@policy_input()
def betriebliche_altersvorsorge_m() -> float:
    """Amount of monthly occupational pension."""
