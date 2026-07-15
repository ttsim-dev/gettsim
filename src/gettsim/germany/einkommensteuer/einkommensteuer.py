"""Income taxes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import portion

from gettsim.tt import (
    UNSET_UNIT,
    AggType,
    ConsecutiveIntLookupTableParamValue,
    PiecewisePolynomialParamValue,
    RoundingSpec,
    Unit,
    agg_by_p_id_function,
    cast_unit,
    get_piecewise_parameters,
    intervals_to_thresholds,
    param_function,
    piecewise_polynomial,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.typing import RawParamValue


@agg_by_p_id_function(agg_type=AggType.SUM, unit=Unit.PERSON_COUNT)
def anzahl_kindergeld_ansprüche_1(
    kindergeld__ist_leistungsbegründendes_kind: bool,
    familie__p_id_elternteil_1: int,
    p_id: int,
) -> int:
    pass


@agg_by_p_id_function(agg_type=AggType.SUM, unit=Unit.PERSON_COUNT)
def anzahl_kindergeld_ansprüche_2(
    kindergeld__ist_leistungsbegründendes_kind: bool,
    familie__p_id_elternteil_2: int,
    p_id: int,
) -> int:
    pass


@policy_function(
    end_date="1996-12-31",
    leaf_name="betrag_y_sn",
    rounding_spec=RoundingSpec(
        unit=Unit.DM.PER_YEAR.PER_SN,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S. 6 EStG",
    ),
    unit=Unit.CURRENCY.PER_YEAR.PER_SN,
)
def betrag_y_sn_kindergeld_kinderfreibetrag_parallel(
    betrag_mit_kinderfreibetrag_y_sn: float,
) -> float:
    """Income tax calculation on Steuernummer level allowing for claiming
    Kinderfreibetrag and receiving Kindergeld at the same time.
    """
    return betrag_mit_kinderfreibetrag_y_sn


@policy_function(
    start_date="2002-01-01",
    leaf_name="betrag_y_sn",
    rounding_spec=RoundingSpec(
        unit=Unit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S.6 EStG",
    ),
    unit=Unit.CURRENCY.PER_YEAR.PER_SN,
)
def betrag_y_sn_kindergeld_oder_kinderfreibetrag(
    betrag_ohne_kinderfreibetrag_y_sn: float,
    betrag_mit_kinderfreibetrag_y_sn: float,
    kinderfreibetrag_günstiger_sn: bool,
    relevantes_kindergeld_y_sn: float,
) -> float:
    """Income tax calculation on Steuernummer level since 1997."""
    if kinderfreibetrag_günstiger_sn:
        out = betrag_mit_kinderfreibetrag_y_sn + relevantes_kindergeld_y_sn
    else:
        out = betrag_ohne_kinderfreibetrag_y_sn

    return out


@policy_function(unit=Unit.DIMENSIONLESS.PER_SN)
def kinderfreibetrag_günstiger_sn(
    betrag_ohne_kinderfreibetrag_y_sn: float,
    betrag_mit_kinderfreibetrag_y_sn: float,
    relevantes_kindergeld_y_sn: float,
) -> bool:
    """Kinderfreibetrag more favorable than Kindergeld."""
    unterschiedsbeitrag = (
        betrag_ohne_kinderfreibetrag_y_sn - betrag_mit_kinderfreibetrag_y_sn
    )

    return unterschiedsbeitrag > relevantes_kindergeld_y_sn


@policy_function(
    end_date="2001-12-31",
    leaf_name="betrag_mit_kinderfreibetrag_y_sn",
    rounding_spec=RoundingSpec(
        unit=Unit.DM.PER_YEAR.PER_SN,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S.6 EStG",
    ),
    fail_msg_if_included="Tax system before 2002 is not implemented yet.",
    unit=Unit.CURRENCY.PER_YEAR.PER_SN,
)
def betrag_mit_kinderfreibetrag_y_sn_bis_2001() -> float:
    pass


@policy_function(
    start_date="2002-01-01",
    leaf_name="betrag_mit_kinderfreibetrag_y_sn",
    rounding_spec=RoundingSpec(
        unit=Unit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S.6 EStG",
    ),
    unit=Unit.CURRENCY.PER_YEAR.PER_SN,
)
def betrag_mit_kinderfreibetrag_y_sn_ab_2002(
    zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn: float,
    familie__anzahl_personen_sn: int,
    parameter_einkommensteuertarif: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Taxes with child allowance on Steuernummer level.

    Also referred to as "tarifliche ESt I".

    """
    zu_verst_eink_per_indiv = (
        zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
        / familie__anzahl_personen_sn
    )
    return familie__anzahl_personen_sn * piecewise_polynomial(
        x=zu_verst_eink_per_indiv,
        parameters=parameter_einkommensteuertarif,
        xnp=xnp,
    )


@policy_function(
    start_date="2002-01-01",
    rounding_spec=RoundingSpec(
        unit=Unit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S.6 EStG",
    ),
    unit=Unit.CURRENCY.PER_YEAR.PER_SN,
)
def betrag_ohne_kinderfreibetrag_y_sn(
    gesamteinkommen_y_sn: float,
    familie__anzahl_personen_sn: int,
    parameter_einkommensteuertarif: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Taxes without child allowance on Steuernummer level. Also referred to as
    "tarifliche ESt II".

    """
    zu_verst_eink_per_indiv = gesamteinkommen_y_sn / familie__anzahl_personen_sn
    return familie__anzahl_personen_sn * piecewise_polynomial(
        x=zu_verst_eink_per_indiv,
        parameters=parameter_einkommensteuertarif,
        xnp=xnp,
    )


@policy_function(
    end_date="2022-12-31",
    leaf_name="relevantes_kindergeld_m",
    unit=Unit.CURRENCY.PER_MONTH,
)
def relevantes_kindergeld_mit_staffelung_m(
    anzahl_kindergeld_ansprüche_1: int,
    anzahl_kindergeld_ansprüche_2: int,
    kindergeld__satz_nach_anzahl_kinder: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Kindergeld relevant for income tax. For each parent, half of the actual
    Kindergeld claim is considered.

    Note: It doesn't matter which parent actually receives the Kindergeld. For income
    tax purposes, only the eligibility to claim Kindergeld is relevant.

    Source: § 31 Satz 4 EStG: "Bei nicht zusammenveranlagten Eltern wird der
    Kindergeldanspruch im Umfang des Kinderfreibetrags angesetzt."

    """
    kindergeld_ansprüche = anzahl_kindergeld_ansprüche_1 + anzahl_kindergeld_ansprüche_2

    return (
        cast_unit(
            kindergeld__satz_nach_anzahl_kinder.look_up(kindergeld_ansprüche),
            Unit.CURRENCY.PER_MONTH,
        )
        / 2
    )


@policy_function(
    start_date="2023-01-01",
    leaf_name="relevantes_kindergeld_m",
    unit=Unit.CURRENCY.PER_MONTH,
)
def relevantes_kindergeld_ohne_staffelung_m(
    anzahl_kindergeld_ansprüche_1: int,
    anzahl_kindergeld_ansprüche_2: int,
    kindergeld__satz: float,
) -> float:
    """Kindergeld relevant for income tax. For each parent, half of the actual
    Kindergeld claim is considered.

    Note: It doesn't matter which parent actually receives the Kindergeld. For income
    tax purposes, only the eligibility to claim Kindergeld is relevant.

    Source: § 31 Satz 4 EStG: "Bei nicht zusammenveranlagten Eltern wird der
    Kindergeldanspruch im Umfang des Kinderfreibetrags angesetzt."

    """
    kindergeld_ansprüche = anzahl_kindergeld_ansprüche_1 + anzahl_kindergeld_ansprüche_2
    return kindergeld__satz * kindergeld_ansprüche / 2


@param_function(start_date="2002-01-01", unit=UNSET_UNIT)
def parameter_einkommensteuertarif(
    raw_parameter_einkommensteuertarif: RawParamValue,
    xnp: ModuleType,
) -> PiecewisePolynomialParamValue:
    """Add the quadratic terms to tax tariff function.

    The German tax tariff is defined on several income intervals with distinct
    marginal tax rates at the thresholds. To ensure an almost linear increase of
    the average tax rate, the German tax tariff is defined as a quadratic function,
    where the quadratic rate is the so called linear Progressionsfaktor. For its
    calculation one needs the lower (low_thres) and upper (upper_thres) thresholds of
    the interval as well as the marginal tax rate of the interval (rate_iv) and of the
    following interval (rate_fiv). The formula is then given by:

    (rate_fiv - rate_iv) / (2 * (upper_thres - low_thres))

    """
    raw_intervals = raw_parameter_einkommensteuertarif["intervals"]
    expanded: list[dict[str, float]] = [
        {k: v if isinstance(v, str) else float(v) for k, v in item.items()}
        for item in raw_intervals
    ]

    # Check and extract lower thresholds.
    parsed_intervals = [
        portion.from_string(item["interval"], conv=float) for item in expanded
    ]
    lower_thresholds, upper_thresholds = intervals_to_thresholds(
        intervals=parsed_intervals,
        xnp=xnp,
    )[:2]
    for i in range(len(expanded)):
        if "quadratic" not in raw_intervals[i]:
            expanded[i]["quadratic"] = float(
                (expanded[i + 1]["slope"] - expanded[i]["slope"])
                / (2 * (upper_thresholds[i] - lower_thresholds[i]))
            )
    return get_piecewise_parameters(
        leaf_name="parameter_einkommensteuertarif",
        func_type="piecewise_quadratic",
        parameter_list=expanded,  # ty: ignore[invalid-argument-type]
        xnp=xnp,
    )
