"""Input columns."""

from __future__ import annotations

from gettsim.tt import FKType, policy_input


@policy_input(start_date="2023-01-01")
def bezug_im_vorjahr() -> bool:
    """Person received Bürgergeld in the last 12 months."""


@policy_input(start_date="2023-01-01", foreign_key_type=FKType.MUST_NOT_POINT_TO_SELF)
def p_id_einstandspartner() -> int:
    """Identifier of Einstandspartner."""
