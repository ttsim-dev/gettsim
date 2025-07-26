"""Income relevant for housing benefit calculation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    AggType,
    ConsecutiveIntLookupTableParamValue,
    PiecewisePolynomialParamValue,
    agg_by_p_id_function,
    get_consecutive_int_lookup_table_param_value,
    param_function,
    piecewise_polynomial,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType


@agg_by_p_id_function(agg_type=AggType.SUM, end_date="2015-12-31")
def alleinerziehendenbonus(
    kindergeld__kind_bis_10_mit_kindergeld: bool,
    kindergeld__p_id_empfänger: int,
    p_id: int,
) -> int:
    pass


@param_function()
def min_einkommen_lookup_table(
    min_einkommen: dict[int, float],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Create a LookupTable for the min income thresholds."""
    return get_consecutive_int_lookup_table_param_value(raw=min_einkommen, xnp=xnp)


@policy_function()
def einkommen_m_wthh(
    anzahl_personen_wthh: int,
    freibetrag_m_wthh: float,
    einkommen_vor_freibetrag_m_wthh: float,
    min_einkommen_lookup_table: ConsecutiveIntLookupTableParamValue,
    xnp: ModuleType,
) -> float:
    """Income relevant for Wohngeld calculation.

    Reference: § 13 WoGG
    """
    einkommen_ohne_freibetrag = einkommen_vor_freibetrag_m_wthh - freibetrag_m_wthh
    mindesteinkommen = min_einkommen_lookup_table.look_up(
        xnp.minimum(
            anzahl_personen_wthh,
            min_einkommen_lookup_table.values_to_look_up.shape[0],
        )
    )

    return xnp.maximum(einkommen_ohne_freibetrag, mindesteinkommen)


@policy_function()
def abzugsanteil_vom_einkommen_für_steuern_sozialversicherung(
    einkommensteuer__betrag_y_sn: float,
    sozialversicherung__rente__beitrag__betrag_versicherter_y: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_y: float,
    abzugsbeträge_steuern_sozialversicherung: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Calculate housing benefit subtractions on the individual level.

    Note that einkommensteuer__betrag_y_sn is used as an approximation for taxes
    on income (as mentioned in § 16 WoGG Satz 1 Nr. 1).

    """
    stufe = 0

    if einkommensteuer__betrag_y_sn > 0:
        stufe = stufe + 1
    if sozialversicherung__rente__beitrag__betrag_versicherter_y > 0:
        stufe = stufe + 1
    if sozialversicherung__kranken__beitrag__betrag_versicherter_y > 0:
        stufe = stufe + 1
    return abzugsbeträge_steuern_sozialversicherung.look_up(stufe)


@policy_function(end_date="2006-12-31", leaf_name="einkommen_vor_freibetrag_m")
def einkommen_vor_freibetrag_m_ohne_elterngeld(
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__einnahmen_nach_abzug_werbungskosten_m: float,
    einnahmen__kapitalerträge_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    sozialversicherung__arbeitslosen__betrag_m: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_m: float,
    einkommensteuer__einkünfte__sonstige__rente__betrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    abzugsanteil_vom_einkommen_für_steuern_sozialversicherung: float,
) -> float:
    """Sum gross incomes relevant for housing benefit calculation on individual level
    and deducting individual housing benefit subtractions.
    Reference: § 14 WoGG

    """
    einkommen = (
        einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        + einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__einnahmen_nach_abzug_werbungskosten_m
        + einnahmen__kapitalerträge_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
    )

    transfers = (
        sozialversicherung__arbeitslosen__betrag_m
        + einkommensteuer__einkünfte__sonstige__rente__betrag_m
        + unterhalt__tatsächlich_erhaltener_betrag_m
        + unterhaltsvorschuss__betrag_m
    )

    eink_ind = (
        einkommen + transfers + einkommensteuer__einkünfte__sonstige__alle_weiteren_m
    )
    return (1 - abzugsanteil_vom_einkommen_für_steuern_sozialversicherung) * eink_ind


@policy_function(start_date="2007-01-01", leaf_name="einkommen_vor_freibetrag_m")
def einkommen_vor_freibetrag_m_mit_elterngeld(
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__einnahmen_nach_abzug_werbungskosten_m: float,
    einnahmen__kapitalerträge_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    sozialversicherung__arbeitslosen__betrag_m: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_m: float,
    einkommensteuer__einkünfte__sonstige__rente__betrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    elterngeld__anrechenbarer_betrag_m: float,
    abzugsanteil_vom_einkommen_für_steuern_sozialversicherung: float,
) -> float:
    """Sum gross incomes relevant for housing benefit calculation on individual level
    and deducting individual housing benefit subtractions.
    Reference: § 14 WoGG


    """
    # TODO(@MImmesberger): Find out whether unterhalt__tatsächlich_erhaltener_betrag_m and
    # unterhaltsvorschuss__betrag_m are counted as income for Wohngeld income check.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/357
    einkommen = (
        einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        + einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__einnahmen_nach_abzug_werbungskosten_m
        + einnahmen__kapitalerträge_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
    )

    transfers = (
        sozialversicherung__arbeitslosen__betrag_m
        + einkommensteuer__einkünfte__sonstige__rente__betrag_m
        + unterhalt__tatsächlich_erhaltener_betrag_m
        + unterhaltsvorschuss__betrag_m
        + elterngeld__anrechenbarer_betrag_m
    )

    eink_ind = (
        einkommen + transfers + einkommensteuer__einkünfte__sonstige__alle_weiteren_m
    )
    return (1 - abzugsanteil_vom_einkommen_für_steuern_sozialversicherung) * eink_ind


@policy_function(end_date="2015-12-31", leaf_name="freibetrag_m")
def freibetrag_m_bis_2015(
    einnahmen__bruttolohn_m: float,
    ist_kind_mit_erwerbseinkommen: bool,
    behinderungsgrad: int,
    familie__alleinerziehend: bool,
    alleinerziehendenbonus: int,
    freibetrag_bei_behinderung_gestaffelt_y: PiecewisePolynomialParamValue,
    freibetrag_kinder_m: dict[str, float],
    xnp: ModuleType,
) -> float:
    """Calculate housing benefit subtractions for one individual until 2015."""
    freibetrag_bei_behinderung = (
        piecewise_polynomial(
            x=behinderungsgrad,
            parameters=freibetrag_bei_behinderung_gestaffelt_y,
            xnp=xnp,
        )
        / 12
    )

    # Subtraction for single parents and working children
    if ist_kind_mit_erwerbseinkommen:
        freibetrag_kinder = min(
            einnahmen__bruttolohn_m,
            freibetrag_kinder_m["arbeitendes_kind"],
        )

    elif familie__alleinerziehend:
        freibetrag_kinder = (
            alleinerziehendenbonus * freibetrag_kinder_m["alleinerziehend"]
        )
    else:
        freibetrag_kinder = 0.0
    return freibetrag_bei_behinderung + freibetrag_kinder


@policy_function(start_date="2016-01-01", leaf_name="freibetrag_m")
def freibetrag_m_ab_2016(
    einnahmen__bruttolohn_m: float,
    ist_kind_mit_erwerbseinkommen: bool,
    behinderungsgrad: int,
    familie__alleinerziehend: bool,
    freibetrag_bei_behinderung_pauschal_y: float,
    freibetrag_kinder_m: dict[str, float],
) -> float:
    """Calculate housing benefit subtracting for one individual since 2016."""
    freibetrag_bei_behinderung = (
        freibetrag_bei_behinderung_pauschal_y / 12 if behinderungsgrad > 0 else 0
    )

    if ist_kind_mit_erwerbseinkommen:
        freibetrag_kinder = min(
            einnahmen__bruttolohn_m,
            freibetrag_kinder_m["arbeitendes_kind"],
        )
    elif familie__alleinerziehend:
        freibetrag_kinder = freibetrag_kinder_m["alleinerziehend"]
    else:
        freibetrag_kinder = 0.0

    return freibetrag_bei_behinderung + freibetrag_kinder


@policy_function()
def ist_kind_mit_erwerbseinkommen(
    einnahmen__bruttolohn_m: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    kindergeld__ist_leistungsbegründendes_kind: bool,
) -> bool:
    """Check if children are working."""
    return (
        einnahmen__bruttolohn_m > 0
        or einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m > 0
    ) and kindergeld__ist_leistungsbegründendes_kind
