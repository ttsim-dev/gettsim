"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def betriebliche_altersvorsorge_m() -> float:
    """Monthly payout from occupational pension schemes (Betriebsrente)."""


@policy_input()
def aus_berufsständischen_versicherungen_m() -> float:
    """Monthly payout from a berufsständisches Versorgungswerk.

    Benefits from the compulsory public-law pension schemes for liberal professions
    (Ärzte, Apotheker, Rechtsanwälte, Architekten, …) that substitute for the
    gesetzliche Rentenversicherung.
    """


@policy_input()
def geförderte_private_vorsorge_m() -> float:
    """Monthly payout from state-subsidised private pension plans.

    This includes all private pension plans that were subsidised during accumulation via
    §10a EStG and are taxed fully when payout is received (§ 22 Nr. 5 EStG) -- not
    according to the cohort-based Besteuerungsanteil like the gesetzliche Rente or the
    Basisrente. The most prominent example is the Riester-Rente.
    """


@policy_input(start_date="2005-01-01")
def basisrente_m() -> float:
    """Monthly payout from the Basisrente (colloquially Rürup-Rente).

    Contributions to the Basisrente were fully tax-deductible during accumulation
    (Sonderausgabenabzug per § 10 Abs. 1 Nr. 2 Buchst. b EStG). Unlike the income in
    `geförderte_private_vorsorge_m`, the payouts are taxed at the cohort-based
    Besteuerungsanteil that depends on the year of retirement (§ 22 Nr. 1 Satz 3 Buchst.
    a Doppelbuchst. aa EStG).
    """


@policy_input()
def sonstige_private_vorsorge_m() -> float:
    """Monthly payout from private pensions taxed via Ertragsanteil only.

    Private pension plans that were not subsidised during accumulation via §10a EStG and
    are taxed via Ertragsanteil only. Most prominent examples are
    Kapitallebensversicherungen and private pension plans other than the Basisrente and
    the Riester-Rente.
    """
