from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def alter_bis_24(alter: int) -> bool:
    """Age is 24 years at most.

    Trivial, but necessary in order to use the target for aggregation.
    """
    return alter <= 24  # noqa: PLR2004
