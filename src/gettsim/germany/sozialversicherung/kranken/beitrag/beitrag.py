"""Public health insurance contributions."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(
    end_date="1999-03-31",
    leaf_name="betrag_versicherter_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_m_bis_03_1999(
    betrag_versicherter_aus_erwerbseinkommen_m: float,
) -> float:
    """Public health insurance contributions paid by the insured person.

    Reference: none (technical helper)
    """
    return betrag_versicherter_aus_erwerbseinkommen_m


@policy_function(
    start_date="1999-04-01",
    leaf_name="betrag_versicherter_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_m_ab_04_1999(
    betrag_versicherter_aus_erwerbseinkommen_m: float,
    betrag_rentner_m: float,
) -> float:
    """Contributions paid by the insured person, including those on pensions.

    Reference: none (technical helper)
    """
    return betrag_versicherter_aus_erwerbseinkommen_m + betrag_rentner_m


@policy_function(
    end_date="1999-03-31",
    leaf_name="betrag_versicherter_aus_erwerbseinkommen_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_aus_erwerbseinkommen_m_bis_03_1999(
    betrag_versicherter_regulärer_beitragssatz_m: float,
) -> float:
    """Contributions on wages and self-employment income paid by the insured person.

    Reference: none (technical helper)
    """
    return betrag_versicherter_regulärer_beitragssatz_m


@policy_function(
    start_date="1999-04-01",
    end_date="2003-03-31",
    leaf_name="betrag_versicherter_aus_erwerbseinkommen_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_aus_erwerbseinkommen_m_ohne_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_selbstständig_m: float,
    betrag_versicherter_regulärer_beitragssatz_m: float,
    einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig: bool,
) -> float:
    """Contributions on wages and self-employment income paid by the insured person.

    Before Midijob introduction in April 2003.

    Reference:
        - § 7 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 7 SGB V idF Art. 3 Nr. 1 G. v. 24.03.1999 BGBl. I S. 388
        - § 250 Abs. 2 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
    """
    if einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig:
        out = betrag_selbstständig_m
    elif sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_versicherter_regulärer_beitragssatz_m

    return out


@policy_function(
    start_date="2003-04-01",
    leaf_name="betrag_versicherter_aus_erwerbseinkommen_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_aus_erwerbseinkommen_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_selbstständig_m: float,
    sozialversicherung__in_gleitzone: bool,
    betrag_versicherter_in_gleitzone_m: float,
    betrag_versicherter_regulärer_beitragssatz_m: float,
    einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig: bool,
) -> float:
    """Contributions on wages and self-employment income paid by the insured person.

    After Midijob introduction in April 2003.

    Reference:
        - § 7 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 250 Abs. 2 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 249 Abs. 4 SGB V idF Art. 3 Nr. 7 G. v. 23.12.2002 BGBl. I S. 4621
        - § 249 Abs. 3 SGB V idF Art. 1 G. v. 21.07.2014 BGBl. I S. 1133
        - § 249 Abs. 3 SGB V idF Art. 8 G. v. 28.06.2022 BGBl. I S. 969
    """
    if einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig:
        out = betrag_selbstständig_m
    elif sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_versicherter_in_gleitzone_m
    else:
        out = betrag_versicherter_regulärer_beitragssatz_m

    return out


@policy_function(
    end_date="1999-03-31",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_bis_03_1999(
    einkommen_m: float,
    einkommensteuer__einkünfte__ist_selbstständig: bool,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Employer's public health insurance contribution.

    Reference: § 249 Abs. 1 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
    """
    if einkommensteuer__einkünfte__ist_selbstständig:
        out = 0.0
    else:
        out = einkommen_m * beitragssatz_arbeitgeber

    return out


@policy_function(
    start_date="1999-04-01",
    end_date="2003-03-31",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_ohne_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    einnahmen__bruttolohn_m: float,
    einkommen_m: float,
    einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig: bool,
    minijob_arbeitgeberpauschale: float,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Employer's public health insurance contribution.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.

    Reference:
        - § 249 Abs. 1 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 249b Satz 1 SGB V idF Art. 3 Nr. 4 G. v. 24.03.1999 BGBl. I S. 388
    """
    if einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig:
        out = 0.0
    elif sozialversicherung__geringfügig_beschäftigt:
        out = einnahmen__bruttolohn_m * minijob_arbeitgeberpauschale
    else:
        out = einkommen_m * beitragssatz_arbeitgeber

    return out


@policy_function(
    start_date="2003-04-01",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__in_gleitzone: bool,
    einnahmen__bruttolohn_m: float,
    betrag_arbeitgeber_in_gleitzone_m: float,
    einkommen_m: float,
    einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig: bool,
    minijob_arbeitgeberpauschale: float,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Employer's public health insurance contribution.

    After Midijob introduction in April 2003.

    Reference:
        - § 249 Abs. 1 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 249b Satz 1 SGB V idF Art. 3 Nr. 8 G. v. 23.12.2002 BGBl. I S. 4621
        - § 249b Satz 1 SGB V idF Art. 10 G. v. 29.06.2006 BGBl. I S. 1402
        - § 249 Abs. 4 SGB V idF Art. 3 Nr. 7 G. v. 23.12.2002 BGBl. I S. 4621
        - § 249 Abs. 3 SGB V idF Art. 1 G. v. 21.07.2014 BGBl. I S. 1133
        - § 249 Abs. 3 SGB V idF Art. 8 G. v. 28.06.2022 BGBl. I S. 969
    """
    if einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig:
        out = 0.0
    elif sozialversicherung__geringfügig_beschäftigt:
        out = einnahmen__bruttolohn_m * minijob_arbeitgeberpauschale
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitgeber_in_gleitzone_m
    else:
        out = einkommen_m * beitragssatz_arbeitgeber

    return out


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_versicherter_regulärer_beitragssatz_m(
    einkommen_m: float,
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Employee's health insurance contributions for regular jobs.

    Reference:
        - § 249 Abs. 1 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 249 Abs. 1 Satz 1 SGB V idF Art. 1 G. v. 26.03.2007 BGBl. I S. 378
        - § 249 Abs. 1 Satz 1 SGB V idF Art. 2 G. v. 26.03.2007 BGBl. I S. 378
        - § 249 Abs. 1 Satz 1 SGB V idF Art. 1 G. v. 22.12.2011 BGBl. I S. 2983
        - § 249 Abs. 1 Satz 1 SGB V idF Art. 1 G. v. 21.07.2014 BGBl. I S. 1133
        - § 249 Abs. 1 Satz 1 SGB V idF Art. 2 G. v. 11.12.2018 BGBl. I S. 2387
    """
    return beitragssatz_arbeitnehmer * einkommen_m


@policy_function(
    end_date="2005-06-30",
    leaf_name="betrag_selbstständig_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_selbstständig_m_mit_einheitlichen_beitragssatz(
    bemessungsgrundlage_selbstständig_m: float,
    beitragssatz: float,
) -> float:
    """Health insurance contributions for self-employed's income. The self-employed
    pay the full reduced contribution.

    Reference: § 250 Abs. 2 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
    """
    return beitragssatz * bemessungsgrundlage_selbstständig_m


@policy_function(
    start_date="2005-07-01",
    end_date="2008-12-31",
    leaf_name="betrag_selbstständig_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_selbstständig_m_ohne_ermäßigtem_beitragssatz(
    bemessungsgrundlage_selbstständig_m: float,
    parameter_beitragssatz: dict[str, float],
) -> float:
    """Health insurance contributions for self-employed's income. The self-employed
    pay the full reduced contribution.

    Reference:
        - § 250 Abs. 2 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 241a Abs. 1 Satz 1 SGB V idF Art. 1 G. v. 15.12.2004 BGBl. I S. 3445
    """
    return (
        parameter_beitragssatz["mean_allgemein"] * bemessungsgrundlage_selbstständig_m
    )


@policy_function(
    start_date="2009-01-01",
    end_date="2014-12-31",
    leaf_name="betrag_selbstständig_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_selbstständig_m_ohne_zusatzbeitrag(
    bemessungsgrundlage_selbstständig_m: float,
    parameter_beitragssatz: dict[str, float],
) -> float:
    """Health insurance contributions for self-employed's income. The self-employed
    pay the full reduced contribution.

    Reference:
        - § 250 Abs. 2 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 243 SGB V idF Art. 2 G. v. 26.03.2007 BGBl. I S. 378
        - § 243 SGB V idF Art. 1 G. v. 22.12.2010 BGBl. I S. 2309
    """
    return parameter_beitragssatz["ermäßigt"] * bemessungsgrundlage_selbstständig_m


@policy_function(
    start_date="2015-01-01",
    leaf_name="betrag_selbstständig_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_selbstständig_m_mit_zusatzbeitrag(
    bemessungsgrundlage_selbstständig_m: float,
    parameter_beitragssatz: dict[str, float],
    zusatzbeitragssatz: float,
) -> float:
    """Health insurance contributions for self-employed's income. The self-employed
    pay the full reduced contribution.

    Contribution rate includes the insurance provider-specific Zusatzbeitrag introduced
    in 2015.

    Reference:
        - § 250 Abs. 2 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 243 SGB V idF Art. 1 G. v. 21.07.2014 BGBl. I S. 1133
        - § 243 SGB V idF Art. 1 G. v. 04.04.2017 BGBl. I S. 778
        - § 242 Abs. 1 SGB V idF Art. 1 G. v. 21.07.2014 BGBl. I S. 1133
    """
    beitrag = parameter_beitragssatz["ermäßigt"] + zusatzbeitragssatz
    return beitrag * bemessungsgrundlage_selbstständig_m


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_rentner_m(
    bemessungsgrundlage_rente_m: float,
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Health insurance contributions for pension incomes.

    Reference:
        - § 249a Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 249a Satz 1 SGB V idF Art. 1 G. v. 26.03.2007 BGBl. I S. 378
        - § 249a Satz 1 SGB V idF Art. 1 G. v. 21.07.2014 BGBl. I S. 1133
    """
    return beitragssatz_arbeitnehmer * bemessungsgrundlage_rente_m


@policy_function(start_date="2003-04-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_gesamt_in_gleitzone_m(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz_arbeitnehmer: float,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Sum of employee and employer health insurance contribution for midijobs.

    Midijobs were introduced in April 2003.

    Reference:
        - § 226 Abs. 4 SGB V idF Art. 3 Nr. 5 G. v. 23.12.2002 BGBl. I S. 4621
        - § 226 Abs. 4 SGB V idF Art. 8 G. v. 28.06.2022 BGBl. I S. 969
    """
    return (
        beitragssatz_arbeitnehmer + beitragssatz_arbeitgeber
    ) * sozialversicherung__midijob_bemessungsentgelt_m


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_arbeitgeber_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_in_gleitzone_m_mit_festem_beitragssatz(
    einnahmen__bruttolohn_m: float,
    sozialversicherung__in_gleitzone: bool,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Employers' health insurance contribution for midijobs until September 2022.

    Midijobs were introduced in April 2003.

    Reference:
        - § 249 Abs. 4 SGB V idF Art. 3 Nr. 7 G. v. 23.12.2002 BGBl. I S. 4621
        - § 249 Abs. 3 SGB V idF Art. 1 G. v. 21.07.2014 BGBl. I S. 1133
    """
    if sozialversicherung__in_gleitzone:
        out = beitragssatz_arbeitgeber * einnahmen__bruttolohn_m
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2022-10-01",
    leaf_name="betrag_arbeitgeber_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_in_gleitzone_m_als_differenz_von_gesamt_und_versichertenbeitrag(
    betrag_gesamt_in_gleitzone_m: float,
    betrag_versicherter_in_gleitzone_m: float,
    sozialversicherung__in_gleitzone: bool,
) -> float:
    """Employer's health insurance contribution for midijobs since October
    2022.

    Reference: § 249 Abs. 3 SGB V idF Art. 8 G. v. 28.06.2022 BGBl. I S. 969
    """
    if sozialversicherung__in_gleitzone:
        out = betrag_gesamt_in_gleitzone_m - betrag_versicherter_in_gleitzone_m
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_versicherter_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_in_gleitzone_m_als_differenz_von_gesamt_und_arbeitgeberbeitrag(
    betrag_gesamt_in_gleitzone_m: float,
    betrag_arbeitgeber_in_gleitzone_m: float,
) -> float:
    """Employee's health insurance contribution for midijobs until September 2022.

    Reference:
        - § 249 Abs. 4 SGB V idF Art. 3 Nr. 7 G. v. 23.12.2002 BGBl. I S. 4621
        - § 249 Abs. 3 SGB V idF Art. 1 G. v. 21.07.2014 BGBl. I S. 1133
    """
    return betrag_gesamt_in_gleitzone_m - betrag_arbeitgeber_in_gleitzone_m


@policy_function(
    start_date="2022-10-01",
    leaf_name="betrag_versicherter_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_in_gleitzone_m_mit_festem_beitragssatz(
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Employee's health insurance contribution for midijobs since October 2022.

    Reference: § 249 Abs. 3 SGB V idF Art. 8 G. v. 28.06.2022 BGBl. I S. 969
    """
    return (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * beitragssatz_arbeitnehmer
    )
