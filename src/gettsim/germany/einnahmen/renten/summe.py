from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def summe_m(
    gesetzliche_m: float,
    sonstige_private_vorsorge_m: float,
    geförderte_private_vorsorge_m: float,
    betriebliche_altersvorsorge_m: float,
    aus_berufsständischen_versicherungen_m: float,
) -> float:
    """Sum of all Renteneinnahmen."""
    return (
        gesetzliche_m
        + sonstige_private_vorsorge_m
        + geförderte_private_vorsorge_m
        + betriebliche_altersvorsorge_m
        + aus_berufsständischen_versicherungen_m
    )
