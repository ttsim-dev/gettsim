"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def bezieht_altersrente() -> bool:
    """Draws an Altersrente.

    Erwerbsminderungsrente is paid irrespective of this input.
    """


@policy_input(end_date="2023-06-30", unit=TTSIMUnit.DIMENSIONLESS)
def entgeltpunkte_ost() -> float:
    """Earnings points for public pension claim accumulated in the new Länder (Beitrittsgebiet)."""


@policy_input(end_date="2023-06-30", unit=TTSIMUnit.DIMENSIONLESS)
def entgeltpunkte_west() -> float:
    """Earnings points for public pension claim accumulated in the old Länder (non-Beitrittsgebiet)."""


@policy_input(start_date="2023-07-01", unit=TTSIMUnit.DIMENSIONLESS)
def entgeltpunkte() -> float:
    """Earnings points for public pension claim."""


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def verzichtet_auf_versicherungsfreiheit() -> bool:
    """Pays employee pension contributions although exempt by default.

    The employment is covered by mandatory pension insurance at the employee's own
    initiative. The legal instrument differs by regime:

    - geringfügige Beschäftigung until 2012-12-31: Verzicht auf die
      Versicherungsfreiheit (§ 5 Abs. 2 S. 2 SGB VI).
    - geringfügige Beschäftigung from 2013-01-01: the negation of the Befreiung von
      der Versicherungspflicht (§ 6 Abs. 1b SGB VI). Minijobs are versicherungspflichtig
      by default here, so `False` means the employee applied for the Befreiung.
    - Beschäftigung nach Erreichen der Regelaltersgrenze from 2017-01-01: Verzicht auf
      die Versicherungsfreiheit (§ 5 Abs. 4 S. 2 SGB VI).
    """


@policy_input(unit=TTSIMUnit.MONTHS)
def ersatzzeiten_monate() -> float:
    """Total months during military, persecution/escape, internment, and consecutive
    sickness.
    """


@policy_input(unit=TTSIMUnit.MONTHS)
def freiwillige_beitragsmonate() -> float:
    """Total months of voluntary pensioninsurance contributions."""


@policy_input(unit=TTSIMUnit.CALENDAR_YEAR)
def jahr_renteneintritt() -> int:
    """Year of pension claiming."""


@policy_input(unit=TTSIMUnit.CALENDAR_MONTH)
def monat_renteneintritt() -> int:
    """Month of retirement."""


@policy_input(unit=TTSIMUnit.MONTHS)
def kinderberücksichtigungszeiten_monate() -> float:
    """Total months of childcare till age 10."""


@policy_input(unit=TTSIMUnit.MONTHS)
def krankheitszeiten_ab_16_bis_24_monate() -> float:
    """Total months of sickness between age 16 and 24."""


@policy_input(unit=TTSIMUnit.MONTHS)
def monate_geringfügiger_beschäftigung() -> float:
    """Total months of marginal employment (w/o mandatory contributions)."""


@policy_input(unit=TTSIMUnit.MONTHS)
def monate_in_arbeitslosigkeit() -> float:
    """Total months of unemployment (registered)."""


@policy_input(unit=TTSIMUnit.MONTHS)
def monate_in_arbeitsunfähigkeit() -> float:
    """Total months of sickness, rehabilitation, measures for worklife
    participation(Teilhabe).
    """


@policy_input(unit=TTSIMUnit.MONTHS)
def monate_in_ausbildungssuche() -> float:
    """Total months of apprenticeship search."""


@policy_input(unit=TTSIMUnit.MONTHS)
def monate_in_mutterschutz() -> float:
    """Total months of maternal protections."""


@policy_input(unit=TTSIMUnit.MONTHS)
def monate_in_schulausbildung() -> float:
    """Months of schooling (incl college, unifrom age 17, max. 8 years)."""


@policy_input(unit=TTSIMUnit.MONTHS)
def monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit() -> float:
    """Total months of unemployment (only time of Entgeltersatzleistungen, not
    ALGII),i.e. Arbeitslosengeld, Unterhaltsgeld, Übergangsgeld.
    """


@policy_input(unit=TTSIMUnit.MONTHS)
def pflichtbeitragsmonate() -> float:
    """Total months of mandatory pension insurance contributions."""


@policy_input(unit=TTSIMUnit.MONTHS)
def pflegeberücksichtigungszeiten_monate() -> float:
    """Total months of home care provision (01.01.1992-31.03.1995)."""
