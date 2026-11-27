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
    """Assign tax deduction allowance for handicaped to different handicap degrees.

    Reference: § 33b Abs. 3 Satz 2 EStG idF Art. 1 G. v. 19.12.2000 BGBl. I S. 1790
    """

    return piecewise_polynomial(
        x=behinderungsgrad,
        parameters=parameter_behindertenpauschbetrag,
        xnp=xnp,
    )
