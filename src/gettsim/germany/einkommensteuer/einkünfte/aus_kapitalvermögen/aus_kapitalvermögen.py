"""Einkünfte aus Kapitalvermögen."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(
    end_date="2008-12-31",
    leaf_name="betrag_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def betrag_y_sn_mit_sparerfreibetrag_und_werbungskostenpauschbetrag(
    einnahmen__kapitalerträge_y_sn: float,
    familie__anzahl_personen_sn: int,
    sparerfreibetrag_y: float,
    werbungskostenpauschbetrag_y: float,
) -> float:
    """Taxable capital income on Steuernummer level."""
    return max(
        einnahmen__kapitalerträge_y_sn
        - familie__anzahl_personen_sn
        * (sparerfreibetrag_y + werbungskostenpauschbetrag_y),
        0.0,
    )


@policy_function(
    start_date="2009-01-01",
    leaf_name="betrag_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def betrag_y_sn_mit_sparerpauschbetrag(
    einnahmen__kapitalerträge_y_sn: float,
    familie__anzahl_personen_sn: int,
    sparerpauschbetrag_y: float,
) -> float:
    """Taxable capital income on Steuernummer level."""
    return max(
        einnahmen__kapitalerträge_y_sn
        - familie__anzahl_personen_sn * sparerpauschbetrag_y,
        0.0,
    )
