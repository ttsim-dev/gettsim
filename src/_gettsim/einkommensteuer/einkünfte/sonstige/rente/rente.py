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
    sozialversicherung__rente__altersrente__betrag_m: float,
    sozialversicherung__rente__erwerbsminderung__betrag_m: float,
    geförderte_private_vorsorge_m: float,
    sonstige_private_vorsorge_m: float,
    betriebliche_altersvorsorge_m: float,
) -> float:
    """Pension income counting towards taxable income.

    Reference: § 22 EStG
    """
    return (
        ertragsanteil
        * (
            sozialversicherung__rente__altersrente__betrag_m
            + sozialversicherung__rente__erwerbsminderung__betrag_m
            + sonstige_private_vorsorge_m
        )
        + betriebliche_altersvorsorge_m
        + geförderte_private_vorsorge_m
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
