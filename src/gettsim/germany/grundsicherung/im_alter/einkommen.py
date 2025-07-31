"""Relevant income for Grundsicherung im Alter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import piecewise_polynomial, policy_function

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.germany.grundsicherung.bedarfe import Regelbedarfsstufen
    from gettsim.tt import PiecewisePolynomialParam


@policy_function()
def einkommen_m(
    erwerbseinkommen_m: float,
    einkommen_aus_zusätzlicher_altersvorsorge_m: float,
    gesetzliche_rente_m: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    kapitaleinkommen_brutto_m: float,
    einkommensteuer__betrag_m_sn: float,
    solidaritätszuschlag__betrag_m_sn: float,
    familie__anzahl_personen_sn: int,
    sozialversicherung__beiträge_versicherter_m: float,
    elterngeld__anrechenbarer_betrag_m: float,
) -> float:
    """Calculate individual income considered in the calculation of Grundsicherung im
    Alter.
    """
    # Income
    total_income = (
        erwerbseinkommen_m
        + gesetzliche_rente_m
        + einkommen_aus_zusätzlicher_altersvorsorge_m
        + einkommensteuer__einkünfte__sonstige__alle_weiteren_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
        + kapitaleinkommen_brutto_m
        + elterngeld__anrechenbarer_betrag_m
    )

    out = (
        total_income
        - (einkommensteuer__betrag_m_sn / familie__anzahl_personen_sn)
        - (solidaritätszuschlag__betrag_m_sn / familie__anzahl_personen_sn)
        - sozialversicherung__beiträge_versicherter_m
    )

    return max(out, 0.0)


@policy_function(start_date="2011-01-01")
def erwerbseinkommen_m(
    einnahmen__bruttolohn_m: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    anrechnungsfreier_anteil_erwerbseinkünfte: float,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
) -> float:
    """Calculate individual earnings considered in the calculation of Grundsicherung im
    Alter.

    Legal reference: § 82 SGB XII Abs. 3

    Notes
    -----
    - Freibeträge for income are currently not considered
    - Start date is 2011 because of the reference to regelbedarfsstufen,
      which was introduced in 2011.
    - The cap at 1/2 of Regelbedarf was only introduced in 2006 (which is currently
      not implemented): https://www.buzer.de/gesetz/3415/al3764-0.htm
    """
    earnings = (
        einnahmen__bruttolohn_m
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
    )

    earnings_after_max_deduction = (
        earnings - grundsicherung__regelbedarfsstufen.rbs_1 / 2
    )
    earnings = (1 - anrechnungsfreier_anteil_erwerbseinkünfte) * earnings

    return max(earnings, earnings_after_max_deduction)


@policy_function(end_date="2015-12-31", leaf_name="kapitaleinkommen_brutto_m")
def kapitaleinkommen_brutto_m_ohne_freibetrag(
    einnahmen__kapitalerträge_m: float,
) -> float:
    """Capital income."""
    return max(0.0, einnahmen__kapitalerträge_m)


@policy_function(start_date="2016-01-01", leaf_name="kapitaleinkommen_brutto_m")
def kapitaleinkommen_brutto_m_mit_freibetrag(
    einnahmen__kapitalerträge_y: float,
    freibetrag_kapitaleinkünfte: float,
) -> float:
    """Capital income minus the capital income exemption.

    Legal reference: § 43 SGB XII Abs. 2
    """
    capital_income_y = einnahmen__kapitalerträge_y - freibetrag_kapitaleinkünfte

    return max(0.0, capital_income_y / 12)


@policy_function(start_date="2011-01-01")
def einkommen_aus_zusätzlicher_altersvorsorge_m(
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
    anrechnungsfreier_anteil_private_renteneinkünfte: PiecewisePolynomialParam,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
    xnp: ModuleType,
) -> float:
    """Calculate individual private pension benefits considered in the calculation of
    Grundsicherung im Alter.

    Legal reference: § 82 SGB XII Abs. 4
    """
    freibetrag = piecewise_polynomial(
        x=(
            einnahmen__renten__sonstige_private_vorsorge_m
            + einnahmen__renten__geförderte_private_vorsorge_m
            + einnahmen__renten__betriebliche_altersvorsorge_m
        ),
        parameters=anrechnungsfreier_anteil_private_renteneinkünfte,
        xnp=xnp,
    )
    upper = grundsicherung__regelbedarfsstufen.rbs_1 / 2

    return (
        einnahmen__renten__sonstige_private_vorsorge_m
        + einnahmen__renten__geförderte_private_vorsorge_m
        + einnahmen__renten__betriebliche_altersvorsorge_m
        - min(
            freibetrag,
            upper,
        )
    )


@policy_function(end_date="2020-12-31", leaf_name="gesetzliche_rente_m")
def gesetzliche_rente_m_bis_2020(
    einnahmen__renten__gesetzliche_m: float,
) -> float:
    """Calculate individual public pension benefits which are considered in the
    calculation of Grundsicherung im Alter until 2020.

    Until 2020: No deduction is possible.
    """
    return einnahmen__renten__gesetzliche_m


@policy_function(start_date="2021-01-01", leaf_name="gesetzliche_rente_m")
def gesetzliche_rente_m_ab_2021(
    einnahmen__renten__gesetzliche_m: float,
    sozialversicherung__rente__grundrente__grundsätzlich_anspruchsberechtigt: bool,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
    anrechnungsfreier_anteil_gesetzliche_rente: PiecewisePolynomialParam,
    xnp: ModuleType,
) -> float:
    """Calculate individual public pension benefits which are considered in the
    calculation of Grundsicherung im Alter since 2021.

    Starting from 2021: If eligible for Grundrente, can deduct 100€ completely and 30%
    of private pension above 100 (but no more than 1/2 of regelbedarf)
    """
    angerechnete_rente = piecewise_polynomial(
        x=einnahmen__renten__gesetzliche_m,
        parameters=anrechnungsfreier_anteil_gesetzliche_rente,
        xnp=xnp,
    )

    upper = grundsicherung__regelbedarfsstufen.rbs_1 / 2
    if sozialversicherung__rente__grundrente__grundsätzlich_anspruchsberechtigt:
        angerechnete_rente = min(angerechnete_rente, upper)
    else:
        angerechnete_rente = 0.0

    return einnahmen__renten__gesetzliche_m - angerechnete_rente
