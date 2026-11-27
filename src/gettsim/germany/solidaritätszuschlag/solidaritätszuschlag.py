"""Solidarity Surcharge (Solidaritätszuschlag)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    TTSIMUnit,
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


@policy_function(
    end_date="2008-12-31",
    leaf_name="betrag_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
    # Body delegates to the plain `solidaritätszuschlagstarif` helper, which the
    # unit check cannot evaluate; its declared unit and edges stay checked (GEP 10).
    verify_units=False,
)
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

    Reference:
        - § 3 Abs. 1 Nr. 1 SolZG idF Art. 1 G. v. 24.06.1991 BGBl. I S. 1318
        - § 4 SolZG idF Art. 1 G. v. 24.06.1991 BGBl. I S. 1318
        - § 3 Abs. 1 Nr. 1 SolZG 1995 idF Art. 31 G. v. 23.06.1993 BGBl. I S. 944
        - § 4 SolZG 1995 idF Art. 31 G. v. 23.06.1993 BGBl. I S. 944
        - § 3 Abs. 2 SolZG 1995 idF B. v. 15.10.2002 BGBl. I S. 4130
    """
    return solidaritätszuschlagstarif(
        steuer_pro_person=einkommensteuer__betrag_mit_kinderfreibetrag_y_sn,
        familie__anzahl_personen_sn=familie__anzahl_personen_sn,
        parameter_solidaritätszuschlag=parameter_solidaritätszuschlag,
        xnp=xnp,
    )


@policy_function(
    start_date="2009-01-01",
    leaf_name="betrag_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
    # Body delegates to the plain `solidaritätszuschlagstarif` helper, which the
    # unit check cannot evaluate; its declared unit and edges stay checked (GEP 10).
    verify_units=False,
)
def betrag_y_sn_mit_abgelt_st(
    einkommensteuer__betrag_mit_kinderfreibetrag_y_sn: float,
    familie__anzahl_personen_sn: int,
    einkommensteuer__abgeltungssteuer__betrag_y_sn: float,
    parameter_solidaritätszuschlag: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Calculate the Solidarity Surcharge on Steuernummer level.

    Solidaritätszuschlaggesetz 1995 (SolZG 1995).

    The Solidarity Surcharge is an additional tax on top of the income tax which
    is the tax base. As opposed to the 'standard' income tax, child allowance is
    always deducted for tax base calculation.

    The Solidarity Surcharge on the income tax under § 32d Abs. 3 and 4 EStG
    (Abgeltungsteuer) is always levied at the full rate, without Freigrenze. The
    version of the JStG 2010 also applies to 2009 and 2010 if it is favourable to the
    taxpayer (§ 6 Abs. 12 SolZG 1995).

    Reference:
        - § 3 Abs. 2 SolZG 1995 idF B. v. 15.10.2002 BGBl. I S. 4130
        - § 3 Abs. 3 SolZG 1995 idF Art. 31 G. v. 08.12.2010 BGBl. I S. 1768
        - § 4 SolZG 1995 idF Art. 31 G. v. 08.12.2010 BGBl. I S. 1768
        - § 4 SolZG 1995 idF Art. 1 G. v. 10.12.2019 BGBl. I S. 2115
    """
    return (
        solidaritätszuschlagstarif(
            steuer_pro_person=einkommensteuer__betrag_mit_kinderfreibetrag_y_sn,
            familie__anzahl_personen_sn=familie__anzahl_personen_sn,
            parameter_solidaritätszuschlag=parameter_solidaritätszuschlag,
            xnp=xnp,
        )
        + parameter_solidaritätszuschlag[-1].slope
        * einkommensteuer__abgeltungssteuer__betrag_y_sn
    )
