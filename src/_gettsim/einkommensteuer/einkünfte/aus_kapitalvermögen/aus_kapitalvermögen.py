"""Einkünfte aus Kapitalvermögen."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(end_date="2008-12-31", leaf_name="betrag_y")
def betrag_y_mit_sparerfreibetrag_und_werbungskostenpauschbetrag(
    kapitalerträge_y: float,
    sparerfreibetrag: float,
    sparer_werbungskostenpauschbetrag: float,
) -> float:
    """Calculate taxable capital income on Steuernummer level."""
    return max(
        kapitalerträge_y - sparerfreibetrag + sparer_werbungskostenpauschbetrag,
        0.0,
    )


@policy_function(start_date="2009-01-01", leaf_name="betrag_y")
def betrag_y_mit_sparerpauschbetrag(
    kapitalerträge_y: float,
    sparerpauschbetrag: float,
) -> float:
    """Calculate taxable capital income on Steuernummer level."""
    return max(kapitalerträge_y - sparerpauschbetrag, 0.0)
