"""Taxable income."""

from __future__ import annotations

from gettsim.tt import RoundingSpec, TTSIMUnit, policy_function


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 Satz 5 EStG idF Art. 9 G. v. 29.12.2003 BGBl. I S. 3076",
    ),
    start_date="2004-01-01",
    leaf_name="zu_versteuerndes_einkommen_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def zu_versteuerndes_einkommen_y_sn_mit_abrundungsregel(
    zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn: float,
    gesamteinkommen_y_sn: float,
    kinderfreibetrag_günstiger_sn: bool,
) -> float:
    """Calculate taxable income on Steuernummer level.

    The taxable income is rounded down to a full Euro amount (§ 32a Abs. 1 Satz 3 to 5
    EStG; since 2023 also § 32a Abs. 1 Satz 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I
    S. 2230).

    Reference:
        - § 31 Satz 4 EStG idF Art. 1 G. v. 22.12.1999 BGBl. I S. 2552
        - § 31 Satz 4 EStG idF Art. 1 G. v. 13.12.2006 BGBl. I S. 2878
    """
    if kinderfreibetrag_günstiger_sn:
        out = zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
    else:
        out = gesamteinkommen_y_sn

    return out


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR.PER_SN,
        base=36,
        direction="down",
        to_add_after_rounding=18,
        reference="§ 32a Abs. 2 EStG idF Art. 1 G. v. 19.12.2000 BGBl. I S. 1790",
    ),
    start_date="2002-01-01",
    end_date="2003-12-31",
    leaf_name="zu_versteuerndes_einkommen_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def zu_versteuerndes_einkommen_y_sn_mit_grober_54er_rundungsregel(
    zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn: float,
    gesamteinkommen_y_sn: float,
    kinderfreibetrag_günstiger_sn: bool,
) -> float:
    """Calculate taxable income on Steuernummer level.

    The rounding to multiples of 36 Euro applied up to and including 2003 (§ 52 Abs. 42
    EStG idF Art. 1 G. v. 19.09.2002 BGBl. I S. 3651).

    Reference: § 31 Satz 4 EStG idF Art. 1 G. v. 22.12.1999 BGBl. I S. 2552
    """
    if kinderfreibetrag_günstiger_sn:
        out = zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
    else:
        out = gesamteinkommen_y_sn

    return out


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.DM.PER_YEAR.PER_SN,
        base=54,
        direction="down",
        to_add_after_rounding=27,
        reference="§ 32a Abs. 2 EStG idF B. v. 07.09.1990 BGBl. I S. 1898",
    ),
    end_date="2001-12-31",
    leaf_name="zu_versteuerndes_einkommen_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def zu_versteuerndes_einkommen_y_sn_mit_dmark_rundungsregel(
    zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn: float,
    gesamteinkommen_y_sn: float,
    kinderfreibetrag_günstiger_sn: bool,
) -> float:
    """Calculate taxable income on Steuernummer level.

    Reference:
        - § 2 Abs. 5 EStG idF B. v. 07.09.1990 BGBl. I S. 1898
        - § 31 Satz 4 EStG idF Art. 1 G. v. 11.10.1995 BGBl. I S. 1250
    """
    if kinderfreibetrag_günstiger_sn:
        out = zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
    else:
        out = gesamteinkommen_y_sn

    return out


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn(
    gesamteinkommen_y_sn: float,
    kinderfreibetrag_y_sn: float,
) -> float:
    """Calculate taxable income with child allowance on Steuernummer level.

    Reference: § 2 Abs. 5 Satz 1 EStG idF Art. 1 G. v. 22.12.1999 BGBl. I S. 2552
    """

    out = gesamteinkommen_y_sn - kinderfreibetrag_y_sn
    return max(out, 0.0)
