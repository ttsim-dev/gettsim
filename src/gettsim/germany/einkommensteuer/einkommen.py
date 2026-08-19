"""Einkommen.

Einkommen are Einkünfte minus Sonderausgaben, Vorsorgeaufwendungen, außergewöhnliche
Belastungen and sonstige Abzüge.
"""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def gesamteinkommen_y_sn(
    einkünfte__gesamtbetrag_der_einkünfte_y_sn: float,
    abzüge__betrag_y_sn: float,
) -> float:
    """Gesamteinkommen without Kinderfreibetrag on tax unit level."""
    out = einkünfte__gesamtbetrag_der_einkünfte_y_sn - abzüge__betrag_y_sn

    return max(out, 0.0)
