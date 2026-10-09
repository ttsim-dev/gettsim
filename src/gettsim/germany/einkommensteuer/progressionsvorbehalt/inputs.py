"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def zurückgezahlte_lohn_und_einkommensersatzleistungen_m() -> float:
    """Repaid benefits under § 32b Abs. 1 S. 1 Nr. 1 EStG.

    Repayments of wage-replacement benefits in the year, for example of Arbeitslosengeld
    or Krankengeld granted for a period in which the entitlement later turned out not to
    exist. They lower the Steuersatzeinkommen from 1996 (§ 32b Abs. 2 EStG).
    """
