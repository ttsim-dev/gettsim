from __future__ import annotations

from ttsim.time_converters import per_m_to_per_y

from gettsim.tt import TTSIMUnit, cast_ttsim_unit, policy_function


@policy_function(
    end_date="1998-07-31",
    leaf_name="neue_entgeltpunkte_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_ohne_arbeitslosengeld(
    neue_entgeltpunkte_aus_beschäftigung_y: float,
) -> float:
    """Earnings points earned in the current year."""
    # TODO(@MImmesberger): Arbeitslosengeld is not modelled before August 1998, so this
    # function does not include earnings points from drawing it.
    # https://github.com/ttsim-dev/gettsim/issues/1253
    return neue_entgeltpunkte_aus_beschäftigung_y


@policy_function(
    start_date="1998-08-01",
    leaf_name="neue_entgeltpunkte_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_mit_arbeitslosengeld(
    neue_entgeltpunkte_aus_beschäftigung_y: float,
    neue_entgeltpunkte_aus_arbeitslosengeld_y: float,
) -> float:
    """Earnings points earned in the current year."""
    return (
        neue_entgeltpunkte_aus_beschäftigung_y
        + neue_entgeltpunkte_aus_arbeitslosengeld_y
    )


@policy_function(
    end_date="1989-12-31",
    leaf_name="neue_entgeltpunkte_aus_beschäftigung_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_aus_beschäftigung_bis_1989(
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
    if wohnort_ost_hh:
        umrechnungswert = umrechnung_entgeltpunkte_beitrittsgebiet
    else:
        umrechnungswert = 1.0

    if beitrag__versicherungsfrei_wegen_alters:
        out = 0.0
    else:
        # Both operands are annual rates, so the ratio counts points per year of work.
        out = (
            umrechnungswert
            * min(einnahmen__bruttolohn_y, beitrag__beitragsbemessungsgrenze_y)
            / beitragspflichtiges_durchschnittsentgelt_y
        )

    return cast_ttsim_unit(out, unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR)


@policy_function(
    start_date="1990-01-01",
    end_date="1999-03-31",
    leaf_name="neue_entgeltpunkte_aus_beschäftigung_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_aus_beschäftigung_nach_wohnort_ohne_geringfügige_beschäftigung(
    einnahmen__bruttolohn_y: float,
    wohnort_ost_hh: bool,
    beitrag__versicherungsfrei_wegen_alters: bool,
    beitrag__beitragsbemessungsgrenze_y: float,
    beitrag__parameter_beitragsbemessungsgrenze_nach_wohnort: dict[str, float],
    beitragspflichtiges_durchschnittsentgelt_y: float,
    umrechnung_entgeltpunkte_beitrittsgebiet: float,
) -> float:
    """Earnings points for the wages earned in the current year.

    Versicherungsfreiheit wegen Alters rules out earnings points (§ 76b Abs. 4 SGB VI).
    Marginal employment carries no employer contribution yet, so it earns none either.

    Wages in the Beitrittsgebiet count up to the Beitragsbemessungsgrenze (Ost), are
    scaled up by Anlage 10, and the result is capped at the Beitragsbemessungsgrenze
    (West) (§ 256a Abs. 1, § 260 Satz 2 SGB VI).
    """
    if wohnort_ost_hh:
        umrechnungswert = umrechnung_entgeltpunkte_beitrittsgebiet
    else:
        umrechnungswert = 1.0

    if beitrag__versicherungsfrei_wegen_alters:
        out = 0.0
    else:
        out = (
            min(
                umrechnungswert
                * min(einnahmen__bruttolohn_y, beitrag__beitragsbemessungsgrenze_y),
                per_m_to_per_y(
                    beitrag__parameter_beitragsbemessungsgrenze_nach_wohnort["west"]
                ),
            )
            / beitragspflichtiges_durchschnittsentgelt_y
        )

    return cast_ttsim_unit(out, unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR)


@policy_function(
    start_date="1999-04-01",
    end_date="2024-12-31",
    leaf_name="neue_entgeltpunkte_aus_beschäftigung_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_aus_beschäftigung_nach_wohnort(
    einnahmen__bruttolohn_y: float,
    wohnort_ost_hh: bool,
    sozialversicherung__geringfügig_beschäftigt: bool,
    verzichtet_auf_versicherungsfreiheit_wegen_geringfügiger_beschäftigung: bool,
    beitrag__versicherungsfrei_wegen_alters: bool,
    beitrag__beitragsbemessungsgrenze_y: float,
    beitrag__parameter_beitragsbemessungsgrenze_nach_wohnort: dict[str, float],
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

    Wages in the Beitrittsgebiet count up to the Beitragsbemessungsgrenze (Ost), are
    scaled up by Anlage 10, and the result is capped at the Beitragsbemessungsgrenze
    (West) (§ 256a Abs. 1, § 260 Satz 2 SGB VI).
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
                umrechnungswert
                * min(einnahmen__bruttolohn_y, beitrag__beitragsbemessungsgrenze_y),
                per_m_to_per_y(
                    beitrag__parameter_beitragsbemessungsgrenze_nach_wohnort["west"]
                ),
            )
            / beitragspflichtiges_durchschnittsentgelt_y
        )

    return cast_ttsim_unit(out, unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR)


@policy_function(
    start_date="2025-01-01",
    leaf_name="neue_entgeltpunkte_aus_beschäftigung_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_aus_beschäftigung_einheitlich(
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
    end_date="1998-07-31",
    leaf_name="neue_entgeltpunkte_aus_arbeitslosengeld_y",
    fail_msg_if_included="Arbeitslosengeld before August 1998 is not implemented.",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_aus_arbeitslosengeld_bis_1998_07() -> float:
    """Earnings points for drawing Arbeitslosengeld in the current year."""


@policy_function(
    start_date="1998-08-01",
    end_date="2024-12-31",
    leaf_name="neue_entgeltpunkte_aus_arbeitslosengeld_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_aus_arbeitslosengeld_nach_wohnort(
    sozialversicherung__arbeitslosen__grundsätzlich_anspruchsberechtigt: bool,
    sozialversicherung__arbeitslosen__mean_bruttoeinkommen_in_12_monaten_vor_arbeitslosigkeit_y: float,
    im_vorjahr_versicherungspflichtig: bool,
    wohnort_ost_hh: bool,
    beitrag__versicherungsfrei_wegen_alters: bool,
    beitrag__beitragsbemessungsgrenze_y: float,
    anteil_bemessungsentgelt_arbeitslosengeld: float,
    beitragspflichtiges_durchschnittsentgelt_y: float,
    umrechnung_entgeltpunkte_beitrittsgebiet: float,
) -> float:
    """Earnings points for drawing Arbeitslosengeld in the current year.

    A person covered under § 3 Satz 1 Nr. 3 SGB VI pays contributions on a share of the
    capped Arbeitsentgelt the benefit is based on (§ 166 Abs. 1 Nr. 2 SGB VI). Amounts
    in the Beitrittsgebiet are scaled up by Anlage 10 (§ 256a Abs. 1 SGB VI).
    """
    if wohnort_ost_hh:
        umrechnungswert = umrechnung_entgeltpunkte_beitrittsgebiet
    else:
        umrechnungswert = 1.0

    if (
        sozialversicherung__arbeitslosen__grundsätzlich_anspruchsberechtigt
        and im_vorjahr_versicherungspflichtig
        and not beitrag__versicherungsfrei_wegen_alters
    ):
        out = (
            umrechnungswert
            * anteil_bemessungsentgelt_arbeitslosengeld
            * min(
                sozialversicherung__arbeitslosen__mean_bruttoeinkommen_in_12_monaten_vor_arbeitslosigkeit_y,
                beitrag__beitragsbemessungsgrenze_y,
            )
            / beitragspflichtiges_durchschnittsentgelt_y
        )
    else:
        out = 0.0

    return cast_ttsim_unit(out, unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR)


@policy_function(
    start_date="2025-01-01",
    leaf_name="neue_entgeltpunkte_aus_arbeitslosengeld_y",
    unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_aus_arbeitslosengeld_einheitlich(
    sozialversicherung__arbeitslosen__grundsätzlich_anspruchsberechtigt: bool,
    sozialversicherung__arbeitslosen__mean_bruttoeinkommen_in_12_monaten_vor_arbeitslosigkeit_y: float,
    im_vorjahr_versicherungspflichtig: bool,
    beitrag__versicherungsfrei_wegen_alters: bool,
    beitrag__beitragsbemessungsgrenze_y: float,
    anteil_bemessungsentgelt_arbeitslosengeld: float,
    beitragspflichtiges_durchschnittsentgelt_y: float,
) -> float:
    """Earnings points for drawing Arbeitslosengeld in the current year.

    A person covered under § 3 Satz 1 Nr. 3 SGB VI pays contributions on a share of the
    capped Arbeitsentgelt the benefit is based on (§ 166 Abs. 1 Nr. 2 SGB VI).
    """
    if (
        sozialversicherung__arbeitslosen__grundsätzlich_anspruchsberechtigt
        and im_vorjahr_versicherungspflichtig
        and not beitrag__versicherungsfrei_wegen_alters
    ):
        out = (
            anteil_bemessungsentgelt_arbeitslosengeld
            * min(
                sozialversicherung__arbeitslosen__mean_bruttoeinkommen_in_12_monaten_vor_arbeitslosigkeit_y,
                beitrag__beitragsbemessungsgrenze_y,
            )
            / beitragspflichtiges_durchschnittsentgelt_y
        )
    else:
        out = 0.0

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
