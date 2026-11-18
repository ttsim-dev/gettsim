"""Inputs for sonstige Einkünfte."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def alle_weiteren_y() -> float:
    """Taxable Einnahmen under § 22 EStG not covered by other inputs.

    Tax-free transfers (e.g., BAföG, Kriegsopferfürsorge) do not belong here.
    """
