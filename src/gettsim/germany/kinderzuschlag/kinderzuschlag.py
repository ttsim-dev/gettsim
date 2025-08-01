"""Kinderzuschlag policy logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import param_function, policy_function

if TYPE_CHECKING:
    from gettsim.germany.param_types import (
        ExistenzminimumNachAufwendungenMitBildungUndTeilhabe,
    )
    from gettsim.tt import ConsecutiveIntLookupTableParamValue


@param_function(start_date="2021-01-01", end_date="2022-12-31", leaf_name="satz")
def satz_mit_gestaffeltem_kindergeld(
    existenzminimum: ExistenzminimumNachAufwendungenMitBildungUndTeilhabe,
    kindergeld__satz_nach_anzahl_kinder: ConsecutiveIntLookupTableParamValue,
    satz_vorjahr_ohne_kindersofortzuschlag: float,
) -> float:
    """Prior to 2021, the maximum amount of the Kinderzuschlag was specified directly in
    the laws and directives.

    In 2021, 2022, and from 2024 on, this measure has been derived from
    subsistence levels. This function implements that calculation.

    For 2023 the amount is once again explicitly specified as a parameter.
    """
    return max(
        (
            existenzminimum.regelsatz.kind
            + existenzminimum.kosten_der_unterkunft.kind
            + existenzminimum.heizkosten.kind
        )
        / 12
        - kindergeld__satz_nach_anzahl_kinder.look_up(1),
        satz_vorjahr_ohne_kindersofortzuschlag,
    )


@param_function(leaf_name="satz", start_date="2024-01-01")
def satz_mit_einheitlichem_kindergeld_und_kindersofortzuschlag(
    existenzminimum: ExistenzminimumNachAufwendungenMitBildungUndTeilhabe,
    kindergeld__satz: float,
    bürgergeld__kindersofortzuschlag: float,
    satz_vorjahr_ohne_kindersofortzuschlag: float,
) -> float:
    """Kinderzuschlag pro Kind.

    Formula according to § 6a (2) BKGG.
    """
    current_formula = (
        existenzminimum.regelsatz.kind
        + existenzminimum.kosten_der_unterkunft.kind
        + existenzminimum.heizkosten.kind
    ) / 12 - kindergeld__satz

    satz_ohne_kindersofortzuschlag = max(
        current_formula,
        satz_vorjahr_ohne_kindersofortzuschlag,
    )
    return satz_ohne_kindersofortzuschlag + bürgergeld__kindersofortzuschlag


@policy_function(start_date="2005-01-01")
def betrag_m_bg(
    anspruchshöhe_m_bg: float,
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger: bool,
    anzahl_rentenbezieher_hh: int,
) -> float:
    """Amount of Kinderzuschlag at the Bedarfsgemeinschaft level."""
    if (not vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger) or (
        anzahl_rentenbezieher_hh > 0
    ):
        out = 0.0
    else:
        out = anspruchshöhe_m_bg

    return out


@policy_function(start_date="2005-01-01")
def anspruchshöhe_m(
    anspruchshöhe_m_bg: float,
    familie__anzahl_personen_bg: int,
) -> float:
    """Kinderzuschlag claim per member of the Bedarfsgemeinschaft."""
    return anspruchshöhe_m_bg / familie__anzahl_personen_bg


@policy_function(start_date="2005-01-01")
def anspruchshöhe_m_bg(
    basisbetrag_m_bg: float,
    vermögen_bg: float,
    vermögensfreibetrag_bg: float,
) -> float:
    """Kinderzuschlag claim at the Bedarfsgemeinschaft level."""
    if vermögen_bg > vermögensfreibetrag_bg:
        out = max(
            basisbetrag_m_bg - (vermögen_bg - vermögensfreibetrag_bg),
            0.0,
        )
    else:
        out = basisbetrag_m_bg
    return out


@policy_function(
    start_date="2005-01-01",
    end_date="2022-12-31",
    leaf_name="vermögensfreibetrag_bg",
)
def vermögensfreibetrag_bg_bis_2022(
    arbeitslosengeld_2__vermögensfreibetrag_bg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag until 2022."""
    return arbeitslosengeld_2__vermögensfreibetrag_bg


@policy_function(start_date="2023-01-01", leaf_name="vermögensfreibetrag_bg")
def vermögensfreibetrag_bg_ab_2023(
    bürgergeld__vermögensfreibetrag_in_karenzzeit_bg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag since 2023."""
    return bürgergeld__vermögensfreibetrag_in_karenzzeit_bg


@policy_function(
    start_date="2005-01-01",
    end_date="2008-09-30",
    leaf_name="basisbetrag_m_bg",
)
def basisbetrag_m_bg_check_maximales_netteinkommen(
    nettoeinkommen_eltern_m_bg: float,
    maximales_nettoeinkommen_m_bg: float,
    basisbetrag_kind_m_bg: float,
    anzurechnendes_einkommen_eltern_m_bg: float,
    familie__anzahl_erwachsene_bg: int,
) -> float:
    """Calculate Kinderzuschlag since 2005 until 06/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, net income needs to be below the maximum income
    threshold.

    Kinderzuschlag is only paid out if parents are part of the BG
    (familie__anzahl_erwachsene_bg >= 1).

    """
    if (
        nettoeinkommen_eltern_m_bg <= maximales_nettoeinkommen_m_bg
    ) and familie__anzahl_erwachsene_bg >= 1:
        out = max(basisbetrag_kind_m_bg - anzurechnendes_einkommen_eltern_m_bg, 0.0)
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2008-10-01",
    end_date="2019-06-30",
    leaf_name="basisbetrag_m_bg",
)
def basisbetrag_m_bg_check_mindestbruttoeinkommen_und_maximales_nettoeinkommen(
    bruttoeinkommen_eltern_m_bg: float,
    nettoeinkommen_eltern_m_bg: float,
    mindestbruttoeinkommen_m_bg: float,
    maximales_nettoeinkommen_m_bg: float,
    basisbetrag_kind_m_bg: float,
    anzurechnendes_einkommen_eltern_m_bg: float,
    familie__anzahl_erwachsene_bg: int,
) -> float:
    """Calculate Kinderzuschlag since 2005 until 06/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold and net income needs to be below the maximum income
    threshold.

    Kinderzuschlag is only paid out if parents are part of the BG
    (familie__anzahl_erwachsene_bg >= 1).

    """
    if (
        (bruttoeinkommen_eltern_m_bg >= mindestbruttoeinkommen_m_bg)
        and (nettoeinkommen_eltern_m_bg <= maximales_nettoeinkommen_m_bg)
        and familie__anzahl_erwachsene_bg >= 1
    ):
        out = max(basisbetrag_kind_m_bg - anzurechnendes_einkommen_eltern_m_bg, 0.0)
    else:
        out = 0.0

    return out


@policy_function(start_date="2019-07-01", leaf_name="basisbetrag_m_bg")
def basisbetrag_m_bg_check_mindestbruttoeinkommen(
    bruttoeinkommen_eltern_m_bg: float,
    mindestbruttoeinkommen_m_bg: float,
    basisbetrag_kind_m_bg: float,
    anzurechnendes_einkommen_eltern_m_bg: float,
    familie__anzahl_erwachsene_bg: int,
) -> float:
    """Calculate Kinderzuschlag since 07/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold.

    Kinderzuschlag is only paid out if parents are part of the BG
    (familie__anzahl_erwachsene_bg >= 1).

    """
    if (
        bruttoeinkommen_eltern_m_bg >= mindestbruttoeinkommen_m_bg
    ) and familie__anzahl_erwachsene_bg >= 1:
        out = max(basisbetrag_kind_m_bg - anzurechnendes_einkommen_eltern_m_bg, 0.0)
    else:
        out = 0.0

    return out


@policy_function(
    leaf_name="basisbetrag_kind_m", start_date="2005-01-01", end_date="2022-12-31"
)
def basisbetrag_kind_m_bis_2022(
    kindergeld__ist_leistungsbegründendes_kind: bool,
    einnahmen__bruttolohn_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    arbeitslosengeld_2__anrechnungsfreies_einkommen_m: float,
    satz: float,
    entzugsrate_kindeseinkommen: float,
) -> float:
    """Kinderzuschlag after income for each possibly eligible child is considered."""
    out = kindergeld__ist_leistungsbegründendes_kind * (
        satz
        - entzugsrate_kindeseinkommen
        * (
            einnahmen__bruttolohn_m
            + unterhalt__tatsächlich_erhaltener_betrag_m
            + unterhaltsvorschuss__betrag_m
            - arbeitslosengeld_2__anrechnungsfreies_einkommen_m
        )
    )

    return max(out, 0.0)


@policy_function(leaf_name="basisbetrag_kind_m", start_date="2023-01-01")
def basisbetrag_kind_m_ab_2023(
    kindergeld__ist_leistungsbegründendes_kind: bool,
    einnahmen__bruttolohn_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    bürgergeld__anrechnungsfreies_einkommen_m: float,
    satz: float,
    entzugsrate_kindeseinkommen: float,
) -> float:
    """Kinderzuschlag after income for each possibly eligible child is considered."""
    out = kindergeld__ist_leistungsbegründendes_kind * (
        satz
        - entzugsrate_kindeseinkommen
        * (
            einnahmen__bruttolohn_m
            + unterhalt__tatsächlich_erhaltener_betrag_m
            + unterhaltsvorschuss__betrag_m
            - bürgergeld__anrechnungsfreies_einkommen_m
        )
    )

    return max(out, 0.0)
