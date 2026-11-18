"""Income relevant for withholding tax on earnings (Lohnsteuer)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    RoundingSpec,
    TTSIMUnit,
    param_function,
    piecewise_polynomial,
    policy_function,
)


@policy_function(
    start_date="2002-01-01",
    end_date="2025-12-31",
    rounding_spec=RoundingSpec(unit=TTSIMUnit.EUR.PER_YEAR, base=1, direction="down"),
    leaf_name="einkommen_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def einkommen_y_bis_2025(
    einnahmen__bruttolohn_y: float,
    steuerklasse: int,
    vorsorgepauschale_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag: float,
    einkommensteuer__abzüge__alleinerziehendenfreibetrag_basis_y: float,
    einkommensteuer__abzüge__sonderausgabenpauschbetrag: float,
) -> float:
    """Steuerbasis for Lohnsteuer (withholding tax on earnings)."""
    if steuerklasse == 6:
        werbungskosten = 0.0
    else:
        werbungskosten = einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag

    if steuerklasse == 6:
        sonderausgaben = 0.0
    else:
        sonderausgaben = einkommensteuer__abzüge__sonderausgabenpauschbetrag

    if steuerklasse == 2:
        alleinerziehendenfreibetrag = (
            einkommensteuer__abzüge__alleinerziehendenfreibetrag_basis_y
        )
    else:
        alleinerziehendenfreibetrag = 0.0

    return max(
        einnahmen__bruttolohn_y
        - werbungskosten
        - sonderausgaben
        - alleinerziehendenfreibetrag
        - vorsorgepauschale_y,
        0.0,
    )


@policy_function(
    start_date="2026-01-01",
    rounding_spec=RoundingSpec(unit=TTSIMUnit.EUR.PER_YEAR, base=1, direction="down"),
    leaf_name="einkommen_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def einkommen_y_ab_2026(
    steuerpflichtiger_arbeitslohn_y: float,
    steuerklasse: int,
    vorsorgepauschale_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag: float,
    einkommensteuer__abzüge__alleinerziehendenfreibetrag_basis_y: float,
    einkommensteuer__abzüge__sonderausgabenpauschbetrag: float,
) -> float:
    """Steuerbasis for Lohnsteuer (withholding tax on earnings)."""
    if steuerklasse == 6:
        werbungskosten = 0.0
    else:
        werbungskosten = einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag

    if steuerklasse == 6:
        sonderausgaben = 0.0
    else:
        sonderausgaben = einkommensteuer__abzüge__sonderausgabenpauschbetrag

    if steuerklasse == 2:
        alleinerziehendenfreibetrag = (
            einkommensteuer__abzüge__alleinerziehendenfreibetrag_basis_y
        )
    else:
        alleinerziehendenfreibetrag = 0.0

    return max(
        steuerpflichtiger_arbeitslohn_y
        - werbungskosten
        - sonderausgaben
        - alleinerziehendenfreibetrag
        - vorsorgepauschale_y,
        0.0,
    )


@policy_function(start_date="2026-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def steuerpflichtiger_arbeitslohn_y(
    einnahmen__bruttolohn_y: float,
    steuerklasse: int,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anspruchshöhe_steuerfreibetrag_aktivrente_y: float,
) -> float:
    """Wage subject to Lohnsteuer, net of the Aktivrente.

    The Lohnsteuer is only computed on the wage above the Aktivrente. This wage is also
    the base of the Teilbeträge of the Vorsorgepauschale. The Aktivrente is not part of
    the Programmablaufplan; employers pass the wage net of it.

    The Altersentlastungsbetrag (§ 39b Abs. 2 Satz 3 EStG) is not deducted yet, see
    https://github.com/ttsim-dev/gettsim/issues/1259.

    Reference: § 3 Nr. 21 EStG; BMF FAQ zur Aktivrente III.4; BMF-Schreiben vom
    14.08.2025 zur Vorsorgepauschale, Rn. 5.
    """
    if steuerklasse == 6:
        # TODO(@MImmesberger): With Steuerklasse 6, the deduction is only applied if the
        # individual does not claim the deduction for another job. As GETTSIM does not
        # support multiple jobs yet, we don't model this distinction. We assume that the
        # Aktivrente is applied to the primary job, not the secondary job.
        # https://github.com/ttsim-dev/gettsim/issues/1249
        return einnahmen__bruttolohn_y
    else:
        return (
            einnahmen__bruttolohn_y
            - einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anspruchshöhe_steuerfreibetrag_aktivrente_y
        )


@policy_function(
    start_date="2010-01-01", end_date="2025-12-31", unit=TTSIMUnit.CURRENCY.PER_YEAR
)
def vorsorge_krankenversicherungsbeiträge_option_a_y(
    sozialversicherung__kranken__beitrag__einkommen_bis_beitragsbemessungsgrenze_y: float,
    steuerklasse: int,
    vorsorgepauschale_mindestanteil: float,
    maximal_absetzbare_krankenversicherungskosten: dict[str, float],
) -> float:
    """Option a for calculating deductible health insurance contributions.

    This function calculates option a where at least 12% of earnings can be deducted,
    but only up to a certain threshold.

    """
    vorsorge_krankenversicherungsbeiträge_option_a_basis = (
        vorsorgepauschale_mindestanteil
        * sozialversicherung__kranken__beitrag__einkommen_bis_beitragsbemessungsgrenze_y
    )

    if steuerklasse == 3:
        vorsorge_krankenversicherungsbeiträge_option_a_max = (
            maximal_absetzbare_krankenversicherungskosten["steuerklasse_3"]
        )
    else:
        vorsorge_krankenversicherungsbeiträge_option_a_max = (
            maximal_absetzbare_krankenversicherungskosten["steuerklasse_nicht_3"]
        )

    return min(
        vorsorge_krankenversicherungsbeiträge_option_a_max,
        vorsorge_krankenversicherungsbeiträge_option_a_basis,
    )


@policy_function(
    start_date="2015-01-01",
    end_date="2018-12-31",
    leaf_name="vorsorge_krankenversicherungsbeiträge_option_b_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorge_krankenversicherungsbeiträge_option_b_ab_2015_bis_2018(
    sozialversicherung__kranken__beitrag__einkommen_bis_beitragsbemessungsgrenze_y: float,
    sozialversicherung__kranken__beitrag__zusatzbeitragssatz: float,
    sozialversicherung__pflege__beitrag__beitragssatz_arbeitnehmer: float,
    sozialversicherung__kranken__beitrag__parameter_beitragssatz: dict[str, float],
) -> float:
    """Option b for calculating deductible health insurance cont.

    For health care deductions, there are two ways to calculate the deductions: "Option
    a" and "Option b". This function calculates option b where the actual contributions
    are used.
    """
    return (
        sozialversicherung__kranken__beitrag__einkommen_bis_beitragsbemessungsgrenze_y
        * (
            sozialversicherung__kranken__beitrag__parameter_beitragssatz["ermäßigt"] / 2
            + sozialversicherung__kranken__beitrag__zusatzbeitragssatz
            + sozialversicherung__pflege__beitrag__beitragssatz_arbeitnehmer
        )
    )


@policy_function(
    start_date="2019-01-01",
    end_date="2025-12-31",
    leaf_name="vorsorge_krankenversicherungsbeiträge_option_b_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorge_krankenversicherungsbeiträge_option_b_ab_2019(
    sozialversicherung__kranken__beitrag__einkommen_bis_beitragsbemessungsgrenze_y: float,
    sozialversicherung__kranken__beitrag__zusatzbeitragssatz: float,
    sozialversicherung__pflege__beitrag__beitragssatz_arbeitnehmer: float,
    sozialversicherung__kranken__beitrag__parameter_beitragssatz: dict[str, float],
) -> float:
    """Option b for calculating deductible health insurance cont.

    For health care deductions, there are two ways to calculate the deductions: "Option
    a" and "Option b". This function calculates option b where the actual contributions
    are used.
    """
    return (
        sozialversicherung__kranken__beitrag__einkommen_bis_beitragsbemessungsgrenze_y
        * (
            sozialversicherung__kranken__beitrag__parameter_beitragssatz["ermäßigt"] / 2
            + sozialversicherung__kranken__beitrag__zusatzbeitragssatz / 2
            + sozialversicherung__pflege__beitrag__beitragssatz_arbeitnehmer
        )
    )


@policy_function(start_date="2026-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def vorsorge_gesetzliche_krankenversicherungsbeiträge_y(
    sozialversicherung__kranken__beitrag__privat_versichert: bool,
    steuerpflichtiger_arbeitslohn_y: float,
    sozialversicherung__kranken__beitrag__beitragsbemessungsgrenze_y: float,
    sozialversicherung__kranken__beitrag__zusatzbeitragssatz: float,
    sozialversicherung__pflege__beitrag__beitragssatz_arbeitnehmer: float,
    sozialversicherung__kranken__beitrag__parameter_beitragssatz: dict[str, float],
) -> float:
    """Vorsorgepauschale für gesetzliche Krankenversicherungsbeiträge.

    The Übergangsbereich is ignored (BMF-Schreiben 14.08.2025, Rn. 7).

    Reference: § 39b Abs. 2 Satz 5 Nr. 3 Buchst. b und c EStG.
    """
    if sozialversicherung__kranken__beitrag__privat_versichert:
        return 0.0
    else:
        return min(
            steuerpflichtiger_arbeitslohn_y,
            sozialversicherung__kranken__beitrag__beitragsbemessungsgrenze_y,
        ) * (
            sozialversicherung__kranken__beitrag__parameter_beitragssatz["ermäßigt"] / 2
            + sozialversicherung__kranken__beitrag__zusatzbeitragssatz / 2
            + sozialversicherung__pflege__beitrag__beitragssatz_arbeitnehmer
        )


@policy_function(start_date="2026-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def vorsorge_arbeitslosenversicherungsbeiträge_y(
    steuerpflichtiger_arbeitslohn_y: float,
    sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_y: float,
    sozialversicherung__arbeitslosen__beitrag__beitragssatz: float,
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
) -> float:
    """Vorsorgepauschale für Arbeitslosenversicherungsbeiträge.

    Employees past the Regelaltersgrenze are versicherungsfrei (§ 28 Abs. 1 Nr. 1 SGB
    III).

    Reference: § 39b Abs. 2 Satz 5 Nr. 3 Buchst. e EStG.
    """
    if sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze:
        return 0.0
    else:
        return (
            min(
                steuerpflichtiger_arbeitslohn_y,
                sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_y,
            )
            * sozialversicherung__arbeitslosen__beitrag__beitragssatz
            / 2
        )


@policy_function(
    end_date="2022-12-31",
    leaf_name="vorsorge_rentenversicherungsbeiträge_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorge_rentenversicherungsbeiträge_teilweise_anrechnung_y(
    sozialversicherung__rente__beitrag__einkommen_y: float,
    sozialversicherung__rente__beitrag__beitragssatz: float,
    sozialversicherung__rente__beitrag__versicherungsfrei_wegen_alters: bool,
    einführungsfaktor_rentenversicherungsaufwendungen: float,
) -> float:
    """Vorsorgepauschale für Rentenversicherungsbeiträge.

    Until 2022 only a share of the contributions is deducted. It rises by 4 percentage
    points each year from 40% in 2010 to 88% in 2022 (§ 39b Abs. 4 EStG).

    Only employees who are pflichtversichert in the public pension insurance or befreit
    under § 6 Abs. 1 Nr. 1 SGB VI get this Teilbetrag (§ 39b Abs. 2 Satz 5 Nr. 3
    Buchst. a EStG).
    """
    # TODO(@MImmesberger): Should also return 0 for other individuals that are not
    # insured via the public pension fund (or a berufsständische Rentenversicherung),
    # e.g. Minijobber who are exempt from mandatory pension insurance (BMF-Schreiben
    # vom 14.08.2025 zur Vorsorgepauschale, Rn. 11).
    # https://github.com/ttsim-dev/gettsim/issues/1114
    if sozialversicherung__rente__beitrag__versicherungsfrei_wegen_alters:
        return 0.0
    else:
        return (
            sozialversicherung__rente__beitrag__einkommen_y
            * sozialversicherung__rente__beitrag__beitragssatz
            / 2
            * einführungsfaktor_rentenversicherungsaufwendungen
        )


@policy_function(
    start_date="2023-01-01",
    end_date="2025-12-31",
    leaf_name="vorsorge_rentenversicherungsbeiträge_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorge_rentenversicherungsbeiträge_volle_anrechnung_y(
    sozialversicherung__rente__beitrag__einkommen_y: float,
    sozialversicherung__rente__beitrag__beitragssatz: float,
    sozialversicherung__rente__beitrag__versicherungsfrei_wegen_alters: bool,
) -> float:
    """Vorsorgepauschale für Rentenversicherungsbeiträge.

    Since 2023 the contributions are fully deductible.

    Only employees who are pflichtversichert in the public pension insurance or befreit
    under § 6 Abs. 1 Nr. 1 SGB VI get this Teilbetrag (§ 39b Abs. 2 Satz 5 Nr. 3
    Buchst. a EStG).
    """
    # TODO(@MImmesberger): Should also return 0 for other individuals that are not
    # insured via the public pension fund (or a berufsständische Rentenversicherung),
    # e.g. Minijobber who are exempt from mandatory pension insurance (BMF-Schreiben
    # vom 14.08.2025 zur Vorsorgepauschale, Rn. 11).
    # https://github.com/ttsim-dev/gettsim/issues/1114
    if sozialversicherung__rente__beitrag__versicherungsfrei_wegen_alters:
        return 0.0
    else:
        return (
            sozialversicherung__rente__beitrag__einkommen_y
            * sozialversicherung__rente__beitrag__beitragssatz
            / 2
        )


@policy_function(
    start_date="2026-01-01",
    leaf_name="vorsorge_rentenversicherungsbeiträge_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorge_rentenversicherungsbeiträge_auf_steuerpflichtigen_arbeitslohn_y(
    steuerpflichtiger_arbeitslohn_y: float,
    sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_y: float,
    sozialversicherung__rente__beitrag__beitragssatz: float,
    sozialversicherung__rente__beitrag__versicherungsfrei_wegen_alters: bool,
) -> float:
    """Vorsorgepauschale für Rentenversicherungsbeiträge.

    Since 2026 the base is the wage net of the Aktivrente, capped at the
    Beitragsbemessungsgrenze.

    Only employees who are pflichtversichert in the public pension insurance or befreit
    under § 6 Abs. 1 Nr. 1 SGB VI get this Teilbetrag.

    Reference: § 39b Abs. 2 Satz 5 Nr. 3 Buchst. a EStG.
    """
    # TODO(@MImmesberger): Should also return 0 for other individuals that are not
    # insured via the public pension fund (or a berufsständische Rentenversicherung),
    # e.g. Minijobber who are exempt from mandatory pension insurance (BMF-Schreiben
    # vom 14.08.2025 zur Vorsorgepauschale, Rn. 11).
    # https://github.com/ttsim-dev/gettsim/issues/1114
    if sozialversicherung__rente__beitrag__versicherungsfrei_wegen_alters:
        return 0.0
    else:
        return (
            min(
                steuerpflichtiger_arbeitslohn_y,
                sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_y,
            )
            * sozialversicherung__rente__beitrag__beitragssatz
            / 2
        )


@param_function(
    start_date="2005-01-01", end_date="2022-12-31", unit=TTSIMUnit.DIMENSIONLESS
)
def einführungsfaktor_rentenversicherungsaufwendungen(
    parameter_einführungsfaktor_rentenversicherungsaufwendungen: PiecewisePolynomialParamValue,
    policy_year: int,
    xnp: ModuleType,
) -> dict[str, Any]:
    """Share of pension insurance contributions in the Vorsorgepauschale.

    The share rises by 4 percentage points each year from 40% in 2010 to 88% in 2022.
    Since 2023, contributions are fully deductible.

    Reference: § 39b Abs. 4 EStG.
    """
    return piecewise_polynomial(
        x=policy_year,
        parameters=parameter_einführungsfaktor_rentenversicherungsaufwendungen,
        xnp=xnp,
    )


@policy_function(
    start_date="2026-01-01",
    rounding_spec=RoundingSpec(unit=TTSIMUnit.EUR.PER_YEAR, base=1, direction="up"),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorgepauschale_ohne_arbeitslosenversicherungsbeiträge_y(
    sozialversicherung__kranken__beitrag__privat_versichert: bool,
    sozialversicherung__kranken__beitrag__beitrag_private_basiskrankenversicherung_abzüglich_arbeitgeberanteil_y: float,
    vorsorge_gesetzliche_krankenversicherungsbeiträge_y: float,
    vorsorge_rentenversicherungsbeiträge_y: float,
    steuerklasse: int,
) -> float:
    """Vorsorgepauschale without unemployment insurance contributions.

    Reference: Calculation of 'MVSPKVPV' in Programmablaufplan Lohnsteuer BMF
    2025-11-12; § 39b Absatz 2 Satz 5 Nummer 3 Buchstaben b bis d EStG
    """
    if sozialversicherung__kranken__beitrag__privat_versichert and steuerklasse == 6:
        kv_pv_aufwendungen_y = 0.0
    elif sozialversicherung__kranken__beitrag__privat_versichert:
        kv_pv_aufwendungen_y = max(
            sozialversicherung__kranken__beitrag__beitrag_private_basiskrankenversicherung_abzüglich_arbeitgeberanteil_y,
            0.0,
        )
    else:
        kv_pv_aufwendungen_y = vorsorge_gesetzliche_krankenversicherungsbeiträge_y
    return kv_pv_aufwendungen_y + vorsorge_rentenversicherungsbeiträge_y


@policy_function(
    start_date="2026-01-01",
    rounding_spec=RoundingSpec(unit=TTSIMUnit.EUR.PER_YEAR, base=1, direction="up"),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorgepauschale_mit_arbeitslosenversicherungsbeiträgen_y(
    vorsorge_rentenversicherungsbeiträge_y: float,
    vorsorge_gesetzliche_krankenversicherungsbeiträge_y: float,
    vorsorge_arbeitslosenversicherungsbeiträge_y: float,
    vorsorgeaufwendungen_grenze_zur_berücksichtigung_arbeitslosenversicherungsbeiträge_y: float,
) -> float:
    """Vorsorgepauschale considering unemployment insurance contributions.

    Unemployment insurance contributions are now deductible up to a certain limit.

    Reference: Calculation of 'MVSPHB' in Programmablaufplan Lohnsteuer BMF 2025-11-12;
    § 39b Absatz 2 Satz 5 Nummer 3 Buchstabe e EStG.
    """
    summe_av_kv_pv = min(
        vorsorge_arbeitslosenversicherungsbeiträge_y
        + vorsorge_gesetzliche_krankenversicherungsbeiträge_y,
        vorsorgeaufwendungen_grenze_zur_berücksichtigung_arbeitslosenversicherungsbeiträge_y,
    )
    return vorsorge_rentenversicherungsbeiträge_y + summe_av_kv_pv


@policy_function(
    start_date="2005-01-01",
    end_date="2009-12-31",
    leaf_name="vorsorgepauschale_y",
    fail_msg_if_included="Vorsorgepauschale not implemented before 2010.",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorgepauschale_y_ab_2005_bis_2009() -> float:
    pass


@policy_function(
    start_date="2010-01-01",
    end_date="2025-12-31",
    leaf_name="vorsorgepauschale_y",
    rounding_spec=RoundingSpec(unit=TTSIMUnit.EUR.PER_YEAR, base=1, direction="up"),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorgepauschale_y_ab_2010_bis_2025(
    vorsorge_rentenversicherungsbeiträge_y: float,
    vorsorge_krankenversicherungsbeiträge_option_a_y: float,
    vorsorge_krankenversicherungsbeiträge_option_b_y: float,
) -> float:
    """Vorsorgepauschale for Lohnsteuer valid since 2010.

    Those are deducted from gross earnings. Idea is similar, but not identical, to
    Vorsorgeaufwendungen used when calculating Einkommensteuer.
    """
    kranken = max(
        vorsorge_krankenversicherungsbeiträge_option_a_y,
        vorsorge_krankenversicherungsbeiträge_option_b_y,
    )
    return vorsorge_rentenversicherungsbeiträge_y + kranken


@policy_function(
    start_date="2026-01-01",
    leaf_name="vorsorgepauschale_y",
    rounding_spec=RoundingSpec(unit=TTSIMUnit.EUR.PER_YEAR, base=1, direction="up"),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def vorsorgepauschale_y_ab_2026(
    vorsorgepauschale_mit_arbeitslosenversicherungsbeiträgen_y: float,
    vorsorgepauschale_ohne_arbeitslosenversicherungsbeiträge_y: float,
    steuerklasse: int,
) -> float:
    """Vorsorgepauschale for Lohnsteuer valid since 2026.

    Favorability check between Vorsorgepauschale with and without unemployment insurance
    contributions.

    Reference: Last part of calculation of 'MVSPKVPV' and 'MVSPHB' in Programmablaufplan
    Lohnsteuer BMF 2025-11-12
    """
    # TODO(@MImmesberger): Should return
    # vorsorgepauschale_ohne_arbeitslosenversicherungsbeiträge_y for individuals other
    # than those past the Regelaltersgrenze that do not pay mandatory unemployment
    # insurance contributions.
    # https://github.com/ttsim-dev/gettsim/issues/1114
    if steuerklasse == 6:
        return vorsorgepauschale_ohne_arbeitslosenversicherungsbeiträge_y
    else:
        return max(
            vorsorgepauschale_mit_arbeitslosenversicherungsbeiträgen_y,
            vorsorgepauschale_ohne_arbeitslosenversicherungsbeiträge_y,
        )
