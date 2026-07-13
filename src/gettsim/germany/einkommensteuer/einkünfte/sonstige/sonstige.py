"""Sonstige Einkünfte according to § 22 EStG."""

from __future__ import annotations

from gettsim.tt import Unit, policy_function


@policy_function(unit=Unit.CURRENCY.PER_YEAR)
def betrag_y(
    rente__steuerpflichtige_einnahmen_y: float,
    alle_weiteren_y: float,
    werbungskostenpauschbetrag: float,
) -> float:
    """Sonstige Einkünfte nach Abzug der Werbungskosten."""
    return max(
        rente__steuerpflichtige_einnahmen_y
        + alle_weiteren_y
        - werbungskostenpauschbetrag,
        0.0,
    )
