"""Sonstige Einkünfte according to § 22 EStG."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    piecewise_polynomial,
    policy_function,
)


@policy_function()
def betrag_m(
    ertragsanteil: float,
    einnahmen__renten__gesetzliche_m: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
) -> float:
    """Pension income counting towards taxable income.

    Reference: § 22 EStG
    """
    return (
        ertragsanteil
        * (
            einnahmen__renten__gesetzliche_m
            + einnahmen__renten__sonstige_private_vorsorge_m
        )
        + einnahmen__renten__betriebliche_altersvorsorge_m
        + einnahmen__renten__geförderte_private_vorsorge_m
    )


@policy_function()
def ertragsanteil(
    sozialversicherung__rente__jahr_renteneintritt: int,
    parameter_ertragsanteil: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Share of pensions subject to income taxation."""
    return piecewise_polynomial(
        x=sozialversicherung__rente__jahr_renteneintritt,
        parameters=parameter_ertragsanteil,
        xnp=xnp,
    )
