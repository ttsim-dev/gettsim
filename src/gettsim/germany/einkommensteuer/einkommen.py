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
    """Gesamteinkommen without Kinderfreibetrag on tax unit level.

    Reference: § 2 Abs. 4 EStG idF B. v. 07.09.1990 BGBl. I S. 1898
    """
    out = einkünfte__gesamtbetrag_der_einkünfte_y_sn - abzüge__betrag_y_sn

    return max(out, 0.0)


@policy_function(
    start_date="2002-01-01",
    leaf_name="gesamteinkommen_y_sn",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="down",
        reference="§ 32a Abs. 2 EStG idF Art. 1 G. v. 19.12.2000 BGBl. I S. 1790",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def gesamteinkommen_y_sn_ab_2002(
    einkünfte__gesamtbetrag_der_einkünfte_y_sn: float,
    abzüge__betrag_y_sn: float,
) -> float:
    """Gesamteinkommen without Kinderfreibetrag on tax unit level.

    Rounded down to a full Euro amount. In 2002 and 2003, the tariff applied to the
    taxable income rounded to full Euro amounts divisible by 36 (§ 32a Abs. 2 EStG);
    from 2004, to the taxable income rounded to a full Euro amount (§ 32a Abs. 1 Satz 5
    EStG idF Art. 9 G. v. 29.12.2003 BGBl. I S. 3076).

    Reference: § 2 Abs. 4 EStG idF B. v. 16.04.1997 BGBl. I S. 821
    """
    out = einkünfte__gesamtbetrag_der_einkünfte_y_sn - abzüge__betrag_y_sn

    return max(out, 0.0)
