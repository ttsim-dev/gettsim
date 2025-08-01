"""Freibeträge für Vermögen in Bürgergeld."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(start_date="2023-01-01")
def vermögensfreibetrag_in_karenzzeit_bg(
    familie__anzahl_personen_bg: int,
    vermögensfreibetrag_je_person_nach_karenzzeit: dict[str, float],
) -> float:
    """Wealth exemptions during Karenzzeit.

    This variable is also reffered to as 'erhebliches Vermögen'."""
    return (
        vermögensfreibetrag_je_person_nach_karenzzeit["während_karenzzeit"]
        + (familie__anzahl_personen_bg - 1)
        * vermögensfreibetrag_je_person_nach_karenzzeit["normaler_satz"]
    )


@policy_function(start_date="2023-01-01", leaf_name="vermögensfreibetrag_bg")
def vermögensfreibetrag_bg_ab_2023(
    familie__anzahl_personen_bg: int,
    vermögensfreibetrag_in_karenzzeit_bg: float,
    bezug_im_vorjahr: bool,
    vermögensfreibetrag_je_person_nach_karenzzeit: dict[str, float],
) -> float:
    """Actual wealth exemptions.

    During the first year (Karenzzeit), the wealth exemption is substantially larger."""
    if bezug_im_vorjahr:
        out = (
            familie__anzahl_personen_bg
            * vermögensfreibetrag_je_person_nach_karenzzeit["normaler_satz"]
        )
    else:
        out = vermögensfreibetrag_in_karenzzeit_bg

    return out
