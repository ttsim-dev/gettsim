from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def gesetzliche_m(
    sozialversicherung__rente__altersrente__betrag_m: float,
    sozialversicherung__rente__erwerbsminderung__betrag_m: float,
) -> float:
    """Monthly income from social security pension."""
    return (
        sozialversicherung__rente__altersrente__betrag_m
        + sozialversicherung__rente__erwerbsminderung__betrag_m
    )
