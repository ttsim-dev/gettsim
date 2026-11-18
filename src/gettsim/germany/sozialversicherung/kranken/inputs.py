"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def krankengeld_m() -> float:
    """Krankengeld received from the statutory health insurance.

    Excludes private Krankentagegeld.
    """


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def mutterschaftsgeld_m() -> float:
    """Mutterschaftsgeld paid by the health insurance (§ 24i SGB V).

    Excludes the employer's Zuschuss zum Mutterschaftsgeld (§ 20 MuSchG), which is not
    implemented.
    """
