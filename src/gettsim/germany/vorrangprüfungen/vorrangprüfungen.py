"""Priority and favorability checks of transfers against each other."""

from __future__ import annotations

from gettsim.germany import WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC
from gettsim.tt import TTSIMUnit, cast_unit, policy_function


@policy_function(
    leaf_name="wohngeld_kinderzuschlag_vorrangig_oder_günstiger",
    end_date="2022-12-31",
    warn_msg_if_included=WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC,
    unit=TTSIMUnit.DIMENSIONLESS,
)
def wohngeld_kinderzuschlag_vorrangig_oder_günstiger_bis_2022(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    arbeitslosengeld_2__anzurechnendes_einkommen_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
    wohngeld__anspruchshöhe_m_wthh: float,
) -> bool:
    """Wohngeld/Kinderzuschlag is more favorable than ALG II.

    Note that this check assumes WTHH=BG; it will not work in more complex situations.
    When calculating `wthh_id` and `bg_id` using the serious implementation in [link],
    you will need to replace this function, too.
    """
    # TODO (@MImmesberger): Vorrangprüfung probably not precise for SGB XII households.
    # https://github.com/ttsim-dev/gettsim/issues/1165
    # The check assumes WTHH = BG, so compare BG-level resources against the BG need.
    return cast_unit(
        arbeitslosengeld_2__anzurechnendes_einkommen_m_bg
        + cast_unit(wohngeld__anspruchshöhe_m_wthh, TTSIMUnit.CURRENCY.PER_MONTH.PER_BG)
        + kinderzuschlag__anspruchshöhe_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg,
        TTSIMUnit.DIMENSIONLESS,
    )


@policy_function(
    leaf_name="wohngeld_kinderzuschlag_vorrangig_oder_günstiger",
    start_date="2023-01-01",
    warn_msg_if_included=WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC,
    unit=TTSIMUnit.DIMENSIONLESS,
)
def wohngeld_kinderzuschlag_vorrangig_oder_günstiger_ab_2023(
    bürgergeld__regelbedarf_m_bg: float,
    bürgergeld__anzurechnendes_einkommen_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
    wohngeld__anspruchshöhe_m_wthh: float,
) -> bool:
    """Wohngeld/Kinderzuschlag is more favorable than Bürgergeld.

    Note that this check assumes WTHH=BG; it will not work in more complex situations.
    When calculating `wthh_id` and `bg_id` using the serious implementation in [link],
    you will need to replace this function, too.
    """
    # TODO (@MImmesberger): Vorrangprüfung probably not precise for SGB XII households.
    # https://github.com/ttsim-dev/gettsim/issues/1165
    # The check assumes WTHH = BG, so compare BG-level resources against the BG need.
    return cast_unit(
        bürgergeld__anzurechnendes_einkommen_m_bg
        + cast_unit(wohngeld__anspruchshöhe_m_wthh, TTSIMUnit.CURRENCY.PER_MONTH.PER_BG)
        + kinderzuschlag__anspruchshöhe_m_bg
        >= bürgergeld__regelbedarf_m_bg,
        TTSIMUnit.DIMENSIONLESS,
    )
