from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(
    end_date="2004-12-31",
    leaf_name="betrag_gesamt_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_gesamt_m_ohne_basisrente(
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


@policy_function(
    start_date="2005-01-01",
    leaf_name="betrag_gesamt_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_gesamt_m_mit_basisrente(
    gesetzliche_m: float,
    basisrente_m: float,
    sonstige_private_vorsorge_m: float,
    geförderte_private_vorsorge_m: float,
    betriebliche_altersvorsorge_m: float,
    aus_berufsständischen_versicherungen_m: float,
) -> float:
    """Sum of all Renteneinnahmen.

    Basisrente / Rürup did not exist before the Alterseinkünftegesetz took effect on
    2005-01-01.
    """
    return (
        gesetzliche_m
        + basisrente_m
        + sonstige_private_vorsorge_m
        + geförderte_private_vorsorge_m
        + betriebliche_altersvorsorge_m
        + aus_berufsständischen_versicherungen_m
    )
