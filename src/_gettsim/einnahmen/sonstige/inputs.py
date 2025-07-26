"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def alle_weiteren_m() -> float:
    """Additional sonstige Einnahmen according to EStG (excl. pensions).

    Includes private and public transfers that are not yet implemented in GETTSIM
    (e.g., BAföG, Kriegsopferfürsorge).
    """
