"""Tax allowances for single parents."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, cast_unit, policy_function


@policy_function(
    end_date="2014-12-31",
    leaf_name="alleinerziehend_betrag_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def alleinerziehend_betrag_y_pauschal(
    familie__alleinerziehend_sn: bool,
    alleinerziehendenfreibetrag_basis: float,
) -> float:
    """Calculate tax deduction allowance for single parents until 2014"""
    return alleinerziehendenfreibetrag_basis if familie__alleinerziehend_sn else 0.0


@policy_function(
    start_date="2015-01-01",
    leaf_name="alleinerziehend_betrag_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def alleinerziehend_betrag_y_nach_kinderzahl(
    familie__alleinerziehend_sn: bool,
    kindergeld__anzahl_ansprüche_sn: int,
    alleinerziehendenfreibetrag_basis: float,
    alleinerziehendenfreibetrag_zusatz_pro_kind: float,
) -> float:
    """Calculate tax deduction allowance for single parents since 2015."""
    if familie__alleinerziehend_sn:
        out = (
            alleinerziehendenfreibetrag_basis
            + (cast_unit(kindergeld__anzahl_ansprüche_sn, TTSIMUnit.DIMENSIONLESS) - 1)
            * alleinerziehendenfreibetrag_zusatz_pro_kind
        )
    else:
        out = 0.0

    return out
