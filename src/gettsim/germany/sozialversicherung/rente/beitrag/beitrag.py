"""Public pension insurance contributions."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(
    end_date="1999-03-31",
    leaf_name="betrag_versicherter_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_m_bis_03_1999(
    versicherungsfrei_wegen_alters: bool,
    betrag_versicherter_regulärer_beitragssatz_m: float,
) -> float:
    """Public pension insurance contributions paid by the insured person."""
    if versicherungsfrei_wegen_alters:
        return 0.0
    else:
        return betrag_versicherter_regulärer_beitragssatz_m


@policy_function(
    start_date="1999-04-01",
    end_date="2003-03-31",
    leaf_name="betrag_versicherter_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_m_ohne_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_versicherter_geringfügige_beschäftigung_m: float,
    versicherungsfrei_wegen_alters: bool,
    betrag_versicherter_regulärer_beitragssatz_m: float,
) -> float:
    """Public pension insurance contributions paid by the insured person.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        return betrag_versicherter_geringfügige_beschäftigung_m
    elif versicherungsfrei_wegen_alters:
        return 0.0
    else:
        return betrag_versicherter_regulärer_beitragssatz_m


@policy_function(
    start_date="2003-04-01",
    leaf_name="betrag_versicherter_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_versicherter_geringfügige_beschäftigung_m: float,
    versicherungsfrei_wegen_alters: bool,
    betrag_in_gleitzone_arbeitnehmer_m: float,
    betrag_versicherter_regulärer_beitragssatz_m: float,
    sozialversicherung__in_gleitzone: bool,
) -> float:
    """Public pension insurance contributions paid by the insured person.

    After Midijob introduction in April 2003.
    """
    # TODO(@MImmesberger): Treatment of individuals that are not insured via the
    # public pension fund (or a berufsständische Rentenversicherung) is wrong.
    # https://github.com/ttsim-dev/gettsim/issues/1114
    if sozialversicherung__geringfügig_beschäftigt:
        return betrag_versicherter_geringfügige_beschäftigung_m
    elif versicherungsfrei_wegen_alters:
        return 0.0
    elif sozialversicherung__in_gleitzone:
        return betrag_in_gleitzone_arbeitnehmer_m
    else:
        return betrag_versicherter_regulärer_beitragssatz_m


@policy_function(
    end_date="2016-12-31",
    leaf_name="versicherungsfrei_wegen_alters",
    unit=TTSIMUnit.DIMENSIONLESS,
)
def versicherungsfrei_wegen_alters_ohne_altersgrenze(
    sozialversicherung__rente__altersrente__betrag_m: float,
) -> bool:
    """Exempt from mandatory pension insurance because an old-age pension is drawn.

    Drawing a Vollrente wegen Alters exempts at any age (§ 5 Abs. 4 Nr. 1 SGB VI).
    """
    return sozialversicherung__rente__altersrente__betrag_m > 0


@policy_function(
    start_date="2017-01-01",
    leaf_name="versicherungsfrei_wegen_alters",
    unit=TTSIMUnit.DIMENSIONLESS,
)
def versicherungsfrei_wegen_alters_mit_altersgrenze(
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
    sozialversicherung__rente__altersrente__betrag_m: float,
    sozialversicherung__rente__verzichtet_auf_versicherungsfreiheit: bool,
) -> bool:
    """Exempt from mandatory pension insurance because of age and an old-age pension.

    The Flexirentengesetz restricted the exemption to Vollrentner past the
    Regelaltersgrenze and allowed them to waive it (§ 5 Abs. 4 Nr. 1 und S. 2 SGB VI).
    """
    return (
        sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze
        and sozialversicherung__rente__altersrente__betrag_m > 0
        and not sozialversicherung__rente__verzichtet_auf_versicherungsfreiheit
    )


@policy_function(start_date="1999-04-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_versicherter_geringfügige_beschäftigung_m(
    sozialversicherung__rente__verzichtet_auf_versicherungsfreiheit: bool,
    beitragspflichtige_einnahmen_geringfügige_beschäftigung_m: float,
    beitragssatz: float,
    einnahmen__bruttolohn_m: float,
    minijob_arbeitgeberpauschale: float,
) -> float:
    """Public pension insurance contributions paid by a marginally employed person.

    Without mandatory coverage the employer's Pauschalbeitrag is the only contribution
    (§ 172 Abs. 3 SGB VI). With it, the employer stays at the Pauschalbeitrag and the
    employee owes the remainder rather than half (§ 168 Abs. 1 Nr. 1b SGB VI).
    """
    if sozialversicherung__rente__verzichtet_auf_versicherungsfreiheit:
        return (
            beitragspflichtige_einnahmen_geringfügige_beschäftigung_m * beitragssatz
            - einnahmen__bruttolohn_m * minijob_arbeitgeberpauschale
        )
    else:
        return 0.0


@policy_function(start_date="1999-04-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def beitragspflichtige_einnahmen_geringfügige_beschäftigung_m(
    einnahmen__bruttolohn_m: float,
    mindestbeitragsbemessungsgrundlage_geringfügige_beschäftigung_m: float,
) -> float:
    """Income subject to pension contributions in marginal employment.

    Reference: § 163 Abs. 8 SGB VI
    """
    return max(
        einnahmen__bruttolohn_m,
        mindestbeitragsbemessungsgrundlage_geringfügige_beschäftigung_m,
    )


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_versicherter_regulärer_beitragssatz_m(
    einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Public pension insurance contributions paid by the insured person."""
    return einkommen_m * beitragssatz / 2


@policy_function(
    end_date="1999-03-31",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_ohne_arbeitgeberpauschale(
    betrag_versicherter_regulärer_beitragssatz_m: float,
) -> float:
    """Employer's public pension insurance contribution.

    Before Minijobs were subject to pension contributions.
    """
    return betrag_versicherter_regulärer_beitragssatz_m


@policy_function(
    start_date="1999-04-01",
    end_date="2003-03-31",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_mit_arbeitgeberpauschale(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_versicherter_regulärer_beitragssatz_m: float,
    einnahmen__bruttolohn_m: float,
    minijob_arbeitgeberpauschale: float,
) -> float:
    """Employer's public pension insurance contribution.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = einnahmen__bruttolohn_m * minijob_arbeitgeberpauschale
    else:
        out = betrag_versicherter_regulärer_beitragssatz_m

    return out


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_in_gleitzone_arbeitgeber_m: float,
    betrag_versicherter_regulärer_beitragssatz_m: float,
    sozialversicherung__in_gleitzone: bool,
    einnahmen__bruttolohn_m: float,
    minijob_arbeitgeberpauschale: float,
) -> float:
    """Employer's public pension insurance contribution.

    After Midijob introduction in April 2003.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = einnahmen__bruttolohn_m * minijob_arbeitgeberpauschale
    elif sozialversicherung__in_gleitzone:
        out = betrag_in_gleitzone_arbeitgeber_m
    else:
        out = betrag_versicherter_regulärer_beitragssatz_m

    return out


@policy_function(
    start_date="2022-10-01",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_mit_midijob_ab_10_2022(
    sozialversicherung__geringfügig_beschäftigt: bool,
    versicherungsfrei_wegen_alters: bool,
    betrag_in_gleitzone_gesamt_m: float,
    betrag_in_gleitzone_arbeitgeber_m: float,
    betrag_versicherter_regulärer_beitragssatz_m: float,
    sozialversicherung__in_gleitzone: bool,
    einnahmen__bruttolohn_m: float,
    minijob_arbeitgeberpauschale: float,
) -> float:
    """Employer's public pension insurance contribution.

    For a versicherungsfreier Beschäftigter the employer owes half of the contribution
    that mandatory coverage would trigger (§ 172 Abs. 1 SGB VI), assessed on the reduced
    beitragspflichtige Einnahme of the Übergangsbereich (§ 20 Abs. 2a Satz 1 SGB IV).
    The asymmetric split of the Übergangsbereich is confined to versicherungspflichtige
    Beschäftigte (§ 168 Abs. 1 Nr. 1d SGB VI). Outside the Übergangsbereich that half is
    the regular employee-rate contribution.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = einnahmen__bruttolohn_m * minijob_arbeitgeberpauschale
    elif versicherungsfrei_wegen_alters and sozialversicherung__in_gleitzone:
        out = betrag_in_gleitzone_gesamt_m / 2
    elif sozialversicherung__in_gleitzone:
        out = betrag_in_gleitzone_arbeitgeber_m
    else:
        out = betrag_versicherter_regulärer_beitragssatz_m

    return out


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def einkommen_m(
    einnahmen__bruttolohn_m: float,
    beitragsbemessungsgrenze_m: float,
) -> float:
    """Wage subject to pension and unemployment insurance contributions."""
    return min(
        einnahmen__bruttolohn_m,
        beitragsbemessungsgrenze_m,
    )


@policy_function(
    start_date="1990-01-01",
    end_date="2024-12-31",
    leaf_name="beitragsbemessungsgrenze_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def beitragsbemessungsgrenze_m_nach_wohnort(
    wohnort_ost_hh: bool,
    parameter_beitragsbemessungsgrenze_nach_wohnort: dict[str, float],
) -> float:
    """Income threshold up to which pension insurance payments apply."""
    return (
        parameter_beitragsbemessungsgrenze_nach_wohnort["ost"]
        if wohnort_ost_hh
        else parameter_beitragsbemessungsgrenze_nach_wohnort["west"]
    )


@policy_function(start_date="2003-04-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_in_gleitzone_gesamt_m(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz: float,
) -> float:
    """Sum of employer and employee pension insurance contribution for midijobs.
    Midijobs were introduced in April 2003.
    """
    return sozialversicherung__midijob_bemessungsentgelt_m * beitragssatz


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_in_gleitzone_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_in_gleitzone_arbeitgeber_m_mit_festem_beitragssatz(
    einnahmen__bruttolohn_m: float,
    beitragssatz: float,
) -> float:
    """Employer's public pension insurance contribution for midijobs until Sep 2022."""
    return einnahmen__bruttolohn_m * beitragssatz / 2


@policy_function(
    start_date="2022-10-01",
    leaf_name="betrag_in_gleitzone_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_in_gleitzone_arbeitgeber_m_als_differenz_von_gesamt_und_arbeitnehmerbeitrag(
    betrag_in_gleitzone_gesamt_m: float,
    betrag_in_gleitzone_arbeitnehmer_m: float,
) -> float:
    """Employer's public pension insurance contribution for midijobs since Oct 2022."""
    return betrag_in_gleitzone_gesamt_m - betrag_in_gleitzone_arbeitnehmer_m


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_in_gleitzone_arbeitnehmer_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_in_gleitzone_arbeitnehmer_m_als_differenz_von_gesamt_und_arbeitgeberbeitrag(
    betrag_in_gleitzone_arbeitgeber_m: float,
    betrag_in_gleitzone_gesamt_m: float,
) -> float:
    """Employee's public pension insurance contribution for midijobs until Sep 2022."""
    return betrag_in_gleitzone_gesamt_m - betrag_in_gleitzone_arbeitgeber_m


@policy_function(
    start_date="2022-10-01",
    leaf_name="betrag_in_gleitzone_arbeitnehmer_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_in_gleitzone_arbeitnehmer_m_mit_festem_beitragssatz(
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    beitragssatz: float,
) -> float:
    """Employee's public pension insurance contribution for midijobs since Oct 2022."""
    return (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * beitragssatz
        / 2
    )
