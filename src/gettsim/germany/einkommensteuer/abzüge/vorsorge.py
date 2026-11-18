from __future__ import annotations

from typing import TYPE_CHECKING, Any

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    RoundingSpec,
    TTSIMUnit,
    cast_ttsim_unit,
    param_function,
    piecewise_polynomial,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType


@policy_function(
    start_date="2002-01-01",
    end_date="2004-12-31",
    leaf_name="vorsorgeaufwendungen_y_sn",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="up",
        reference="§ 10 Abs. 3 EStG",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def vorsorgeaufwendungen_y_sn_bis_2004(
    vorsorgeaufwendungen_regime_bis_2004_y_sn: float,
) -> float:
    """Vorsorgeaufwendungen until 2004."""
    return vorsorgeaufwendungen_regime_bis_2004_y_sn


@policy_function(
    start_date="2005-01-01",
    end_date="2009-12-31",
    leaf_name="vorsorgeaufwendungen_y_sn",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="up",
        reference="§ 10 Abs. 3 EStG",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def vorsorgeaufwendungen_y_sn_ab_2005_bis_2009(
    vorsorgeaufwendungen_regime_bis_2004_y_sn: float,
    vorsorgeaufwendungen_globale_kappung_y_sn: float,
) -> float:
    """Vorsorgeaufwendungen from 2005 to 2009.

    Günstigerprüfung against the regime until 2004.

    """
    return max(
        vorsorgeaufwendungen_regime_bis_2004_y_sn,
        vorsorgeaufwendungen_globale_kappung_y_sn,
    )


@policy_function(
    start_date="2010-01-01",
    end_date="2019-12-31",
    leaf_name="vorsorgeaufwendungen_y_sn",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="up",
        reference="§ 10 Abs. 3 EStG",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def vorsorgeaufwendungen_y_sn_ab_2010_bis_2019(
    vorsorgeaufwendungen_regime_bis_2004_y_sn: float,
    vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn: float,
) -> float:
    """Vorsorgeaufwendungen from 2010 to 2019.

    Günstigerprüfung against the regime until 2004.

    """
    return max(
        vorsorgeaufwendungen_regime_bis_2004_y_sn,
        vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn,
    )


@policy_function(
    start_date="2020-01-01",
    leaf_name="vorsorgeaufwendungen_y_sn",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="up",
        reference="§ 10 Abs. 3 EStG",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def vorsorgeaufwendungen_y_sn_ab_2020(
    vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn: float,
) -> float:
    """Vorsorgeaufwendungen since 2020.

    Günstigerprüfung against the regime until 2004 is revoked.

    """
    return vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn


@policy_function(
    end_date="2019-12-31",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
    # All arguments are Steuernummer totals, while the caps of this regime are written
    # per taxpayer. The body switches between the two views several times — dividing by
    # and multiplying with the head count — and compares per-taxpayer amounts with
    # Steuernummer totals, so no single unit describes its intermediate terms. The
    # declaration above and the units of all arguments are still checked.
    verify_units=False,
)
def vorsorgeaufwendungen_regime_bis_2004_y_sn(
    vorwegabzug_lohnsteuer_y_sn: float,
    abziehbare_krankenversicherungsbeiträge_y_sn: float,
    abziehbare_rentenversicherungsbeiträge_y_sn: float,
    familie__anzahl_personen_sn: int,
    parameter_altersvorsorgeaufwendungen_regime_bis_2004: dict[str, float],
) -> float:
    """Vorsorgeaufwendungen calculated using the regime until 2004."""
    multiplikator1 = max(
        (
            (
                abziehbare_rentenversicherungsbeiträge_y_sn
                + abziehbare_krankenversicherungsbeiträge_y_sn
            )
            - vorwegabzug_lohnsteuer_y_sn
        ),
        0.0,
    )

    item_1 = (1 / familie__anzahl_personen_sn) * multiplikator1

    höchstbetrag = parameter_altersvorsorgeaufwendungen_regime_bis_2004[
        "grundhöchstbetrag"
    ]

    multiplikator2 = min(item_1, höchstbetrag)

    item_2 = (1 / familie__anzahl_personen_sn) * multiplikator2

    höchstgrenze_item3 = familie__anzahl_personen_sn * höchstbetrag

    if (item_1 - item_2) > höchstgrenze_item3:
        item_3 = 0.5 * höchstgrenze_item3
    else:
        item_3 = 0.5 * (item_1 - item_2)

    return vorwegabzug_lohnsteuer_y_sn + item_2 + item_3


@policy_function(
    start_date="2005-01-01",
    end_date="2009-12-31",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def vorsorgeaufwendungen_globale_kappung_y_sn(
    altersvorsorge_y_sn: float,
    abziehbare_krankenversicherungsbeiträge_y_sn: float,
    abziehbare_arbeitslosenversicherungsbeiträge_y_sn: float,
    abziehbare_pflegeversicherungsbeiträge_y_sn: float,
    familie__anzahl_personen_sn: int,
    maximalbetrag_sonstige_vorsorgeaufwendungen: float,
) -> float:
    """Vorsorgeaufwendungen before favorability checks from 2005 to 2009.

    All deductions for social insurance contributions are capped.

    """
    sum_vorsorge = (
        abziehbare_krankenversicherungsbeiträge_y_sn
        + abziehbare_arbeitslosenversicherungsbeiträge_y_sn
        + abziehbare_pflegeversicherungsbeiträge_y_sn
    )
    max_value = (
        familie__anzahl_personen_sn * maximalbetrag_sonstige_vorsorgeaufwendungen
    )

    sum_vorsorge = min(sum_vorsorge, max_value)
    return sum_vorsorge + altersvorsorge_y_sn


@policy_function(
    start_date="2010-01-01",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn(
    altersvorsorge_y_sn: float,
    abziehbare_pflegeversicherungsbeiträge_y_sn: float,
    abziehbare_krankenversicherungsbeiträge_y_sn: float,
    abziehbare_arbeitslosenversicherungsbeiträge_y_sn: float,
    familie__anzahl_personen_sn: int,
    maximalbetrag_sonstige_vorsorgeaufwendungen: float,
    minderungsanteil_vorsorgeaufwendungen_für_krankenversicherungsbeiträge: float,
) -> float:
    """Vorsorgeaufwendungen.

    Expenses for health insurance contributions are not subject to any caps.

    """
    basiskrankenversicherung = (
        abziehbare_pflegeversicherungsbeiträge_y_sn
        + (1 - minderungsanteil_vorsorgeaufwendungen_für_krankenversicherungsbeiträge)
        * abziehbare_krankenversicherungsbeiträge_y_sn
    )

    sonst_vors_max = (
        maximalbetrag_sonstige_vorsorgeaufwendungen * familie__anzahl_personen_sn
    )
    sonst_vors_before_basiskrankenv = min(
        (
            abziehbare_arbeitslosenversicherungsbeiträge_y_sn
            + abziehbare_pflegeversicherungsbeiträge_y_sn
            + abziehbare_krankenversicherungsbeiträge_y_sn
        ),
        sonst_vors_max,
    )

    # Basiskrankenversicherung can always be deducted even if above sonst_vors_max
    sonst_vors = max(basiskrankenversicherung, sonst_vors_before_basiskrankenv)

    return sonst_vors + altersvorsorge_y_sn


@param_function(
    start_date="2005-01-01", end_date="2022-12-31", unit=TTSIMUnit.DIMENSIONLESS
)
def rate_abzugsfähige_altersvorsorgeaufwendungen(
    parameter_einführungsfaktor_altersvorsorgeaufwendungen: PiecewisePolynomialParamValue,
    policy_year: int,
    xnp: ModuleType,
) -> dict[str, Any]:
    """Calculate introductory factor for pension expense deductions which depends on the
    current year as follows:

    In the years 2005-2025 the share of deductible contributions increases by
    2 percentage points each year from 60% in 2005 to 100% in 2025.

    Reference: § 10 Abs. 1 Nr. 2 Buchst. a und b EStG


    """
    return piecewise_polynomial(
        x=policy_year,
        parameters=parameter_einführungsfaktor_altersvorsorgeaufwendungen,
        xnp=xnp,
    )


@policy_function(
    start_date="2005-01-01",
    end_date="2022-12-31",
    leaf_name="altersvorsorge_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def altersvorsorge_y_sn_phase_in(
    abziehbare_rentenversicherungsbeiträge_y_sn: float,
    beitrag_private_rentenversicherung_y_sn: float,
    familie__anzahl_personen_sn: int,
    rate_abzugsfähige_altersvorsorgeaufwendungen: float,
    maximalbetrag_altersvorsorgeaufwendungen_y: float,
) -> float:
    """Contributions to retirement savings deductible from taxable income.

    The Höchstbetrag caps employee and employer pension contributions plus private
    contributions. The share of deductible contributions applies to the capped amount
    and increases each year from 60% in 2005 to 100% in 2025. The employer share is
    subtracted last (§ 10 Abs. 3 Sätze 1 bis 6 EStG). Both contributions count only as
    far as they are not linked to tax-free wages (BMF-Schreiben vom 24.05.2017, Rz 199).

    The employer share is taken to equal the employee share.
    """
    capped = min(
        2 * abziehbare_rentenversicherungsbeiträge_y_sn
        + beitrag_private_rentenversicherung_y_sn,
        familie__anzahl_personen_sn * maximalbetrag_altersvorsorgeaufwendungen_y,
    )
    return (
        rate_abzugsfähige_altersvorsorgeaufwendungen * capped
        - abziehbare_rentenversicherungsbeiträge_y_sn
    )


@policy_function(
    start_date="2023-01-01",
    leaf_name="altersvorsorge_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def altersvorsorge_y_sn_volle_anrechnung(
    abziehbare_rentenversicherungsbeiträge_y_sn: float,
    beitrag_private_rentenversicherung_y_sn: float,
    familie__anzahl_personen_sn: int,
    maximalbetrag_altersvorsorgeaufwendungen_y: float,
) -> float:
    """Contributions to retirement savings deductible from taxable income.

    The Höchstbetrag caps employee and employer pension contributions plus private
    contributions; the employer share is subtracted afterwards (§ 10 Abs. 3 Sätze 1 bis 6
    EStG). Both contributions count only as far as they are not linked to tax-free wages
    (BMF-Schreiben vom 24.05.2017, Rz 199).

    The employer share is taken to equal the employee share.
    """
    capped = min(
        2 * abziehbare_rentenversicherungsbeiträge_y_sn
        + beitrag_private_rentenversicherung_y_sn,
        familie__anzahl_personen_sn * maximalbetrag_altersvorsorgeaufwendungen_y,
    )
    return capped - abziehbare_rentenversicherungsbeiträge_y_sn


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def abziehbare_rentenversicherungsbeiträge_y(
    sozialversicherung__rente__beitrag__betrag_versicherter_y: float,
    einnahmen__bruttolohn_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anteil_steuerfälliger_einnahmen: float,
) -> float:
    """Pension insurance contributions not linked to tax-free wages.

    Contributions linked to tax-free wages are not deductible (§ 10 Abs. 2 Satz 1 Nr. 1
    EStG). They are split in proportion to the tax-free share of the wage (BMF-Schreiben
    vom 24.05.2017, Rz 199). The ratio uses the whole wage, also above the
    Beitragsbemessungsgrenze (BMF-Schreiben vom 05.09.2024, Abschnitt I Nr. 15).
    """
    if einnahmen__bruttolohn_y > 0.0:
        return (
            sozialversicherung__rente__beitrag__betrag_versicherter_y
            * einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anteil_steuerfälliger_einnahmen
        )
    else:
        return sozialversicherung__rente__beitrag__betrag_versicherter_y


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def abziehbare_arbeitslosenversicherungsbeiträge_y(
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y: float,
    einnahmen__bruttolohn_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anteil_steuerfälliger_einnahmen: float,
) -> float:
    """Unemployment insurance contributions not linked to tax-free wages.

    Contributions linked to tax-free wages are not deductible (§ 10 Abs. 2 Satz 1 Nr. 1
    EStG). They are split in proportion to the tax-free share of the wage (BMF-Schreiben
    vom 24.05.2017, Rz 199; BMF-Schreiben vom 05.09.2024, Abschnitt I Nr. 15).
    """
    if einnahmen__bruttolohn_y > 0.0:
        return (
            sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y
            * einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anteil_steuerfälliger_einnahmen
        )
    else:
        return sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def abziehbare_krankenversicherungsbeiträge_y(
    sozialversicherung__kranken__beitrag__betrag_versicherter_y: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_aus_erwerbseinkommen_y: float,
    einnahmen__bruttolohn_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anteil_steuerfälliger_einnahmen: float,
) -> float:
    """Health insurance contributions not linked to tax-free wages.

    Contributions linked to tax-free wages are not deductible (§ 10 Abs. 2 Satz 1 Nr. 1
    EStG). The tax-free share of the contributions on wages is subtracted (BMF-Schreiben
    vom 24.05.2017, Rz 199); contributions on pensions are deductible in full (Rz 200).
    """
    if einnahmen__bruttolohn_y > 0.0:
        return (
            sozialversicherung__kranken__beitrag__betrag_versicherter_y
            - (
                1.0
                - einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anteil_steuerfälliger_einnahmen
            )
            * sozialversicherung__kranken__beitrag__betrag_versicherter_aus_erwerbseinkommen_y
        )
    else:
        return sozialversicherung__kranken__beitrag__betrag_versicherter_y


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def abziehbare_pflegeversicherungsbeiträge_y(
    sozialversicherung__pflege__beitrag__betrag_versicherter_y: float,
    sozialversicherung__pflege__beitrag__betrag_versicherter_aus_erwerbseinkommen_y: float,
    einnahmen__bruttolohn_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anteil_steuerfälliger_einnahmen: float,
) -> float:
    """Long-term care insurance contributions not linked to tax-free wages.

    Contributions linked to tax-free wages are not deductible (§ 10 Abs. 2 Satz 1 Nr. 1
    EStG). The tax-free share of the contributions on wages is subtracted (BMF-Schreiben
    vom 24.05.2017, Rz 199); contributions on pensions are deductible in full (Rz 200).
    """
    if einnahmen__bruttolohn_y > 0.0:
        return (
            sozialversicherung__pflege__beitrag__betrag_versicherter_y
            - (
                1.0
                - einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__anteil_steuerfälliger_einnahmen
            )
            * sozialversicherung__pflege__beitrag__betrag_versicherter_aus_erwerbseinkommen_y
        )
    else:
        return sozialversicherung__pflege__beitrag__betrag_versicherter_y


@policy_function(
    end_date="2019-12-31",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def vorwegabzug_lohnsteuer_y_sn(
    einnahmen__bruttolohn_y_sn: float,
    familie__anzahl_personen_sn: int,
    parameter_altersvorsorgeaufwendungen_regime_bis_2004: dict[str, float],
) -> float:
    """Vorwegabzug for Vorsorgeaufwendungen via Lohnsteuer."""
    out = (
        familie__anzahl_personen_sn
        * parameter_altersvorsorgeaufwendungen_regime_bis_2004["vorwegabzug"]
        - parameter_altersvorsorgeaufwendungen_regime_bis_2004[
            "kürzungsanteil_abhängig_beschäftigte"
        ]
        * einnahmen__bruttolohn_y_sn
    ) / familie__anzahl_personen_sn

    # The parenthesised term is a Steuernummer total; dividing it by the head count
    # makes it a per-taxpayer amount. It still enters
    # `vorsorgeaufwendungen_regime_bis_2004_y_sn` as a Steuernummer amount, so tag it as
    # one. The level is lost in this one spot only, so a cast is enough here and the
    # rest of the body stays checked.
    return cast_ttsim_unit(max(out, 0.0), unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)


@param_function(start_date="2015-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def maximalbetrag_altersvorsorgeaufwendungen_y(
    sozialversicherung__rente__beitrag__beitragssatz_knappschaftliche_rentenversicherung: float,
    sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_knappschaftliche_rentenversicherung_west_y: float,
    xnp: ModuleType,
) -> float:
    """Maximalbetrag der Altersvorsorgeaufwendungen."""
    return xnp.ceil(
        sozialversicherung__rente__beitrag__beitragssatz_knappschaftliche_rentenversicherung
        * sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_knappschaftliche_rentenversicherung_west_y
    )
