"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def alter() -> int:
    """Age in years."""


# TODO(@MImmesberger): Remove once evaluation date is available.
# https://github.com/ttsim-dev/gettsim/issues/211
@policy_input()
def alter_monate() -> int:
    """Age in months."""


@policy_input()
def arbeitsstunden_w() -> float:
    """Working hours."""


@policy_input()
def behinderungsgrad() -> int:
    pass


@policy_input()
def geburtsjahr() -> int:
    """Birth year."""


@policy_input()
def geburtsmonat() -> int:
    """Month of birth (within year)."""


@policy_input()
def geburtstag() -> int:
    """Day of birth (within month)."""


@policy_input()
def schwerbehindert_grad_g() -> bool:
    pass


@policy_input()
def vermögen() -> float:
    """Assets for means testing on individual level. {ref}`See this page for more details. <means_testing>`"""


@policy_input(end_date="2017-12-31")
def weiblich() -> bool:
    """Female."""


@policy_input(end_date="2024-12-31")
def wohnort_ost_hh() -> bool:
    """Whether the household is located in the new Länder (Beitrittsgebiet)."""
