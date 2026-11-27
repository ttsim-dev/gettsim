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
    """Taxable capital income on Steuernummer level.

    Reference:
        - § 20 Abs. 4 Satz 1 EStG idF Art. 1 G. v. 19.12.2000 BGBl. I S. 1790
        - § 9a Satz 1 Nr. 2 EStG idF Art. 1 G. v. 19.12.2000 BGBl. I S. 1790
    """
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
    """Taxable capital income on Steuernummer level.

    Reference: § 20 Abs. 9 Satz 1 EStG idF Art. 1 G. v. 14.08.2007 BGBl. I S. 1912
    """
    return max(
        einnahmen__kapitalerträge_y_sn
        - familie__anzahl_personen_sn * sparerpauschbetrag_y,
        0.0,
    )
