"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def privat_versichert() -> bool:
    """Has (only) a private health insurance contract."""


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def beitrag_private_basiskrankenversicherung_abzüglich_arbeitgeberanteil_m() -> float:
    """Monthly contribution to private basic health insurance minus (tax-exempt)
    employer's contribution.
    """
