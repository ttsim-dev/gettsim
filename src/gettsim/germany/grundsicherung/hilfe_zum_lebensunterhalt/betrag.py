"""Hilfe zum Lebensunterhalt (§§ 27-40 SGB XII, Drittes Kapitel).

Not yet implemented. See https://github.com/ttsim-dev/gettsim/issues/1153
"""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(
    start_date="2005-01-01",
    fail_msg_if_included=(
        "Hilfe zum Lebensunterhalt (Drittes Kapitel SGB XII) is not yet implemented. "
        "See https://github.com/ttsim-dev/gettsim/issues/1153"
    ),
)
def betrag_m() -> float:
    """Hilfe zum Lebensunterhalt benefit per person.

    Covers minor children in Einsatzgemeinschaften where the adults receive
    Grundsicherung im Alter (Viertes Kapitel SGB XII). The children's needs are computed
    jointly with the parents' (kopfteilige KdU, Regelbedarfsstufen), but the benefit is
    legally separate (§ 19 Abs. 1, 2 SGB XII).

    Reference: §§ 27-40 SGB XII
    """
    return 0.0
