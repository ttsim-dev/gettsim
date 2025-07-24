"""Priority checks of transfers against each other."""

from __future__ import annotations

from gettsim.tt import AggType, agg_by_group_function, policy_function


@agg_by_group_function(agg_type=AggType.ANY)
def wohngeld_vorrang_wthh(
    wohngeld_vorrang_vor_arbeitslosengeld_2_bg: bool,
    wthh_id: int,
) -> bool:
    pass


@agg_by_group_function(agg_type=AggType.ANY)
def wohngeld_kinderzuschlag_vorrang_wthh(
    wohngeld_und_kinderzuschlag_vorrang_vor_arbeitslosengeld_2_bg: bool,
    wthh_id: int,
) -> bool:
    pass


@policy_function()
def wohngeld_vorrang_vor_arbeitslosengeld_2_bg(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    arbeitslosengeld_2__anzurechnendes_einkommen_m_bg: float,
    wohngeld__anspruchshöhe_m_bg: float,
) -> bool:
    """Check if housing benefit has priority.

    Housing benefit has priority if the sum of housing benefit and income covers the
    needs according to SGB II of the Bedarfsgemeinschaft.
    """
    return (
        arbeitslosengeld_2__anzurechnendes_einkommen_m_bg + wohngeld__anspruchshöhe_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg
    )


@policy_function()
def kinderzuschlag_vorrang_vor_arbeitslosengeld_2_bg(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    arbeitslosengeld_2__anzurechnendes_einkommen_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
) -> bool:
    """Check if child benefit has priority."""
    return (
        arbeitslosengeld_2__anzurechnendes_einkommen_m_bg
        + kinderzuschlag__anspruchshöhe_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg
    )


@policy_function()
def wohngeld_und_kinderzuschlag_vorrang_vor_arbeitslosengeld_2_bg(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    arbeitslosengeld_2__anzurechnendes_einkommen_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
    wohngeld__anspruchshöhe_m_bg: float,
) -> bool:
    """Check if housing and child benefit have priority."""
    return (
        arbeitslosengeld_2__anzurechnendes_einkommen_m_bg
        + wohngeld__anspruchshöhe_m_bg
        + kinderzuschlag__anspruchshöhe_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg
    )
