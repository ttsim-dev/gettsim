"""Hilfe zum Lebensunterhalt (SGB XII Kap. 3)."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(
    fail_msg_if_included="Hilfe zum Lebensunterhalt (SGB XII Kap. 3) is not implemented"
    " yet, see https://github.com/ttsim-dev/gettsim/issues/1153",
)
def betrag_m() -> float:
    """Hilfe zum Lebensunterhalt per person (§27 ff. SGB XII).

    Covers the livelihood of persons who are not eligible for Grundsicherung im Alter
    und bei Erwerbsminderung (SGB XII Kap. 4), in particular children whose parents
    receive Grundsicherung.

    # TODO (@MImmesberger): Implement Hilfe zum Lebensunterhalt.
    # https://github.com/ttsim-dev/gettsim/issues/1153
    """
    return 0.0


@policy_function(start_date="2005-01-01")
def überschusseinkommen_m(
    kindergeld__betrag_m: float,
) -> float:
    """Excess HzL income flowing to the parent's Grundsicherung im Alter.

    For now, this returns the child's Kindergeld as a simplified proxy for the child's
    excess income. Once Hilfe zum Lebensunterhalt is fully implemented, this should be
    computed from the child's ungedeckter Bedarf and einkommen_zur_verteilung.

    # TODO (@MImmesberger): Compute from full HzL Bedarf/Einkommen once implemented.
    # https://github.com/ttsim-dev/gettsim/issues/1153
    """
    return kindergeld__betrag_m
