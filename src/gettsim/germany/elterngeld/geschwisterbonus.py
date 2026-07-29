"""Geschwisterbonus for Elterngeld."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, cast_ttsim_unit, policy_function


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_FG)
def geschwisterbonus_m_fg(
    basisbetrag_m: float,
    geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg: bool,
    geschwisterbonus_aufschlag: float,
    geschwisterbonus_minimum_m_fg: float,
) -> float:
    """Elterngeld bonus for (older) siblings.

    According to § 2a parents of siblings get a bonus.
    """
    if geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg:
        out = max(
            geschwisterbonus_aufschlag
            * cast_ttsim_unit(basisbetrag_m, unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_FG),
            geschwisterbonus_minimum_m_fg,
        )
    else:
        out = 0.0
    return out


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_FG)
def mehrlingsbonus_m_fg(
    anzahl_mehrlinge_fg: int, mehrlingsbonus_pro_kind_m: float
) -> float:
    """Elterngeld bonus for multiples."""
    return anzahl_mehrlinge_fg * mehrlingsbonus_pro_kind_m


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.DIMENSIONLESS.PER_FG)
def geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg(
    familie__anzahl_kinder_bis_2_fg: int,
    familie__anzahl_kinder_bis_5_fg: int,
    geschwisterbonus_altersgrenzen: dict[int, int],
) -> bool:
    """Siblings that give rise to Elterngeld siblings bonus."""
    geschwister_unter_3 = (
        familie__anzahl_kinder_bis_2_fg >= geschwisterbonus_altersgrenzen[3]
    )
    geschwister_unter_6 = (
        familie__anzahl_kinder_bis_5_fg >= geschwisterbonus_altersgrenzen[6]
    )

    return geschwister_unter_3 or geschwister_unter_6


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.DIMENSIONLESS.PER_FG)
def anzahl_mehrlinge_fg(
    anzahl_mehrlinge_jüngstes_kind_fg: int,
) -> int:
    """Number of multiples of the youngest child."""
    out = anzahl_mehrlinge_jüngstes_kind_fg - cast_ttsim_unit(
        1, unit=TTSIMUnit.DIMENSIONLESS.PER_FG
    )
    return max(out, 0)
