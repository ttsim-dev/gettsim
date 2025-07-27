"""Einkünfte according to §§ 13-24 EStG."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(end_date="2008-12-31", leaf_name="gesamtbetrag_der_einkünfte_y")
def gesamtbetrag_der_einkünfte_y_mit_kapiteleinkünften(
    aus_forst_und_landwirtschaft__betrag_y: float,
    aus_gewerbebetrieb__betrag_y: float,
    aus_selbstständiger_arbeit__betrag_y: float,
    aus_nichtselbstständiger_arbeit__betrag_y: float,
    aus_kapitalvermögen__betrag_y: float,
    aus_vermietung_und_verpachtung__betrag_y: float,
    sonstige__betrag_y: float,
) -> float:
    """Gesamtbetrag der Einkünfte (GdE) with capital income."""
    return (
        aus_forst_und_landwirtschaft__betrag_y
        + aus_gewerbebetrieb__betrag_y
        + aus_selbstständiger_arbeit__betrag_y
        + aus_nichtselbstständiger_arbeit__betrag_y
        + aus_kapitalvermögen__betrag_y
        + aus_vermietung_und_verpachtung__betrag_y
        + sonstige__betrag_y
    )


@policy_function(start_date="2009-01-01", leaf_name="gesamtbetrag_der_einkünfte_y")
def gesamtbetrag_der_einkünfte_y_ohne_kapitaleinkünfte(
    aus_forst_und_landwirtschaft__betrag_y: float,
    aus_gewerbebetrieb__betrag_y: float,
    aus_selbstständiger_arbeit__betrag_y: float,
    aus_nichtselbstständiger_arbeit__betrag_y: float,
    aus_vermietung_und_verpachtung__betrag_y: float,
    sonstige__betrag_y: float,
) -> float:
    """Gesamtbetrag der Einkünfte (GdE) without capital income.

    Since 2009 capital income is not subject to normal taxation.
    """
    return (
        aus_forst_und_landwirtschaft__betrag_y
        + aus_gewerbebetrieb__betrag_y
        + aus_selbstständiger_arbeit__betrag_y
        + aus_nichtselbstständiger_arbeit__betrag_y
        + aus_vermietung_und_verpachtung__betrag_y
        + sonstige__betrag_y
    )
