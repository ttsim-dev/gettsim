"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input(start_date="2023-01-01")
def bezug_im_vorjahr() -> bool:
    """Person received Bürgergeld in the last 12 months."""
