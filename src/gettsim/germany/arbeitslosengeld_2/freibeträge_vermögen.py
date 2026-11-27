"""Freibeträge für Vermögen in Arbeitslosengeld II."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import TTSIMUnit, policy_function

if TYPE_CHECKING:
    from gettsim.tt import ConsecutiveIntLookupTableParamValue


# TODO(@MImmesberger): Treatment of children who live in their own BG may be wrong here.
# https://github.com/ttsim-dev/gettsim/issues/1009
@policy_function(
    start_date="2005-01-01", end_date="2022-12-31", unit=TTSIMUnit.CURRENCY
)
def grundfreibetrag_vermögen(
    familie__ist_kind_in_bedarfsgemeinschaft: bool,
    alter: int,
    geburtsjahr: int,
    maximaler_grundfreibetrag_vermögen: float,
    vermögensgrundfreibetrag_je_lebensjahr: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Wealth exemptions based on individuals age.

    Reference:
        - § 12 Abs. 2 Nr. 1 SGB II idF Art. 2 G. v. 19.11.2004 BGBl. I S. 2902
        - § 65 Abs. 5 SGB II idF Art. 1 G. v. 24.12.2003 BGBl. I S. 2954
        - § 12 Abs. 2 Nr. 1 SGB II idF Art. 1 G. v. 20.07.2006 BGBl. I S. 1706
        - § 65 Abs. 5 SGB II idF Art. 1 G. v. 20.07.2006 BGBl. I S. 1706
        - § 12 Abs. 2 Satz 1 Nr. 1 SGB II idF Art. 2 G. v. 20.04.2007 BGBl. I S. 554
        - § 12 Abs. 2 Satz 1 Nr. 1 SGB II idF Art. 2 G. v. 24.03.2011 BGBl. I S. 453
    """
    if not familie__ist_kind_in_bedarfsgemeinschaft:
        out = vermögensgrundfreibetrag_je_lebensjahr.look_up(geburtsjahr) * alter
    else:
        out = 0.0
    return min(out, maximaler_grundfreibetrag_vermögen)


# TODO(@MImmesberger): Treatment of children who live in their own BG may be wrong here.
# https://github.com/ttsim-dev/gettsim/issues/1009
@policy_function(
    start_date="2005-01-01", end_date="2022-12-31", unit=TTSIMUnit.CURRENCY
)
def maximaler_grundfreibetrag_vermögen(
    geburtsjahr: int,
    familie__ist_kind_in_bedarfsgemeinschaft: bool,
    obergrenze_vermögensgrundfreibetrag: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Maximal wealth exemptions by year of birth.

    Reference:
        - § 12 Abs. 2 Nr. 1 SGB II idF Art. 2 G. v. 19.11.2004 BGBl. I S. 2902
        - § 65 Abs. 5 SGB II idF Art. 1 G. v. 24.12.2003 BGBl. I S. 2954
        - § 12 Abs. 2 Nr. 1 SGB II idF Art. 1 G. v. 20.07.2006 BGBl. I S. 1706
        - § 65 Abs. 5 SGB II idF Art. 1 G. v. 20.07.2006 BGBl. I S. 1706
        - § 12 Abs. 2 Satz 2 SGB II idF Art. 2 G. v. 20.04.2007 BGBl. I S. 554
    """
    if familie__ist_kind_in_bedarfsgemeinschaft:
        return 0.0
    else:
        return obergrenze_vermögensgrundfreibetrag.look_up(geburtsjahr)


@policy_function(
    start_date="2005-01-01",
    end_date="2022-12-31",
    unit=TTSIMUnit.CURRENCY.PER_BG,
)
def vermögensfreibetrag_bg(
    grundfreibetrag_vermögen_bg: float,
    familie__anzahl_kinder_bis_17_bg: int,
    familie__anzahl_personen_bg: int,
    vermögensfreibetrag_austattung: float,
    vermögensgrundfreibetrag_je_kind: float,
) -> float:
    """Actual exemptions until 2022.

    Reference:
        - § 12 Abs. 2 SGB II idF Art. 2 G. v. 19.11.2004 BGBl. I S. 2902
        - § 12 Abs. 2 Nr. 4 SGB II idF Art. 1 G. v. 24.12.2003 BGBl. I S. 2954
        - § 12 Abs. 2 SGB II idF Art. 1 G. v. 20.07.2006 BGBl. I S. 1706
        - § 12 Abs. 2 Satz 1 SGB II idF Art. 2 G. v. 24.03.2011 BGBl. I S. 453
    """
    return (
        grundfreibetrag_vermögen_bg
        + familie__anzahl_kinder_bis_17_bg * vermögensgrundfreibetrag_je_kind
        + familie__anzahl_personen_bg * vermögensfreibetrag_austattung
    )
