"""Input columns."""

from __future__ import annotations

from gettsim.tt import FKType, policy_input


@policy_input(
    start_date="2005-01-01",
    end_date="2022-12-31",
    foreign_key_type=FKType.MUST_NOT_POINT_TO_SELF,
)
def p_id_einstandspartner() -> int:
    """Identifier of Einstandspartner."""
