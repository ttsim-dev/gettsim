"""Taxes on capital income (Abgeltungssteuer)."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(start_date="2009-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def betrag_y_sn(
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn: float, satz: float
) -> float:
    """Abgeltungssteuer on Steuernummer level.

    Reference: § 32d Abs. 1 Satz 1 EStG idF Art. 1 G. v. 14.08.2007 BGBl. I S. 1912
    """

    return satz * einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn
