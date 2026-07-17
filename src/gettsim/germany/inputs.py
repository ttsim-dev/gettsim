"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.YEARS)
def alter() -> int:
    """Age in years."""


# TODO(@MImmesberger): Remove once evaluation date is available.
# https://github.com/ttsim-dev/gettsim/issues/211
@policy_input(unit=TTSIMUnit.MONTHS)
def alter_monate() -> int:
    """Age in months."""


@policy_input(unit=TTSIMUnit.HOURS.PER_WEEK)
def arbeitsstunden_w() -> float:
    """Working hours."""


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def behinderungsgrad() -> int:
    pass


@policy_input(unit=TTSIMUnit.CALENDAR_YEAR)
def geburtsjahr() -> int:
    """Birth year."""


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def geburtsmonat() -> int:
    """Month of birth (within year)."""


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def geburtstag() -> int:
    """Day of birth (within month)."""


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def schwerbehindert_grad_g() -> bool:
    pass


@policy_input(unit=TTSIMUnit.CURRENCY)
def vermögen() -> float:
    """Assets for means testing on individual level. {ref}`See this page for more details. <means_testing>`"""


@policy_input(end_date="2017-12-31", unit=TTSIMUnit.DIMENSIONLESS)
def weiblich() -> bool:
    """Female."""


@policy_input(end_date="2024-12-31", unit=TTSIMUnit.DIMENSIONLESS)
def wohnort_ost_hh() -> bool:
    """Whether the household is located in the new Länder (Beitrittsgebiet)."""
