"""Input columns."""

from __future__ import annotations

from gettsim.tt import AggType, FKType, agg_by_group_function, policy_input


@policy_input()
def alleinerziehend() -> bool:
    """Single parent."""


@agg_by_group_function(agg_type=AggType.ANY, end_date="2008-12-31")
def alleinerziehend_fg(alleinerziehend: bool, fg_id: int) -> bool:
    """Only used for Erziehungsgeld and even there it might be wrong."""


@policy_input(foreign_key_type=FKType.MUST_NOT_POINT_TO_SELF)
def p_id_ehepartner() -> int:
    """Identifier of married partner."""


@policy_input(foreign_key_type=FKType.MUST_NOT_POINT_TO_SELF)
def p_id_elternteil_1() -> int:
    """Identifier of the first parent."""


@policy_input(foreign_key_type=FKType.MUST_NOT_POINT_TO_SELF)
def p_id_elternteil_2() -> int:
    """Identifier of the second parent."""
