"""Sonstige Einkünfte according to § 22 EStG."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def betrag_y(
    rente__steuerpflichtige_einnahmen_y: float,
    alle_weiteren_y: float,
    werbungskostenpauschbetrag_y: float,
) -> float:
    """Sonstige Einkünfte nach Abzug der Werbungskosten."""
    return max(
        rente__steuerpflichtige_einnahmen_y
        + alle_weiteren_y
        - werbungskostenpauschbetrag_y,
        0.0,
    )
