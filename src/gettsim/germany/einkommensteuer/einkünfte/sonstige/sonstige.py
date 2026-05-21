"""Sonstige Einkünfte according to § 22 EStG."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def betrag_y(
    einnahmen_y: float,
    werbungskosten_y: float,
) -> float:
    """Sonstige Einkünfte nach Abzug der Werbungskosten."""
    return max(einnahmen_y - werbungskosten_y, 0.0)


@policy_function()
def einnahmen_y(
    alle_weiteren_y: float,
    rente__steuerpflichtige_einnahmen_y: float,
) -> float:
    """Steuerpflichtige Einnahmen aus sonstigen Einkünften i.S.d. § 22 EStG."""
    return alle_weiteren_y + rente__steuerpflichtige_einnahmen_y


@policy_function()
def werbungskosten_y(
    werbungskostenpauschbetrag: float,
) -> float:
    """Werbungskosten für sonstige Einkünfte.

    Reference: § 9a Satz 1 Nr. 3 EStG.
    """
    return werbungskostenpauschbetrag
