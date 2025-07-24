"""Aggregations for Arbeitslosengeld II."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    AggType,
    agg_by_group_function,
    join,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.typing import BoolColumn, IntColumn


@policy_function(start_date="2005-01-01")
def ist_kind_in_bedarfsgemeinschaft(
    familie__p_id_elternteil_1: IntColumn,
    familie__p_id_elternteil_2: IntColumn,
    p_id: IntColumn,
    bg_id: IntColumn,
    xnp: ModuleType,
) -> BoolColumn:
    """Child in a Bedarfsgemeinschaft."""
    bg_id_elternteil_1 = join(
        foreign_key=familie__p_id_elternteil_1,
        primary_key=p_id,
        target=bg_id,
        value_if_foreign_key_is_missing=-1,
        xnp=xnp,
    )
    bg_id_elternteil_2 = join(
        foreign_key=familie__p_id_elternteil_2,
        primary_key=p_id,
        target=bg_id,
        value_if_foreign_key_is_missing=-1,
        xnp=xnp,
    )
    in_gleicher_fg_wie_elternteil_1 = bg_id_elternteil_1 == bg_id
    in_gleicher_fg_wie_elternteil_2 = bg_id_elternteil_2 == bg_id
    return in_gleicher_fg_wie_elternteil_1 | in_gleicher_fg_wie_elternteil_2


@policy_function(start_date="2005-01-01")
def ist_erwachsener_in_bedarfsgemeinschaft(
    ist_kind_in_bedarfsgemeinschaft: bool,
) -> bool:
    """Adult in a Bedarfsgemeinschaft."""
    return not ist_kind_in_bedarfsgemeinschaft


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.COUNT)
def anzahl_personen_bg(bg_id: int) -> int:
    pass


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_erwachsene_bg(
    ist_erwachsener_in_bedarfsgemeinschaft: bool,
    bg_id: int,
) -> int:
    pass


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_kinder_bg(ist_kind_in_bedarfsgemeinschaft: bool, bg_id: int) -> int:
    pass


@policy_function(start_date="2005-01-01")
def ist_kind_bis_17_in_bedarfsgemeinschaft(
    alter: int, ist_kind_in_bedarfsgemeinschaft: bool
) -> bool:
    """Child under the age of 18 in Bedarfsgemeinschaft."""
    return ist_kind_in_bedarfsgemeinschaft and (alter <= 17)  # noqa: PLR2004


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_kinder_bis_17_bg(
    ist_kind_bis_17_in_bedarfsgemeinschaft: bool, bg_id: int
) -> int:
    pass


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.ANY)
def alleinerziehend_bg(familie__alleinerziehend: bool, bg_id: int) -> bool:
    pass


@policy_function(start_date="2005-01-01")
def hat_kind_in_gleicher_bedarfsgemeinschaft(
    anzahl_kinder_bg: int,
    ist_erwachsener_in_bedarfsgemeinschaft: bool,
) -> bool:
    """Has a child in the same Bedarfsgemeinschaft."""
    return anzahl_kinder_bg >= 1 and ist_erwachsener_in_bedarfsgemeinschaft
