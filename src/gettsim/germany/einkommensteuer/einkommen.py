"""Einkommen.

Einkommen are Einkünfte minus Sonderausgaben, Vorsorgeaufwendungen, außergewöhnliche
Belastungen and sonstige Abzüge.
"""

from __future__ import annotations

from gettsim.tt import RoundingSpec, TTSIMUnit, policy_function


@policy_function(
    end_date="2001-12-31",
    leaf_name="gesamteinkommen_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def gesamteinkommen_y_sn_bis_2001(
    einkünfte__gesamtbetrag_der_einkünfte_y_sn: float,
    abzüge__betrag_y_sn: float,
) -> float:
    """Gesamteinkommen without Kinderfreibetrag on tax unit level."""
    out = einkünfte__gesamtbetrag_der_einkünfte_y_sn - abzüge__betrag_y_sn

    return max(out, 0.0)


@policy_function(
    start_date="2002-01-01",
    leaf_name="gesamteinkommen_y_sn",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S. 1 EStG",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def gesamteinkommen_y_sn_ab_2002(
    einkünfte__gesamtbetrag_der_einkünfte_y_sn: float,
    abzüge__betrag_y_sn: float,
) -> float:
    """Gesamteinkommen without Kinderfreibetrag on tax unit level."""
    out = einkünfte__gesamtbetrag_der_einkünfte_y_sn - abzüge__betrag_y_sn

    return max(out, 0.0)
