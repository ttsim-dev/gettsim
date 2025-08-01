"""This module computes demographic variables directly on the data.

These information are used throughout modules of gettsim.

"""

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


@policy_function(vectorization_strategy="not_required")
def ist_kind_in_familiengemeinschaft(
    p_id_elternteil_1: IntColumn,
    p_id_elternteil_2: IntColumn,
    p_id: IntColumn,
    fg_id: IntColumn,
    xnp: ModuleType,
) -> BoolColumn:
    """
    Determines whether the given person is a child in a family group.
    """
    fg_id_elternteil_1 = join(
        foreign_key=p_id_elternteil_1,
        primary_key=p_id,
        target=fg_id,
        value_if_foreign_key_is_missing=-1,
        xnp=xnp,
    )
    fg_id_elternteil_2 = join(
        foreign_key=p_id_elternteil_2,
        primary_key=p_id,
        target=fg_id,
        value_if_foreign_key_is_missing=-1,
        xnp=xnp,
    )
    in_gleicher_fg_wie_elternteil_1 = fg_id_elternteil_1 == fg_id
    in_gleicher_fg_wie_elternteil_2 = fg_id_elternteil_2 == fg_id
    return in_gleicher_fg_wie_elternteil_1 | in_gleicher_fg_wie_elternteil_2


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_kinder_fg(ist_kind_in_familiengemeinschaft: bool, fg_id: int) -> int:
    pass


@policy_function()
def ist_kind_bis_2_in_familiengemeinschaft(
    alter: int, ist_kind_in_familiengemeinschaft: bool
) -> bool:
    """Child under the age of 3 in Familiengemeinschaft."""
    return ist_kind_in_familiengemeinschaft and (alter <= 2)


@agg_by_group_function(agg_type=AggType.SUM)
def anzahl_kinder_bis_2_fg(
    ist_kind_bis_2_in_familiengemeinschaft: bool, fg_id: int
) -> int:
    pass


@policy_function()
def ist_kind_bis_5_in_familiengemeinschaft(
    alter: int, ist_kind_in_familiengemeinschaft: bool
) -> bool:
    """Child under the age of 6 in Familiengemeinschaft."""
    return ist_kind_in_familiengemeinschaft and (alter <= 5)


@agg_by_group_function(agg_type=AggType.SUM)
def anzahl_kinder_bis_5_fg(
    ist_kind_bis_5_in_familiengemeinschaft: bool, fg_id: int
) -> int:
    pass


@policy_function()
def ist_kind_bis_6_in_familiengemeinschaft(
    alter: int, ist_kind_in_familiengemeinschaft: bool
) -> bool:
    """Child under the age of 7 in Familiengemeinschaft."""
    return ist_kind_in_familiengemeinschaft and (alter <= 6)


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_kinder_bis_6_fg(
    ist_kind_bis_6_in_familiengemeinschaft: bool, fg_id: int
) -> int:
    pass


@policy_function()
def ist_kind_bis_15_in_familiengemeinschaft(
    alter: int, ist_kind_in_familiengemeinschaft: bool
) -> bool:
    """Child under the age of 16 in Familiengemeinschaft."""
    return ist_kind_in_familiengemeinschaft and (alter <= 15)


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_kinder_bis_15_fg(
    ist_kind_bis_15_in_familiengemeinschaft: bool, fg_id: int
) -> int:
    pass


@policy_function()
def ist_kind_bis_17_in_familiengemeinschaft(
    alter: int, ist_kind_in_familiengemeinschaft: bool
) -> bool:
    """Child under the age of 18 in Familiengemeinschaft."""
    return ist_kind_in_familiengemeinschaft and (alter <= 17)


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_kinder_bis_17_fg(
    ist_kind_bis_17_in_familiengemeinschaft: bool, fg_id: int
) -> int:
    pass


@agg_by_group_function(agg_type=AggType.SUM)
def anzahl_erwachsene_fg(
    ist_erwachsener_in_familiengemeinschaft: bool, fg_id: int
) -> int:
    pass


@agg_by_group_function(agg_type=AggType.MIN)
def alter_monate_jüngstes_mitglied_fg(alter_monate: int, fg_id: int) -> float:
    pass


@policy_function(start_date="2005-01-01")
def ist_kind_in_bedarfsgemeinschaft(
    p_id_elternteil_1: IntColumn,
    p_id_elternteil_2: IntColumn,
    p_id: IntColumn,
    bg_id: IntColumn,
    xnp: ModuleType,
) -> BoolColumn:
    """Child in a Bedarfsgemeinschaft."""
    bg_id_elternteil_1 = join(
        foreign_key=p_id_elternteil_1,
        primary_key=p_id,
        target=bg_id,
        value_if_foreign_key_is_missing=-1,
        xnp=xnp,
    )
    bg_id_elternteil_2 = join(
        foreign_key=p_id_elternteil_2,
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
    return ist_kind_in_bedarfsgemeinschaft and (alter <= 17)


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_kinder_bis_17_bg(
    ist_kind_bis_17_in_bedarfsgemeinschaft: bool, bg_id: int
) -> int:
    pass


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.ANY)
def alleinerziehend_bg(alleinerziehend: bool, bg_id: int) -> bool:
    pass


@policy_function(start_date="2005-01-01")
def hat_kind_in_gleicher_bedarfsgemeinschaft(
    anzahl_kinder_bg: int,
    ist_erwachsener_in_bedarfsgemeinschaft: bool,
) -> bool:
    """Has a child in the same Bedarfsgemeinschaft."""
    return anzahl_kinder_bg >= 1 and ist_erwachsener_in_bedarfsgemeinschaft


@agg_by_group_function(agg_type=AggType.COUNT)
def anzahl_personen_sn(sn_id: int) -> int:
    pass


@agg_by_group_function(agg_type=AggType.ANY)
def alleinerziehend_sn(familie__alleinerziehend: bool, sn_id: int) -> bool:
    pass


@policy_function(vectorization_strategy="not_required")
def ist_kind_in_einstandsgemeinschaft(alter: IntColumn) -> BoolColumn:
    """Determines whether the given person is a child in a Einstandsgemeinschaft.

    The 'child' definition follows §27 SGB XII.
    """
    # TODO(@MImmesberger): This assumes that parents are part of the minor's (SGB XII)
    # Einstandsgemeinschaft. This is not necessarily true. Rewrite once we refactor SGB
    # XII.
    # https://github.com/ttsim-dev/gettsim/issues/738
    return alter <= 17


@policy_function()
def ist_erwachsener_in_einstandsgemeinschaft(
    ist_kind_in_einstandsgemeinschaft: bool,
) -> bool:
    """
    Determines whether the given person is an adult in a Einstandsgemeinschaft.

    The 'adult' definition follows §27 SGB XII.
    """
    # TODO(@MImmesberger): This assumes that parents are part of the minor's
    # Einstandsgemeinschaft. This is not necessarily true. Rewrite once we refactor SGB
    # XII.
    # https://github.com/ttsim-dev/gettsim/issues/738
    return not ist_kind_in_einstandsgemeinschaft


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_kinder_eg(ist_kind_in_einstandsgemeinschaft: bool, eg_id: int) -> int:
    pass


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_erwachsene_eg(
    ist_erwachsener_in_einstandsgemeinschaft: bool, eg_id: int
) -> int:
    pass


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.COUNT)
def anzahl_personen_eg(eg_id: int) -> int:
    pass


@agg_by_group_function(agg_type=AggType.COUNT)
def anzahl_personen_ehe(ehe_id: int) -> int:
    pass


@policy_function()
def volljährig(alter: int) -> bool:
    """Person over the age of 18."""
    return alter >= 18


@policy_function()
def ist_erwachsener_in_familiengemeinschaft(
    ist_kind_in_familiengemeinschaft: bool,
) -> bool:
    """Person is an adult in the Familengemeinschaft."""
    return not ist_kind_in_familiengemeinschaft
