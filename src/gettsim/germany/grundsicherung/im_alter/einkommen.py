"""Relevant income for Grundsicherung im Alter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ttsim.unit_converters import per_y_to_per_m

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    piecewise_polynomial,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.germany.grundsicherung.bedarfe import Regelbedarfsstufen


@policy_function(
    end_date="2017-12-31",
    leaf_name="einkommen_m",
)
def einkommen_m_bis_2017(
    erwerbseinkommen_m: float,
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
    einnahmen__renten__aus_berufsständischen_versicherungen_m: float,
    gesetzliche_rente_m: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    kapitaleinkommen_brutto_m: float,
    einkommensteuer__betrag_m_sn: float,
    solidaritätszuschlag__betrag_m_sn: float,
    familie__anzahl_personen_sn: int,
    sozialversicherung__beiträge_versicherter_m: float,
    elterngeld__anrechenbarer_betrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
) -> float:
    """Income considered for Grundsicherung im Alter before 2018.

    All pension income is fully counted as income.
    """
    total_income = (
        erwerbseinkommen_m
        + gesetzliche_rente_m
        + einnahmen__renten__sonstige_private_vorsorge_m
        + einnahmen__renten__geförderte_private_vorsorge_m
        + einnahmen__renten__betriebliche_altersvorsorge_m
        + einnahmen__renten__aus_berufsständischen_versicherungen_m
        + einkommensteuer__einkünfte__sonstige__alle_weiteren_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
        + kapitaleinkommen_brutto_m
        + elterngeld__anrechenbarer_betrag_m
        + unterhalt__tatsächlich_erhaltener_betrag_m
        + unterhaltsvorschuss__betrag_m
    )

    out = (
        total_income
        - (einkommensteuer__betrag_m_sn / familie__anzahl_personen_sn)
        - (solidaritätszuschlag__betrag_m_sn / familie__anzahl_personen_sn)
        - sozialversicherung__beiträge_versicherter_m
    )

    return max(out, 0.0)


@policy_function(start_date="2018-01-01", leaf_name="einkommen_m")
def einkommen_m_ab_2018(
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
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
) -> float:
    """Income considered for Grundsicherung im Alter from 2018.

    From 2018, § 82 Abs. 4, 5 SGB XII (Art. 2 Nr. 7 Betriebsrentenstärkungsgesetz v.
    17.08.2017, BGBl. I S. 3214) introduces a Freibetrag for 'zusätzliche
    Altersvorsorge', applied via einkommen_aus_zusätzlicher_altersvorsorge_m.
    """
    total_income = (
        erwerbseinkommen_m
        + gesetzliche_rente_m
        + einkommen_aus_zusätzlicher_altersvorsorge_m
        + einkommensteuer__einkünfte__sonstige__alle_weiteren_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
        + kapitaleinkommen_brutto_m
        + elterngeld__anrechenbarer_betrag_m
        + unterhalt__tatsächlich_erhaltener_betrag_m
        + unterhaltsvorschuss__betrag_m
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
    """Earnings considered for Grundsicherung im Alter.

    Legal reference: § 82 SGB XII Abs. 3
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

    return max(0.0, per_y_to_per_m(capital_income_y))


@policy_function(start_date="2018-01-01")
def einkommen_aus_zusätzlicher_altersvorsorge_m(
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
    einnahmen__renten__aus_berufsständischen_versicherungen_m: float,
    anrechnungsfreier_anteil_zusätzliche_altersvorsorge: PiecewisePolynomialParamValue,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
    xnp: ModuleType,
) -> float:
    """Private and occupational pension income for Grundsicherung im Alter.

    Legal reference: § 82 Abs. 4, 5 SGB XII (eingeführt durch Art. 2 Nr. 7
    Betriebsrentenstärkungsgesetz v. 17.08.2017, BGBl. I S. 3214)

    The Freibetrag for 'zusätzliche Altersvorsorge' applies as defined in § 82 Abs. 5
    SGB XII:

    - Betriebliche Altersversorgung i.S.d. BetrAVG (Abs. 5 Satz 2 Nr. 1)
    - Zertifizierte Altersvorsorge / Riester (Abs. 5 Satz 2 Nr. 2)
    - Sonstige private Altersvorsorge (Abs. 5 Satz 1: freiwillig, lebenslang)
    """
    zusätzliche_altersvorsorge_m = (
        einnahmen__renten__sonstige_private_vorsorge_m
        + einnahmen__renten__geförderte_private_vorsorge_m
        + einnahmen__renten__betriebliche_altersvorsorge_m
    )
    freibetrag = piecewise_polynomial(
        x=zusätzliche_altersvorsorge_m,
        parameters=anrechnungsfreier_anteil_zusätzliche_altersvorsorge,
        xnp=xnp,
    )

    return (
        zusätzliche_altersvorsorge_m
        - min(freibetrag, grundsicherung__regelbedarfsstufen.rbs_1 / 2)
        + einnahmen__renten__aus_berufsständischen_versicherungen_m
    )


@policy_function(end_date="2020-12-31", leaf_name="gesetzliche_rente_m")
def gesetzliche_rente_m_bis_2020(
    einnahmen__renten__gesetzliche_m: float,
) -> float:
    """Public pension benefits considered for Grundsicherung im Alter until 2020."""
    return einnahmen__renten__gesetzliche_m


@policy_function(start_date="2021-01-01", leaf_name="gesetzliche_rente_m")
def gesetzliche_rente_m_ab_2021(
    einnahmen__renten__gesetzliche_m: float,
    sozialversicherung__rente__grundrente__grundsätzlich_anspruchsberechtigt: bool,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
    anrechnungsfreier_anteil_gesetzliche_rente: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Public pension income for Grundsicherung im Alter, with Grundrentenzeiten-Freibetrag.

    Legal reference: § 82a SGB XII (eingeführt durch Art. 3 Grundrentengesetz
    v. 12.08.2020, BGBl. I S. 1879, effective 2021-01-01)

    Persons with ≥ 33 years of Grundrentenzeiten (§ 76g Abs. 2 SGB VI) receive
    a Freibetrag: 100 € + 30 % of public pension income above 100 €, capped at
    50 % of Regelbedarfsstufe 1.
    """
    freibetrag = piecewise_polynomial(
        x=einnahmen__renten__gesetzliche_m,
        parameters=anrechnungsfreier_anteil_gesetzliche_rente,
        xnp=xnp,
    )

    if sozialversicherung__rente__grundrente__grundsätzlich_anspruchsberechtigt:
        freibetrag = min(freibetrag, grundsicherung__regelbedarfsstufen.rbs_1 / 2)
    else:
        freibetrag = 0.0

    return einnahmen__renten__gesetzliche_m - freibetrag
