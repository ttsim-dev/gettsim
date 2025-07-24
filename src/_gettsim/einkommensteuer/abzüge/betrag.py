"""Tax allowances."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def betrag_y_sn(
    sonderausgaben_y_sn: float,
    vorsorgeaufwendungen_y_sn: float,
    betrag_ind_y_sn: float,
) -> float:
    """Calculate total allowances on Steuernummer level."""
    return sonderausgaben_y_sn + vorsorgeaufwendungen_y_sn + betrag_ind_y_sn


@policy_function()
def betrag_ind_y(
    pauschbetrag_behinderung_y: float,
    alleinerziehend_betrag_y: float,
    altersfreibetrag_y: float,
) -> float:
    """Sum up all tax-deductible allowances applicable at the individual level."""
    return pauschbetrag_behinderung_y + alleinerziehend_betrag_y + altersfreibetrag_y
