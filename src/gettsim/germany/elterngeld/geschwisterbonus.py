"""Geschwisterbonus for Elterngeld."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(start_date="2007-01-01")
def geschwisterbonus_m(
    basisbetrag_m: float,
    geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg: bool,
    geschwisterbonus_aufschlag: float,
    geschwisterbonus_minimum: float,
) -> float:
    """Elterngeld bonus for (older) siblings.

    According to § 2a parents of siblings get a bonus.
    """
    if geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg:
        out = max(
            geschwisterbonus_aufschlag * basisbetrag_m,
            geschwisterbonus_minimum,
        )
    else:
        out = 0.0
    return out


@policy_function(start_date="2007-01-01")
def mehrlingsbonus_m(anzahl_mehrlinge_fg: int, mehrlingsbonus_pro_kind: float) -> float:
    """Elterngeld bonus for multiples."""
    return anzahl_mehrlinge_fg * mehrlingsbonus_pro_kind


@policy_function(start_date="2007-01-01")
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


@policy_function(start_date="2007-01-01")
def anzahl_mehrlinge_fg(
    anzahl_mehrlinge_jüngstes_kind_fg: int,
) -> int:
    """Number of multiples of the youngest child."""
    out = anzahl_mehrlinge_jüngstes_kind_fg - 1
    return max(out, 0)
