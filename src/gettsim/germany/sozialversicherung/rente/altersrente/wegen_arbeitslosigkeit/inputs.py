"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input(end_date="2017-12-31")
def arbeitslos_für_1_jahr_nach_alter_58_ein_halb() -> bool:
    """Has been unemployed at least 1 year after age 58.5."""


@policy_input(end_date="2017-12-31")
def pflichtbeitragsjahre_8_von_10() -> bool:
    """Has at least 8 contribution years in past 10 years."""


@policy_input(start_date="1996-07-29", end_date="2009-12-31")
def vertrauensschutz_1997() -> bool:
    """Is covered by Vertrauensschutz rules for the Altersrente wegen Arbeitslosigkeit
    implemented in 1997 (§ 237 SGB VI Abs. 4).
    """


@policy_input(start_date="2004-07-26", end_date="2017-12-31")
def vertrauensschutz_2004() -> bool:
    """Is covered by Vertrauensschutz rules for the Altersrente wegen Arbeitslosigkeit
    enacted in July 2004 (§ 237 SGB VI Abs. 5).
    """
