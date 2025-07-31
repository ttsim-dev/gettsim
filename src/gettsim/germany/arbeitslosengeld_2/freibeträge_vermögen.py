"""Freibeträge für Vermögen in Arbeitslosengeld II."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import policy_function

if TYPE_CHECKING:
    from gettsim.tt import ConsecutiveIntLookupTableParamValue


# TODO(@MImmesberger): Treatment of children who live in their own BG may be wrong here.
# https://github.com/ttsim-dev/gettsim/issues/1009
@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def grundfreibetrag_vermögen(
    ist_kind_in_bedarfsgemeinschaft: bool,
    alter: int,
    geburtsjahr: int,
    maximaler_grundfreibetrag_vermögen: float,
    vermögensgrundfreibetrag_je_lebensjahr: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Wealth exemptions based on individuals age."""
    if not ist_kind_in_bedarfsgemeinschaft:
        out = vermögensgrundfreibetrag_je_lebensjahr.look_up(geburtsjahr) * alter
    else:
        out = 0.0
    return min(out, maximaler_grundfreibetrag_vermögen)


# TODO(@MImmesberger): Treatment of children who live in their own BG may be wrong here.
# https://github.com/ttsim-dev/gettsim/issues/1009
@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def maximaler_grundfreibetrag_vermögen(
    geburtsjahr: int,
    ist_kind_in_bedarfsgemeinschaft: bool,
    obergrenze_vermögensgrundfreibetrag: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Maximal wealth exemptions by year of birth."""
    if ist_kind_in_bedarfsgemeinschaft:
        return 0.0
    else:
        return obergrenze_vermögensgrundfreibetrag.look_up(geburtsjahr)


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
    """Actual exemptions until 2022."""
    return (
        grundfreibetrag_vermögen_bg
        + anzahl_kinder_bis_17_bg * vermögensgrundfreibetrag_je_kind
        + anzahl_personen_bg * vermögensfreibetrag_austattung
    )
