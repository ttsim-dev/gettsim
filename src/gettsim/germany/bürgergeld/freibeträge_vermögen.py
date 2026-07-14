"""Freibeträge für Vermögen in Bürgergeld."""

from __future__ import annotations

from gettsim.tt import Unit, policy_function, cast_unit


@policy_function(start_date="2023-01-01", unit=Unit.CURRENCY.PER_BG)
def vermögensfreibetrag_in_karenzzeit_bg(
    familie__anzahl_personen_bg: int,
    vermögensfreibetrag_je_person_nach_karenzzeit: dict[str, float],
) -> float:
    """Wealth exemptions during Karenzzeit.

    This variable is also referred to as 'erhebliches Vermögen'.
    """
    # Per-person exemptions sum to the BG-level total wealth exemption.
    return cast_unit(
        vermögensfreibetrag_je_person_nach_karenzzeit["während_karenzzeit"]
        + (cast_unit(familie__anzahl_personen_bg, Unit.DIMENSIONLESS) - 1)
        * vermögensfreibetrag_je_person_nach_karenzzeit["normaler_satz"],
        Unit.CURRENCY.PER_BG,
    )


@policy_function(
    start_date="2023-01-01",
    leaf_name="vermögensfreibetrag_bg",
    unit=Unit.CURRENCY.PER_BG,
)
def vermögensfreibetrag_bg_ab_2023(
    familie__anzahl_personen_bg: int,
    vermögensfreibetrag_in_karenzzeit_bg: float,
    bezug_im_vorjahr: bool,
    vermögensfreibetrag_je_person_nach_karenzzeit: dict[str, float],
) -> float:
    """Actual wealth exemptions.

    During the first year (Karenzzeit), the wealth exemption is substantially larger.
    """
    if bezug_im_vorjahr:
        out = (
            familie__anzahl_personen_bg
            * vermögensfreibetrag_je_person_nach_karenzzeit["normaler_satz"]
        )
    else:
        out = vermögensfreibetrag_in_karenzzeit_bg

    return out
