"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def bruttolohn_m() -> float:
    """Income (Einnahmen) from non-self-employment."""


@policy_input(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def kapitalerträge_y() -> float:
    """Income (Einnahmen) from capital income."""


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def zurückgezahlte_lohn_und_einkommensersatzleistungen_m() -> float:
    """Repaid benefits under § 32b Abs. 1 S. 1 Nr. 1 EStG.

    Repayments of wage-replacement benefits, for example of Arbeitslosengeld or
    Krankengeld granted for a period in which the entitlement later turned out not to
    exist. Only the income tax uses them: they lower the Steuersatzeinkommen
    (§ 32b Abs. 2 EStG).
    """
