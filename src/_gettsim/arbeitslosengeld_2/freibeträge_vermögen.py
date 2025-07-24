"""Freibeträge für Vermögen in Arbeitslosengeld II."""

from __future__ import annotations

from gettsim.tt import policy_function


# TODO(@MImmesberger): Treatment of children who live in their own BG may be wrong here.
# https://github.com/ttsim-dev/gettsim/issues/1009
@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def grundfreibetrag_vermögen(
    ist_kind_in_bedarfsgemeinschaft: bool,
    alter: int,
    geburtsjahr: int,
    maximaler_grundfreibetrag_vermögen: float,
    vermögensgrundfreibetrag_je_lebensjahr: dict[int, float],
) -> float:
    """Calculate wealth exemptions based on individuals age.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    """
    threshold_years = list(vermögensgrundfreibetrag_je_lebensjahr.keys())
    if geburtsjahr <= threshold_years[0]:
        out = next(iter(vermögensgrundfreibetrag_je_lebensjahr.values())) * alter
    elif (geburtsjahr >= threshold_years[1]) and (not ist_kind_in_bedarfsgemeinschaft):
        out = list(vermögensgrundfreibetrag_je_lebensjahr.values())[1] * alter
    else:
        out = 0.0

    return min(out, maximaler_grundfreibetrag_vermögen)


# TODO(@MImmesberger): Parameter should be defined as a piecewise_constant.
# https://github.com/ttsim-dev/gettsim/issues/911
# TODO(@MImmesberger): Treatment of children who live in their own BG may be wrong here.
# https://github.com/ttsim-dev/gettsim/issues/1009
@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def maximaler_grundfreibetrag_vermögen(
    geburtsjahr: int,
    ist_kind_in_bedarfsgemeinschaft: bool,
    obergrenze_vermögensgrundfreibetrag: dict[int, float],
) -> float:
    """Calculate maximal wealth exemptions by year of birth.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    """
    threshold_years = list(obergrenze_vermögensgrundfreibetrag.keys())
    obergrenzen = list(obergrenze_vermögensgrundfreibetrag.values())
    if ist_kind_in_bedarfsgemeinschaft:
        out = 0.0
    else:
        if geburtsjahr < threshold_years[1]:
            out = obergrenzen[0]
        elif geburtsjahr < threshold_years[2]:
            out = obergrenzen[1]
        elif geburtsjahr < threshold_years[3]:
            out = obergrenzen[2]
        else:
            out = obergrenzen[3]

    return out


@policy_function(start_date="2023-01-01")
def vermögensfreibetrag_in_karenzzeit_bg(
    anzahl_personen_bg: int,
    vermögensfreibetrag_je_person_nach_karenzzeit: dict[str, float],
) -> float:
    """Calculate wealth exemptions since 2023 during Karenzzeit. This variable is also
    reffered to as 'erhebliches Vermögen'.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    """
    return (
        vermögensfreibetrag_je_person_nach_karenzzeit["während_karenzzeit"]
        + (anzahl_personen_bg - 1)
        * vermögensfreibetrag_je_person_nach_karenzzeit["normaler_satz"]
    )


@policy_function(
    start_date="2005-01-01",
    end_date="2022-12-31",
    leaf_name="vermögensfreibetrag_bg",
)
def vermögensfreibetrag_bg_bis_2022(
    grundfreibetrag_vermögen_bg: float,
    anzahl_kinder_bis_17_bg: int,
    anzahl_personen_bg: int,
    vermögensfreibetrag_austattung: float,
    vermögensgrundfreibetrag_je_kind: float,
) -> float:
    """Calculate actual exemptions until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    """
    return (
        grundfreibetrag_vermögen_bg
        + anzahl_kinder_bis_17_bg * vermögensgrundfreibetrag_je_kind
        + anzahl_personen_bg * vermögensfreibetrag_austattung
    )


@policy_function(start_date="2023-01-01", leaf_name="vermögensfreibetrag_bg")
def vermögensfreibetrag_bg_ab_2023(
    anzahl_personen_bg: int,
    vermögensfreibetrag_in_karenzzeit_bg: float,
    bezug_im_vorjahr: bool,
    vermögensfreibetrag_je_person_nach_karenzzeit: dict[str, float],
) -> float:
    """Calculate actual wealth exemptions since 2023.

    During the first year (Karenzzeit), the wealth exemption is substantially larger.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    """
    if bezug_im_vorjahr:
        out = (
            anzahl_personen_bg
            * vermögensfreibetrag_je_person_nach_karenzzeit["normaler_satz"]
        )
    else:
        out = vermögensfreibetrag_in_karenzzeit_bg

    return out
