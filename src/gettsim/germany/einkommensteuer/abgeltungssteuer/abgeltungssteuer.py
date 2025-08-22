"""Taxes on capital income (Abgeltungssteuer)."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(start_date="2009-01-01")
def betrag_y_sn(
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn: float, satz: float
) -> float:
    """Abgeltungssteuer on Steuernummer level."""
    return satz * einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn
