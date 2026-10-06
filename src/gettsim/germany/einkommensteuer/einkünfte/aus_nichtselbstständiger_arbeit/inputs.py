"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def tatsächliche_werbungskosten_y() -> float:
    """Actual yearly work-related expenses (Werbungskosten) before comparison with the
    Arbeitnehmer-Pauschbetrag.

    This corresponds to the sum of individually claimed expenses on Anlage N of the
    income tax return (e.g. commuting costs, work equipment, travel expenses).
    """


@policy_input(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def aufstockungsbeträge_altersteilzeit_y() -> float:
    """Tax-exempt Aufstockungsbeträge under the Altersteilzeitgesetz (§ 3 Nr. 28 EStG)."""
