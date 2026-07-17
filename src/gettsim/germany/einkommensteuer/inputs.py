"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def gemeinsam_veranlagt() -> bool:
    """Taxes are filed jointly."""
