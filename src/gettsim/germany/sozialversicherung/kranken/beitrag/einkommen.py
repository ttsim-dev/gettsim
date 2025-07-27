"""Income relevant for public health insurance contributions."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(end_date="1999-03-31", leaf_name="einkommen_m")
def einkommen_m_bis_03_1999(
    einkommen_bis_beitragsbemessungsgrenze_m: float,
) -> float:
    """Wage subject to public health insurance contributions."""
    return einkommen_bis_beitragsbemessungsgrenze_m


@policy_function(start_date="1999-04-01", leaf_name="einkommen_m")
def einkommen_m_ab_04_1999(
    einkommen_bis_beitragsbemessungsgrenze_m: float,
    sozialversicherung__regulär_beschäftigt: bool,
) -> float:
    """Wage subject to public health insurance contributions.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.
    """
    if sozialversicherung__regulär_beschäftigt:
        out = einkommen_bis_beitragsbemessungsgrenze_m
    else:
        out = 0.0
    return out


@policy_function()
def einkommen_bis_beitragsbemessungsgrenze_m(
    einnahmen__bruttolohn_m: float,
    beitragsbemessungsgrenze_m: float,
) -> float:
    """Income from dependent employment, capped at the contribution ceiling.

    This does not consider reduced contributions for Mini- and Midijobs. Relevant for
    the computation of payroll taxes.
    """
    return min(
        einnahmen__bruttolohn_m,
        beitragsbemessungsgrenze_m,
    )


@policy_function(start_date="1990-01-01")
def bemessungsgrundlage_selbstständig_m(
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    bezugsgröße_selbstständige_m: float,
    einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig: bool,
    privat_versichert: bool,
    beitragsbemessungsgrenze_m: float,
    mindestanteil_bezugsgröße_selbstständige: float,
) -> float:
    """Self-employed income which is subject to health insurance contributions.

    The value is bounded from below and from above. Only affects those self-employed who
    voluntarily contribute to the public health system.

    Reference: §240 SGB V Abs. 4
    """
    # Calculate if self employed insures via public health insurance.
    if (
        einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig
        and not privat_versichert
    ):
        out = min(
            beitragsbemessungsgrenze_m,
            max(
                bezugsgröße_selbstständige_m * mindestanteil_bezugsgröße_selbstständige,
                einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m,
            ),
        )
    else:
        out = 0.0

    return out


@policy_function(
    start_date="1990-01-01",
    end_date="2000-12-31",
    leaf_name="beitragsbemessungsgrenze_m",
)
def beitragsbemessungsgrenze_m_nach_wohnort(
    wohnort_ost_hh: bool,
    parameter_beitragsbemessungsgrenze_nach_wohnort: dict[str, float],
) -> float:
    """Income threshold up to which health insurance payments apply."""
    return (
        parameter_beitragsbemessungsgrenze_nach_wohnort["ost"]
        if wohnort_ost_hh
        else parameter_beitragsbemessungsgrenze_nach_wohnort["west"]
    )


@policy_function(start_date="1990-01-01", end_date="2024-12-31")
def bezugsgröße_selbstständige_m(
    wohnort_ost_hh: bool,
    bezugsgröße_selbstständige_nach_wohnort: dict[str, float],
) -> float:
    """Threshold for self employment income subject to health insurance.

    Selecting by place of living the income threshold for self employed up to which the
    rate of health insurance contributions apply.
    """
    return (
        bezugsgröße_selbstständige_nach_wohnort["ost"]
        if wohnort_ost_hh
        else bezugsgröße_selbstständige_nach_wohnort["west"]
    )


@policy_function()
def bemessungsgrundlage_rente_m(
    einnahmen__renten__gesetzliche_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
    beitragsbemessungsgrenze_m: float,
) -> float:
    """Pension income which is subject to health insurance contribution."""
    return min(
        einnahmen__renten__gesetzliche_m
        + einnahmen__renten__betriebliche_altersvorsorge_m,
        beitragsbemessungsgrenze_m,
    )
