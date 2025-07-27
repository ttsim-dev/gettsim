from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import AggType, agg_by_group_function, policy_function

if TYPE_CHECKING:
    from gettsim.typing import BoolColumn, IntColumn


@policy_function(vectorization_strategy="not_required")
def ist_kind_in_einstandsgemeinschaft(alter: IntColumn) -> BoolColumn:
    """Determines whether the given person is a child in a Einstandsgemeinschaft.

    The 'child' definition follows §27 SGB XII.
    """
    # TODO(@MImmesberger): This assumes that parents are part of the minor's (SGB XII)
    # Einstandsgemeinschaft. This is not necessarily true. Rewrite once we refactor SGB
    # XII.
    # https://github.com/ttsim-dev/gettsim/issues/738
    return alter <= 17  # noqa: PLR2004


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
