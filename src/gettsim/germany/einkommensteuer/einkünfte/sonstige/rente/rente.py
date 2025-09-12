"""Sonstige Einkünfte according to § 22 EStG."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.tt import (
        ConsecutiveIntLookupTableParamValue,
        PiecewisePolynomialParamValue,
    )

from gettsim.tt import (
    piecewise_polynomial,
    policy_function,
)


@policy_function(end_date="2004-12-31", leaf_name="betrag_m")
def betrag_m_besteuerung_gesetzliche_rente_nach_ertragsanteil(
    ertragsanteil: float,
    einnahmen__renten__gesetzliche_m: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
    einnahmen__renten__aus_berufsständischen_versicherungen_m: float,
) -> float:
    """Pension income counting towards taxable income."""
    return (
        ertragsanteil
        * (
            einnahmen__renten__gesetzliche_m
            + einnahmen__renten__aus_berufsständischen_versicherungen_m
            + einnahmen__renten__sonstige_private_vorsorge_m
        )
        + einnahmen__renten__betriebliche_altersvorsorge_m
        + einnahmen__renten__geförderte_private_vorsorge_m
    )


@policy_function(start_date="2005-01-01", leaf_name="betrag_m")
def betrag_m_besteuerung_gesetzliche_rente_nach_besteuerungsanteil(
    besteuerungsanteil: float,
    ertragsanteil: float,
    einnahmen__renten__gesetzliche_m: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
    einnahmen__renten__aus_berufsständischen_versicherungen_m: float,
) -> float:
    """Pension income counting towards taxable income.

    Reference: § 22 Nr. 1 Satz 3 Buchstabe a Doppelbuchstabe aa EStG
    """
    return (
        besteuerungsanteil
        * (
            einnahmen__renten__gesetzliche_m
            + einnahmen__renten__sonstige_private_vorsorge_m
            + einnahmen__renten__aus_berufsständischen_versicherungen_m
        )
        + ertragsanteil * einnahmen__renten__sonstige_private_vorsorge_m
        + einnahmen__renten__betriebliche_altersvorsorge_m
        + einnahmen__renten__geförderte_private_vorsorge_m
    )


@policy_function()
def ertragsanteil(
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    parameter_ertragsanteil: ConsecutiveIntLookupTableParamValue,
    xnp: ModuleType,
) -> float:
    """Ertragsanteil."""
    return parameter_ertragsanteil.look_up(
        xnp.floor(sozialversicherung__rente__alter_bei_renteneintritt).astype(int),
    )


@policy_function(start_date="2005-01-01")
def besteuerungsanteil(
    sozialversicherung__rente__jahr_renteneintritt: int,
    parameter_besteuerungsanteil: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Share of pensions subject to income taxation."""
    return piecewise_polynomial(
        x=sozialversicherung__rente__jahr_renteneintritt,
        parameters=parameter_besteuerungsanteil,
        xnp=xnp,
    )
