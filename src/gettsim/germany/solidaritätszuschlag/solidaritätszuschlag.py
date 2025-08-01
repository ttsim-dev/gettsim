"""Solidarity Surcharge (Solidaritätszuschlag)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    piecewise_polynomial,
    policy_function,
)


def solidaritätszuschlagstarif(
    steuer_pro_person: float,
    familie__anzahl_personen_sn: int,
    parameter_solidaritätszuschlag: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """The isolated function for Solidaritätszuschlag."""
    return familie__anzahl_personen_sn * piecewise_polynomial(
        x=steuer_pro_person / familie__anzahl_personen_sn,
        parameters=parameter_solidaritätszuschlag,
        xnp=xnp,
    )


@policy_function(end_date="2008-12-31", leaf_name="betrag_y_sn")
def betrag_y_sn_ohne_abgelt_st(
    einkommensteuer__betrag_mit_kinderfreibetrag_y_sn: float,
    familie__anzahl_personen_sn: int,
    parameter_solidaritätszuschlag: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Calculate the Solidarity Surcharge on Steuernummer level.

    Solidaritätszuschlaggesetz (SolZG) in 1991 and 1992.
    Solidaritätszuschlaggesetz 1995 (SolZG 1995) since 1995.

    The Solidarity Surcharge is an additional tax on top of the income tax which
    is the tax base. As opposed to the 'standard' income tax, child allowance is
    always deducted for tax base calculation.

    There is also Solidarity Surcharge on the Capital Income Tax, but always
    with Solidarity Surcharge tax rate and no tax exempt level. §3 (3) S.2
    SolzG 1995.

    """
    return solidaritätszuschlagstarif(
        steuer_pro_person=einkommensteuer__betrag_mit_kinderfreibetrag_y_sn,
        familie__anzahl_personen_sn=familie__anzahl_personen_sn,
        parameter_solidaritätszuschlag=parameter_solidaritätszuschlag,
        xnp=xnp,
    )


@policy_function(start_date="2009-01-01", leaf_name="betrag_y_sn")
def betrag_y_sn_mit_abgelt_st(
    einkommensteuer__betrag_mit_kinderfreibetrag_y_sn: float,
    familie__anzahl_personen_sn: int,
    einkommensteuer__abgeltungssteuer__betrag_y_sn: float,
    parameter_solidaritätszuschlag: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Calculate the Solidarity Surcharge on Steuernummer level.

    Solidaritätszuschlaggesetz (SolZG) in 1991 and 1992.
    Solidaritätszuschlaggesetz 1995 (SolZG 1995) since 1995.

    The Solidarity Surcharge is an additional tax on top of the income tax which
    is the tax base. As opposed to the 'standard' income tax, child allowance is
    always deducted for tax base calculation.

    There is also Solidarity Surcharge on the Capital Income Tax, but always
    with Solidarity Surcharge tax rate and no tax exempt level. §3 (3) S.2
    SolzG 1995.

    """
    return (
        solidaritätszuschlagstarif(
            steuer_pro_person=einkommensteuer__betrag_mit_kinderfreibetrag_y_sn,
            familie__anzahl_personen_sn=familie__anzahl_personen_sn,
            parameter_solidaritätszuschlag=parameter_solidaritätszuschlag,
            xnp=xnp,
        )
        + parameter_solidaritätszuschlag.rates[0, -1]
        * einkommensteuer__abgeltungssteuer__betrag_y_sn
    )
