from __future__ import annotations

from gettsim.tt import TTSIMUnit, cast_ttsim_unit, policy_function


@policy_function(
    end_date="1999-03-31",
    leaf_name="neue_entgeltpunkte_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_nach_wohnort_ohne_geringfügige_beschäftigung(
    einnahmen__bruttolohn_y: float,
    wohnort_ost_hh: bool,
    beitrag__versicherungsfrei_wegen_alters: bool,
    beitrag__beitragsbemessungsgrenze_y: float,
    beitragspflichtiges_durchschnittsentgelt_y: float,
    umrechnung_entgeltpunkte_beitrittsgebiet: float,
) -> float:
    """Earnings points for the wages earned in the current year.

    Versicherungsfreiheit wegen Alters rules out earnings points (§ 76b Abs. 4 SGB VI).
    Marginal employment carries no employer contribution yet, so it earns none either.
    """
    # Scale bruttolohn up if earned in eastern Germany
    if wohnort_ost_hh:
        umgerechneter_bruttolohn_y = (
            einnahmen__bruttolohn_y * umrechnung_entgeltpunkte_beitrittsgebiet
        )
    else:
        umgerechneter_bruttolohn_y = einnahmen__bruttolohn_y

    if beitrag__versicherungsfrei_wegen_alters:
        out = 0.0
    else:
        # Both operands are annual rates, so the ratio counts points per year of work.
        out = (
            min(umgerechneter_bruttolohn_y, beitrag__beitragsbemessungsgrenze_y)
            / beitragspflichtiges_durchschnittsentgelt_y
        )

    return cast_ttsim_unit(out, unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR)


@policy_function(
    start_date="1999-04-01",
    end_date="2024-12-31",
    leaf_name="neue_entgeltpunkte_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_nach_wohnort(
    einnahmen__bruttolohn_y: float,
    wohnort_ost_hh: bool,
    sozialversicherung__geringfügig_beschäftigt: bool,
    verzichtet_auf_versicherungsfreiheit_wegen_geringfügiger_beschäftigung: bool,
    beitrag__versicherungsfrei_wegen_alters: bool,
    beitrag__beitragsbemessungsgrenze_y: float,
    beitrag__beitragssatz: float,
    beitrag__minijob_arbeitgeberpauschale: float,
    beitrag__beitragspflichtige_einnahmen_geringfügige_beschäftigung_y: float,
    beitragspflichtiges_durchschnittsentgelt_y: float,
    umrechnung_entgeltpunkte_beitrittsgebiet: float,
) -> float:
    """Earnings points for the wages earned in the current year.

    Versicherungsfreiheit wegen Alters rules out any changes in earnings points, both
    from contributions and as a Zuschlag (§ 76b Abs. 4 SGB VI). A marginally employed
    person without mandatory coverage earns a Zuschlag reflecting the employer's
    Pauschalbeitrag (§ 76b Abs. 1 und 2 SGB VI); the counterfactual Entgelt appears in
    both factors of that product and cancels. With mandatory coverage the
    Mindestbeitragsbemessungsgrundlage applies (§ 163 Abs. 8 SGB VI).
    """
    # Earnings in the Beitrittsgebiet are scaled up before they are compared to the
    # national Durchschnittsentgelt (§ 256a SGB VI).
    if wohnort_ost_hh:
        umrechnungswert = umrechnung_entgeltpunkte_beitrittsgebiet
    else:
        umrechnungswert = 1.0

    if beitrag__versicherungsfrei_wegen_alters:
        out = 0.0
    elif (
        sozialversicherung__geringfügig_beschäftigt
        and not verzichtet_auf_versicherungsfreiheit_wegen_geringfügiger_beschäftigung
    ):
        out = (
            umrechnungswert
            * einnahmen__bruttolohn_y
            * beitrag__minijob_arbeitgeberpauschale
        ) / (beitrag__beitragssatz * beitragspflichtiges_durchschnittsentgelt_y)
    elif sozialversicherung__geringfügig_beschäftigt:
        out = (
            umrechnungswert
            * beitrag__beitragspflichtige_einnahmen_geringfügige_beschäftigung_y
            / beitragspflichtiges_durchschnittsentgelt_y
        )
    else:
        # Both operands are annual rates, so the ratio counts points per year of work.
        out = (
            min(
                umrechnungswert * einnahmen__bruttolohn_y,
                beitrag__beitragsbemessungsgrenze_y,
            )
            / beitragspflichtiges_durchschnittsentgelt_y
        )

    return cast_ttsim_unit(out, unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR)


@policy_function(
    start_date="2025-01-01",
    leaf_name="neue_entgeltpunkte_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_einheitlich(
    einnahmen__bruttolohn_y: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
    verzichtet_auf_versicherungsfreiheit_wegen_geringfügiger_beschäftigung: bool,
    beitrag__versicherungsfrei_wegen_alters: bool,
    beitrag__beitragsbemessungsgrenze_y: float,
    beitrag__beitragssatz: float,
    beitrag__minijob_arbeitgeberpauschale: float,
    beitrag__beitragspflichtige_einnahmen_geringfügige_beschäftigung_y: float,
    beitragspflichtiges_durchschnittsentgelt_y: float,
) -> float:
    """Earning points for the wages earned in this year.

    Versicherungsfreiheit wegen Alters rules out any changes in earnings points, both
    from contributions and as a Zuschlag (§ 76b Abs. 4 SGB VI). A marginally employed
    person without mandatory coverage earns a Zuschlag reflecting the employer's
    Pauschalbeitrag (§ 76b Abs. 1 und 2 SGB VI); the counterfactual Entgelt appears in
    both factors of that product and cancels. With mandatory coverage the
    Mindestbeitragsbemessungsgrundlage applies (§ 163 Abs. 8 SGB VI).
    """
    if beitrag__versicherungsfrei_wegen_alters:
        out = 0.0
    elif (
        sozialversicherung__geringfügig_beschäftigt
        and not verzichtet_auf_versicherungsfreiheit_wegen_geringfügiger_beschäftigung
    ):
        out = (einnahmen__bruttolohn_y * beitrag__minijob_arbeitgeberpauschale) / (
            beitrag__beitragssatz * beitragspflichtiges_durchschnittsentgelt_y
        )
    elif sozialversicherung__geringfügig_beschäftigt:
        out = (
            beitrag__beitragspflichtige_einnahmen_geringfügige_beschäftigung_y
            / beitragspflichtiges_durchschnittsentgelt_y
        )
    else:
        # Both operands are annual rates, so the ratio counts points per year of work.
        out = (
            min(einnahmen__bruttolohn_y, beitrag__beitragsbemessungsgrenze_y)
            / beitragspflichtiges_durchschnittsentgelt_y
        )

    return cast_ttsim_unit(out, unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR)


@policy_function(
    start_date="1992-01-01",
    end_date="2023-06-30",
    leaf_name="rentenwert_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def rentenwert_nach_wohnort(
    wohnort_ost_hh: bool,
    sozialversicherung__rente__parameter_rentenwert_nach_wohnort: dict[str, float],
) -> float:
    """Rentenwert."""
    return (
        sozialversicherung__rente__parameter_rentenwert_nach_wohnort["ost"]
        if wohnort_ost_hh
        else sozialversicherung__rente__parameter_rentenwert_nach_wohnort["west"]
    )
