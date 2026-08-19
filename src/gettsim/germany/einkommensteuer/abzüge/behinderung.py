"""Tax allowances for the disabled."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    TTSIMUnit,
    piecewise_polynomial,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def pauschbetrag_behinderung_y(
    behinderungsgrad: int,
    parameter_behindertenpauschbetrag: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Assign tax deduction allowance for handicaped to different handicap degrees."""
    return piecewise_polynomial(
        x=behinderungsgrad,
        parameters=parameter_behindertenpauschbetrag,
        xnp=xnp,
    )
