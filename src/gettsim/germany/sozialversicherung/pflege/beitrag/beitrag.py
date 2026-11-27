"""Contributions to public long-term care insurance."""

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
    """Long-term care insurance contributions paid by the insured person.

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
    einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig: bool,
    betrag_selbstständig_m: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_versicherter_regulärer_beitragssatz_m: float,
) -> float:
    """Contributions on wages and self-employment income paid by the insured person.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.

    Reference:
        - § 58 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
        - § 57 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
        - § 7 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 7 SGB V idF Art. 3 Nr. 1 G. v. 24.03.1999 BGBl. I S. 388
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
    einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig: bool,
    betrag_selbstständig_m: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_versicherter_in_gleitzone_m: float,
    betrag_versicherter_regulärer_beitragssatz_m: float,
) -> float:
    """Contributions on wages and self-employment income paid by the insured person.

    Reference:
        - § 58 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
        - § 57 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
        - § 7 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 58 Abs. 5 SGB XI idF Art. 6 G. v. 23.12.2002 BGBl. I S. 4621
        - § 58 Abs. 5 SGB XI idF Art. 10 G. v. 28.06.2022 BGBl. I S. 969
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
    betrag_arbeitgeber_regulärer_beitragssatz_m: float,
) -> float:
    """Long-term care insurance contribution paid by the employer.

    Reference: none (technical helper)
    """
    return betrag_arbeitgeber_regulärer_beitragssatz_m


@policy_function(
    start_date="1999-04-01",
    end_date="2003-03-31",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_ohne_midijob(
    einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig: bool,
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_arbeitgeber_regulärer_beitragssatz_m: float,
) -> float:
    """Long-term care insurance contribution paid by the employer.

    Before Midijob introduction in April 2003.

    Reference:
        - § 58 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
        - § 7 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 7 SGB V idF Art. 3 Nr. 1 G. v. 24.03.1999 BGBl. I S. 388
    """
    if (
        einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig
        or sozialversicherung__geringfügig_beschäftigt
    ):
        out = 0.0
    else:
        out = betrag_arbeitgeber_regulärer_beitragssatz_m

    return out


@policy_function(
    start_date="2003-04-01",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_mit_midijob(
    einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig: bool,
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_arbeitgeber_in_gleitzone_m: float,
    betrag_arbeitgeber_regulärer_beitragssatz_m: float,
) -> float:
    """Long-term care insurance contribution paid by the employer.

    After Midijob introduction in April 2003.

    Reference:
        - § 58 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
        - § 7 Satz 1 SGB V idF Art. 1 G. v. 20.12.1988 BGBl. I S. 2477
        - § 58 Abs. 5 SGB XI idF Art. 6 G. v. 23.12.2002 BGBl. I S. 4621
        - § 58 Abs. 5 SGB XI idF Art. 10 G. v. 28.06.2022 BGBl. I S. 969
    """
    if (
        einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig
        or sozialversicherung__geringfügig_beschäftigt
    ):
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitgeber_in_gleitzone_m
    else:
        out = betrag_arbeitgeber_regulärer_beitragssatz_m

    return out


@policy_function(start_date="1995-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_selbstständig_m(
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbstständig_m: float,
    beitragssatz_arbeitnehmer: float,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Self-employed individuals' long-term care insurance contribution.

    Self-employed pay the full contribution (employer + employee), which is either
    assessed on their self-employement income or 3/4 of the 'Bezugsgröße'

    Reference:
        - § 59 Abs. 4 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
        - § 57 Abs. 4 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
    """
    return sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbstständig_m * (
        beitragssatz_arbeitnehmer + beitragssatz_arbeitgeber
    )


@policy_function(start_date="1995-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_versicherter_regulärer_beitragssatz_m(
    sozialversicherung__kranken__beitrag__einkommen_m: float,
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Long-term care insurance contributions paid by the insured person if regularly
    employed.

    Reference:
        - § 58 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
        - § 58 Abs. 1 Satz 1 SGB XI idF Art. 8 G. v. 26.03.2007 BGBl. I S. 378
        - § 57 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
    """
    return sozialversicherung__kranken__beitrag__einkommen_m * beitragssatz_arbeitnehmer


@policy_function(start_date="1995-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_arbeitgeber_regulärer_beitragssatz_m(
    sozialversicherung__kranken__beitrag__einkommen_m: float,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Long-term care insurance contributions paid by the employer under regular
    employment.

    Reference:
        - § 58 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
        - § 58 Abs. 1 Satz 1 SGB XI idF Art. 8 G. v. 26.03.2007 BGBl. I S. 378
        - § 57 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
    """
    return sozialversicherung__kranken__beitrag__einkommen_m * beitragssatz_arbeitgeber


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_gesamt_in_gleitzone_m(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz_arbeitnehmer: float,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Sum of employee and employer long-term care insurance contributions.

    Reference:
        - § 226 Abs. 4 SGB V idF Art. 3 Nr. 5 G. v. 23.12.2002 BGBl. I S. 4621
        - § 57 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
    """
    return sozialversicherung__midijob_bemessungsentgelt_m * (
        beitragssatz_arbeitnehmer + beitragssatz_arbeitgeber
    )


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_versicherter_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_in_gleitzone_m_als_differenz_von_gesamt_und_arbeitgeberbeitrag(
    betrag_arbeitgeber_in_gleitzone_m: float,
    betrag_gesamt_in_gleitzone_m: float,
) -> float:
    """Employee's long-term care insurance contribution for Midijobs.

    Reference: § 58 Abs. 5 SGB XI idF Art. 6 G. v. 23.12.2002 BGBl. I S. 4621
    """
    return betrag_gesamt_in_gleitzone_m - betrag_arbeitgeber_in_gleitzone_m


@policy_function(
    start_date="2022-10-01",
    end_date="2023-06-30",
    leaf_name="betrag_versicherter_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_in_gleitzone_m_mit_zusatzbetrag_auf_bemessungsentgelt(
    zahlt_zusatzbetrag_kinderlos: bool,
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz_nach_kinderzahl: dict[str, float],
) -> float:
    """Employee's long-term care insurance contribution for Midijobs.

    The employee bears half of the standard contribution rate, assessed on the reduced
    income of § 20 Abs. 2a S. 6 SGB IV. The surcharge for childless individuals raises the
    contribution rate (§ 55 Abs. 3 S. 1 SGB XI), is borne by the employee alone (§ 58
    Abs. 1 S. 3 SGB XI), and is assessed separately on the income subject to
    contributions of § 20 Abs. 2a S. 1 SGB IV.

    Reference:
        - § 58 Abs. 5 SGB XI idF Art. 10 G. v. 28.06.2022 BGBl. I S. 969
        - § 2 Abs. 2 BVV idF Art. 13 G. v. 28.06.2022 BGBl. I S. 969
        - § 58 Abs. 1 Satz 3 SGB XI idF Art. 1 Nr. 3 G. v. 15.12.2004 BGBl. I S. 3448
    """
    base = (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * beitragssatz_nach_kinderzahl["standard"]
        / 2
    )

    zusatzbetrag = (
        sozialversicherung__midijob_bemessungsentgelt_m
        * beitragssatz_nach_kinderzahl["zusatz_kinderlos"]
        if zahlt_zusatzbetrag_kinderlos
        else 0.0
    )

    return base + zusatzbetrag


@policy_function(
    start_date="2023-07-01",
    leaf_name="betrag_versicherter_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_midijob_m_mit_verringertem_beitrag_für_eltern_mit_mehreren_kindern(
    anzahl_kinder_bis_24: int,
    zahlt_zusatzbetrag_kinderlos: bool,
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz_nach_kinderzahl: dict[str, float],
) -> float:
    """Employee's long-term care insurance contribution for Midijobs.

    The employee bears half of the standard contribution rate, assessed on the reduced
    income of § 20 Abs. 2a S. 6 SGB IV. The surcharge for childless individuals raises the
    contribution rate (§ 55 Abs. 3 S. 1 SGB XI), is borne by the employee alone (§ 58
    Abs. 1 S. 3 SGB XI), and is assessed separately on the income subject to
    contributions of § 20 Abs. 2a S. 1 SGB IV. The reduction for parents of more than
    one child below 25 (§ 55 Abs. 3 S. 4 SGB XI) lowers the employee's share only.

    Reference:
        - § 58 Abs. 5 SGB XI idF Art. 10 G. v. 28.06.2022 BGBl. I S. 969
        - § 55 Abs. 3 Satz 4 SGB XI idF Art. 1 G. v. 19.06.2023 BGBl. 2023 I Nr. 155
        - § 58 Abs. 1 Satz 3 SGB XI idF Art. 1 Nr. 3 G. v. 15.12.2004 BGBl. I S. 3448
    """
    base = (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * beitragssatz_nach_kinderzahl["standard"]
        / 2
    )

    add = 0.0
    if zahlt_zusatzbetrag_kinderlos:
        add = (
            add
            + sozialversicherung__midijob_bemessungsentgelt_m
            * beitragssatz_nach_kinderzahl["zusatz_kinderlos"]
        )
    if anzahl_kinder_bis_24 > 1:
        add = add - (
            sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
            * beitragssatz_nach_kinderzahl["abschlag_für_kinder_bis_24"]
            * min(anzahl_kinder_bis_24 - 1, 4)
        )

    return base + add


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_arbeitgeber_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_in_gleitzone_m_als_anteil_des_bruttolohns(
    einnahmen__bruttolohn_m: float,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Employer's long-term care insurance contribution for Midijobs.

    Reference: § 58 Abs. 5 SGB XI idF Art. 6 G. v. 23.12.2002 BGBl. I S. 4621
    """
    return einnahmen__bruttolohn_m * beitragssatz_arbeitgeber


@policy_function(
    start_date="2022-10-01",
    leaf_name="betrag_arbeitgeber_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_in_gleitzone_m_als_anteil_der_beitragspflichtigen_einnahmen(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    beitragssatz_arbeitgeber: float,
    beitragssatz_nach_kinderzahl: dict[str, float],
) -> float:
    """Employer's long-term care insurance contribution for Midijobs.

    The employer bears the total contribution — assessed on the income subject to
    contributions of § 20 Abs. 2a S. 1 SGB IV (§ 226 Abs. 4 SGB V) — less half of the
    standard contribution rate applied to the reduced employee income of § 20 Abs. 2a
    S. 6 SGB IV. Both the surcharge for childless individuals and the reduction for
    parents of more than one child below 25 are left out of that deduction, so neither
    changes the employer's share.

    Reference:
        - § 58 Abs. 5 SGB XI idF Art. 10 G. v. 28.06.2022 BGBl. I S. 969
        - § 2 Abs. 2 BVV idF Art. 13 G. v. 28.06.2022 BGBl. I S. 969
    """
    return (
        sozialversicherung__midijob_bemessungsentgelt_m
        * beitragssatz_nach_kinderzahl["standard"]
        - sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * beitragssatz_arbeitgeber
    )


@policy_function(
    start_date="1995-01-01",
    end_date="2004-03-31",
    leaf_name="betrag_rentner_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_rentner_m_reduzierter_beitrag(
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m: float,
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Long-term care insurance contribution from pension income.

    Pensioners pay the same contribution as employees.

    Reference: § 59 Abs. 1 Satz 1 SGB XI idF Art. 1 G. v. 26.05.1994 BGBl. I S. 1014
    """
    return (
        sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m
        * beitragssatz_arbeitnehmer
    )


@policy_function(
    start_date="2004-04-01",
    end_date="2004-12-31",
    leaf_name="betrag_rentner_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_rentner_m_ohne_zusatz_für_kinderlose(
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m: float,
    beitragssatz: float,
) -> float:
    """Health insurance contribution from pension income.

    Pensioners pay twice the contribution of employees.

    Reference: § 59 Abs. 1 Satz 1 SGB XI idF Art. 6 G. v. 27.12.2003 BGBl. I S. 3013
    """
    return sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m * (
        beitragssatz
    )


@policy_function(
    start_date="2005-01-01",
    leaf_name="betrag_rentner_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_rentner_m_mit_zusatz_für_kinderlose(
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m: float,
    beitragssatz_arbeitnehmer: float,
    beitragssatz_nach_kinderzahl: dict[str, float],
) -> float:
    """Health insurance contribution from pension income.

    Pensioners pay twice the contribution of employees, but only once the additional
    charge for childless individuals.

    Reference:
        - § 59 Abs. 1 Satz 1 SGB XI idF Art. 6 G. v. 27.12.2003 BGBl. I S. 3013
        - § 55 Abs. 3 Satz 1 SGB XI idF Art. 1 Nr. 1 G. v. 15.12.2004 BGBl. I S. 3448
        - § 59 Abs. 5 SGB XI idF Art. 1 Nr. 4 G. v. 15.12.2004 BGBl. I S. 3448
    """
    return sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m * (
        beitragssatz_arbeitnehmer + beitragssatz_nach_kinderzahl["standard"] / 2
    )
