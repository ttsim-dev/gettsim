"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def sonstige_private_vorsorge_nachgelagert_besteuert_m() -> float:
    """Monthly payout from private pensions taxed as deferred (nachgelagerte Besteuerung).

    Primarily Basisrente / Rürup. Subject to the cohort-based besteuerungsanteil per
    § 22 Nr. 1 Satz 3 Buchst. a Doppelbuchst. aa EStG.
    """


@policy_input()
def sonstige_private_vorsorge_ertragsanteil_besteuert_m() -> float:
    """Monthly payout from private pensions taxed via Ertragsanteil only.

    Private Rentenversicherung and annuitized Kapitallebensversicherung, whose
    contributions were not tax-deductible. Subject to the age-dependent Ertragsanteil
    per § 22 Nr. 1 Satz 3 Buchst. a Doppelbuchst. bb EStG.
    """


@policy_input()
def geförderte_private_vorsorge_m() -> float:
    """Monthly payout from private pensions with tax-favored contributions.

    This refers to pension payments from plans where the original
    contributions were tax-deductible (or tax-exempt). Primarily Riesterrente.
    """


@policy_input()
def betriebliche_altersvorsorge_m() -> float:
    """Monthly payout from occupational pension funds (Betriebsrenten)."""


@policy_input()
def aus_berufsständischen_versicherungen_m() -> float:
    """Monthly payout from professional pension schemes (berufsständische Versicherungen)."""
