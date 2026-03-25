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
