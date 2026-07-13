"""Input columns."""

from __future__ import annotations

from gettsim.tt import Unit, policy_input


@policy_input(unit=Unit.DIMENSIONLESS)
def gemeinsam_veranlagt() -> bool:
    """Taxes are filed jointly."""
