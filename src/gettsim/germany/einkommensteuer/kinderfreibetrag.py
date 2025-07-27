"""Tax allowances for individuals or couples with children."""

from __future__ import annotations

from gettsim.tt import (
    AggType,
    agg_by_p_id_function,
    param_function,
    policy_function,
)


@policy_function()
def kinderfreibetrag_y(
    anzahl_kinderfreibeträge: int,
    kinderfreibetrag_pro_kind_y: float,
) -> float:
    """Individual child allowance."""
    return kinderfreibetrag_pro_kind_y * anzahl_kinderfreibeträge


@param_function()
def kinderfreibetrag_pro_kind_y(parameter_kinderfreibetrag: dict[str, float]) -> float:
    return sum(parameter_kinderfreibetrag.values())


@policy_function()
def anzahl_kinderfreibeträge(
    anzahl_kinderfreibeträge_1: int,
    anzahl_kinderfreibeträge_2: int,
) -> int:
    """Return the number of Kinderfreibeträge a person is entitled to.

    The person could be a parent or legal custodian.

    Note: Users should overwrite this function if there are single parents in the data
    who should receive two instead of one Kinderfreibeträge. GETTSIM does not
    automatically do this, even if the p_id of the other parent is set to missing (-1).
    """
    return anzahl_kinderfreibeträge_1 + anzahl_kinderfreibeträge_2


@agg_by_p_id_function(agg_type=AggType.SUM)
def anzahl_kinderfreibeträge_1(
    kindergeld__ist_leistungsbegründendes_kind: bool,
    p_id_kinderfreibetragsempfänger_1: int,
    p_id: int,
) -> int:
    pass


@agg_by_p_id_function(agg_type=AggType.SUM)
def anzahl_kinderfreibeträge_2(
    kindergeld__ist_leistungsbegründendes_kind: bool,
    p_id_kinderfreibetragsempfänger_2: int,
    p_id: int,
) -> int:
    pass


@policy_function()
def p_id_kinderfreibetragsempfänger_1(
    familie__p_id_elternteil_1: int,
) -> int:
    """Assigns child allowance to parent 1."""
    return familie__p_id_elternteil_1


@policy_function()
def p_id_kinderfreibetragsempfänger_2(
    familie__p_id_elternteil_2: int,
) -> int:
    """Assigns child allowance to parent 2."""
    return familie__p_id_elternteil_2
