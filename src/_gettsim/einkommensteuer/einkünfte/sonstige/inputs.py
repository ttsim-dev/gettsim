"""Inputs for sonstige Einkünfte."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def alle_weiteren_y() -> float:
    """Any sonstige Einnahmen according to EStG not considered explicitly.

    Includes private and public transfers that are not yet implemented in GETTSIM
    (e.g., BAföG, Kriegsopferfürsorge).
    """
