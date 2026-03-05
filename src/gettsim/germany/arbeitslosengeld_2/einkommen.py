"""Relevant income for Arbeitslosengeld II."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    get_piecewise_parameters,
    merge_piecewise_intervals,
    param_function,
    piecewise_polynomial,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.typing import RawParamValue


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def anzurechnendes_einkommen_m(
    nettoeinkommen_nach_abzug_freibetrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    kindergeld_zur_bedarfsdeckung_m: float,
    kindergeldübertrag_m: float,
) -> float:
    """Relevant income according to SGB II.

    Note: If you are using GETTSIM and want to aggregate to BG/HH level (which is never
    required by the rules of the taxes and transfers system), you need to deduct
    `differenz_kindergeld_kindbedarf_m_hh` from the result of this function. This is
    necessary because the Kindergeld received by the child may enter
    `anzurechnendes_einkommen_m_hh` twice: once as Kindergeld and once as
    Kindergeldübertrag.
    """
    return (
        nettoeinkommen_nach_abzug_freibetrag_m
        + unterhalt__tatsächlich_erhaltener_betrag_m
        + unterhaltsvorschuss__betrag_m
        + kindergeld_zur_bedarfsdeckung_m
        + kindergeldübertrag_m
    )


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def nettoeinkommen_nach_abzug_freibetrag_m(
    nettoeinkommen_vor_abzug_freibetrag_m: float,
    anrechnungsfreies_einkommen_m: float,
) -> float:
    """Net income after deductions for calculation of basic subsistence."""
    return nettoeinkommen_vor_abzug_freibetrag_m - anrechnungsfreies_einkommen_m


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def nettoeinkommen_vor_abzug_freibetrag_m(
    bruttoeinkommen_m: float,
    einkommensteuer__betrag_m_sn: float,
    solidaritätszuschlag__betrag_m_sn: float,
    familie__anzahl_personen_sn: int,
    sozialversicherung__beiträge_versicherter_m: float,
) -> float:
    """Net income for calculation of basic subsistence."""
    return (
        bruttoeinkommen_m
        - (einkommensteuer__betrag_m_sn / familie__anzahl_personen_sn)
        - (solidaritätszuschlag__betrag_m_sn / familie__anzahl_personen_sn)
        - sozialversicherung__beiträge_versicherter_m
    )


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def bruttoeinkommen_m(
    einnahmen__bruttolohn_m: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    einnahmen__kapitalerträge_m: float,
    einnahmen__renten__gesamt_m: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_m: float,
    sozialversicherung__arbeitslosen__betrag_m: float,
    elterngeld__betrag_m: float,
) -> float:
    """Sum up the gross income for calculation of basic subsistence."""
    return (
        einnahmen__bruttolohn_m
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
        + einnahmen__kapitalerträge_m
        + einnahmen__renten__gesamt_m
        + einkommensteuer__einkünfte__sonstige__alle_weiteren_m
        + sozialversicherung__arbeitslosen__betrag_m
        + elterngeld__betrag_m
    )


@policy_function(start_date="2005-01-01", end_date="2005-09-30")
def nettoquote(
    einnahmen__bruttolohn_m: float,
    einkommensteuer__betrag_m_sn: float,
    solidaritätszuschlag__betrag_m_sn: float,
    familie__anzahl_personen_sn: int,
    sozialversicherung__beiträge_versicherter_m: float,
    abzugsfähige_pauschalen: dict[str, float],
) -> float:
    """Share of net to gross wage.

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3 Abs. 2 Alg II-V.
    """
    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit nach § 11 Abs. 2 Nr. 1-5.
    alg2_2005_bne = max(
        (
            einnahmen__bruttolohn_m
            - (einkommensteuer__betrag_m_sn / familie__anzahl_personen_sn)
            - (solidaritätszuschlag__betrag_m_sn / familie__anzahl_personen_sn)
            - sozialversicherung__beiträge_versicherter_m
            - abzugsfähige_pauschalen["werbung"]
            - abzugsfähige_pauschalen["versicherung"]
        ),
        0,
    )

    return alg2_2005_bne / einnahmen__bruttolohn_m


@policy_function(
    start_date="2005-01-01",
    end_date="2005-09-30",
    leaf_name="anrechnungsfreies_einkommen_m",
)
def anrechnungsfreies_einkommen_m_basierend_auf_nettoquote(
    einnahmen__bruttolohn_m: float,
    nettoquote: float,
    parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Share of income which remains to the individual."""
    return nettoquote * piecewise_polynomial(
        x=einnahmen__bruttolohn_m,
        parameters=parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg,
        xnp=xnp,
    )


@policy_function(start_date="2005-10-01", end_date="2022-12-31")
def anrechnungsfreies_einkommen_m(
    einnahmen__bruttolohn_m: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    familie__anzahl_kinder_bis_17_bg: int,
    einkommensteuer__anzahl_kinderfreibeträge: int,
    parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg: PiecewisePolynomialParamValue,
    parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Share of income, which remains to the individual since 10/2005.

    Sozialgesetzbuch (SGB) Zweites Buch (II) - Arbeitslosengeld II, Grundsicherung für
    Arbeitsuchende. SGB II §11b Abs 3
    https://www.gesetze-im-internet.de/sgb_2/__11b.html
    """
    # Beneficiaries who live with a minor child in a group home or who have a minor
    # child have slightly different thresholds. We currently do not consider the second
    # condition.
    eink_erwerbstätigkeit = (
        einnahmen__bruttolohn_m
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
    )

    if (
        familie__anzahl_kinder_bis_17_bg > 0
        or einkommensteuer__anzahl_kinderfreibeträge > 0
    ):
        out = piecewise_polynomial(
            x=eink_erwerbstätigkeit,
            parameters=parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg,
            xnp=xnp,
        )
    else:
        out = piecewise_polynomial(
            x=eink_erwerbstätigkeit,
            parameters=parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg,
            xnp=xnp,
        )
    return out


@param_function(start_date="2005-01-01", end_date="2022-12-31")
def parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg(
    raw_parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg: RawParamValue,
    xnp: ModuleType,
) -> PiecewisePolynomialParamValue:
    """Parameter for calculation of income not subject to transfer withdrawal when
    children are not in the Bedarfsgemeinschaft.
    """
    return get_piecewise_parameters(
        leaf_name="parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg",
        func_type="piecewise_linear",
        parameter_list=raw_parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg,  # ty: ignore[invalid-argument-type]
        xnp=xnp,
    )


@param_function(start_date="2005-10-01", end_date="2022-12-31")
def parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg(
    raw_parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg: RawParamValue,
    raw_parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg: RawParamValue,
    xnp: ModuleType,
) -> PiecewisePolynomialParamValue:
    """Parameter for calculation of income not subject to transfer withdrawal when
    children are in the Bedarfsgemeinschaft.
    """
    updated_parameters = merge_piecewise_intervals(
        base=raw_parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg,  # ty: ignore[invalid-argument-type]
        update=raw_parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg,  # ty: ignore[invalid-argument-type]
    )
    return get_piecewise_parameters(
        leaf_name="parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg",
        func_type="piecewise_linear",
        parameter_list=updated_parameters,
        xnp=xnp,
    )
