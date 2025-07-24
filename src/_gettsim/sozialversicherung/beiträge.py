"""Social insurance contributions."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def beiträge_versicherter_m(
    pflege__beitrag__betrag_versicherter_m: float,
    kranken__beitrag__betrag_versicherter_m: float,
    rente__beitrag__betrag_versicherter_m: float,
    arbeitslosen__beitrag__betrag_versicherter_m: float,
) -> float:
    """Sum of social insurance contributions paid by the insured person."""
    return (
        pflege__beitrag__betrag_versicherter_m
        + kranken__beitrag__betrag_versicherter_m
        + rente__beitrag__betrag_versicherter_m
        + arbeitslosen__beitrag__betrag_versicherter_m
    )


@policy_function()
def beiträge_arbeitgeber_m(
    pflege__beitrag__betrag_arbeitgeber_m: float,
    kranken__beitrag__betrag_arbeitgeber_m: float,
    rente__beitrag__betrag_arbeitgeber_m: float,
    arbeitslosen__beitrag__betrag_arbeitgeber_m: float,
) -> float:
    """Sum of employer's social insurance contributions."""
    return (
        pflege__beitrag__betrag_arbeitgeber_m
        + kranken__beitrag__betrag_arbeitgeber_m
        + rente__beitrag__betrag_arbeitgeber_m
        + arbeitslosen__beitrag__betrag_arbeitgeber_m
    )


@policy_function()
def beiträge_gesamt_m(
    beiträge_versicherter_m: float,
    beiträge_arbeitgeber_m: float,
) -> float:
    """Sum of employer's and insured person's social insurance contributions."""
    return beiträge_versicherter_m + beiträge_arbeitgeber_m
