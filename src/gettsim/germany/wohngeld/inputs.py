"""Input columns."""

from __future__ import annotations

from gettsim.tt import Unit, policy_input


@policy_input(unit=Unit.DIMENSIONLESS)
def mietstufe_hh() -> int:
    """Municipality's rent classification."""
