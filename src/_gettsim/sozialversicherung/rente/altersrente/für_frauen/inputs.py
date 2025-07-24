"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input(end_date="2017-12-31")
def pflichtsbeitragsjahre_ab_alter_40() -> float:
    """Total years of mandatory contributions after age 40."""
