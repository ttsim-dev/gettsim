"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def bezieht_rente() -> bool:
    """Draws public pension benefits."""


@policy_input(end_date="2023-06-30")
def entgeltpunkte_ost() -> float:
    """Earnings points for public pension claim accumulated in the new Länder (Beitrittsgebiet)."""


@policy_input(end_date="2023-06-30")
def entgeltpunkte_west() -> float:
    """Earnings points for public pension claim accumulated in the old Länder (non-Beitrittsgebiet)."""


@policy_input(start_date="2023-07-01")
def entgeltpunkte() -> float:
    """Earnings points for public pension claim."""


@policy_input()
def ersatzzeiten_monate() -> float:
    """Total months during military, persecution/escape, internment, and consecutive
    sickness.
    """


@policy_input()
def freiwillige_beitragsmonate() -> float:
    """Total months of voluntary pensioninsurance contributions."""


@policy_input()
def jahr_renteneintritt() -> int:
    """Year of pension claiming."""


@policy_input()
def monat_renteneintritt() -> int:
    """Month of retirement."""


@policy_input()
def kinderberücksichtigungszeiten_monate() -> float:
    """Total months of childcare till age 10."""


@policy_input()
def krankheitszeiten_ab_16_bis_24_monate() -> float:
    """Total months of sickness between age 16 and 24."""


@policy_input()
def monate_geringfügiger_beschäftigung() -> float:
    """Total months of marginal employment (w/o mandatory contributions)."""


@policy_input()
def monate_in_arbeitslosigkeit() -> float:
    """Total months of unemployment (registered)."""


@policy_input()
def monate_in_arbeitsunfähigkeit() -> float:
    """Total months of sickness, rehabilitation, measures for worklife
    participation(Teilhabe).
    """


@policy_input()
def monate_in_ausbildungssuche() -> float:
    """Total months of apprenticeship search."""


@policy_input()
def monate_in_mutterschutz() -> float:
    """Total months of maternal protections."""


@policy_input()
def monate_in_schulausbildung() -> float:
    """Months of schooling (incl college, unifrom age 17, max. 8 years)."""


@policy_input()
def monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit() -> float:
    """Total months of unemployment (only time of Entgeltersatzleistungen, not
    ALGII),i.e. Arbeitslosengeld, Unterhaltsgeld, Übergangsgeld.
    """


@policy_input()
def pflichtbeitragsmonate() -> float:
    """Total months of mandatory pension insurance contributions."""


@policy_input()
def pflegeberücksichtigungszeiten_monate() -> float:
    """Total months of home care provision (01.01.1992-31.03.1995)."""
