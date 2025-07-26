"""Unemployment benefits (Arbeitslosengeld)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from _gettsim.param_converters import (
    convert_sparse_dict_to_consecutive_int_lookup_table,
)
from gettsim.tt import (
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.tt import (
        ConsecutiveIntLookupTableParamValue,
    )


@policy_function(
    end_date="1998-07-31",
    leaf_name="betrag_m",
    fail_msg_if_included="Arbeitslosengeld before August 1998 is not implemented.",
)
def betrag_m_bis_1998_07() -> float:
    """Calculate individual unemployment benefit."""


@policy_function(start_date="1998-08-01")
def betrag_m(
    einkommensteuer__anzahl_kinderfreibeträge: int,
    grundsätzlich_anspruchsberechtigt: bool,
    mean_nettoeinkommen_in_12_monaten_vor_arbeitslosigkeit_m: float,
    satz: dict[str, float],
) -> float:
    """Calculate individual unemployment benefit."""
    if einkommensteuer__anzahl_kinderfreibeträge == 0:
        arbeitsl_geld_satz = satz["allgemein"]
    else:
        arbeitsl_geld_satz = satz["erhöht"]

    if grundsätzlich_anspruchsberechtigt:
        out = (
            mean_nettoeinkommen_in_12_monaten_vor_arbeitslosigkeit_m
            * arbeitsl_geld_satz
        )
    else:
        out = 0.0

    return out


@policy_function()
def monate_verbleibender_anspruchsdauer(
    alter: int,
    monate_sozialversicherungspflichtiger_beschäftigung_in_letzten_5_jahren: int,
    mindestversicherungszeit_erreicht: bool,
    monate_durchgängigen_bezugs_von_arbeitslosengeld: int,
    anspruchsdauer_nach_alter: ConsecutiveIntLookupTableParamValue,
    anspruchsdauer_nach_versicherungspflichtigen_monaten: ConsecutiveIntLookupTableParamValue,
) -> int:
    """Remaining amount of months of potential unemployment benefit claims."""
    auf_altersbasis = anspruchsdauer_nach_alter.look_up(alter)
    auf_basis_versicherungspflichtiger_monate = (
        anspruchsdauer_nach_versicherungspflichtigen_monaten.look_up(
            monate_sozialversicherungspflichtiger_beschäftigung_in_letzten_5_jahren
        )
    )

    if mindestversicherungszeit_erreicht:
        out = max(
            min(auf_altersbasis, auf_basis_versicherungspflichtiger_monate)
            - monate_durchgängigen_bezugs_von_arbeitslosengeld,
            0,
        )
    else:
        out = 0

    return out


@policy_function()
def mindestversicherungszeit_erreicht(
    monate_beitragspflichtig_versichert_in_letzten_30_monaten: int,
    mindestversicherungsmonate: int,
) -> bool:
    """At least 12 months of unemployment contributions in the 30 months before claiming
    unemployment insurance.
    """
    return (
        monate_beitragspflichtig_versichert_in_letzten_30_monaten
        >= mindestversicherungsmonate
    )


@policy_function()
def grundsätzlich_anspruchsberechtigt(
    alter: int,
    arbeitssuchend: bool,
    monate_verbleibender_anspruchsdauer: int,
    arbeitsstunden_w: float,
    sozialversicherung__rente__altersrente__regelaltersrente__altersgrenze: float,
    stundengrenze: float,
) -> bool:
    """Check eligibility for unemployment benefit."""
    regelaltersgrenze = (
        sozialversicherung__rente__altersrente__regelaltersrente__altersgrenze
    )

    return (
        arbeitssuchend
        and (monate_verbleibender_anspruchsdauer > 0)
        and (alter < regelaltersgrenze)
        and (arbeitsstunden_w < stundengrenze)
    )


@policy_function()
def mean_nettoeinkommen_für_bemessungsgrundlage_bei_arbeitslosigkeit_y(
    sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y: float,
    sozialversicherungspauschale: float,
    lohnsteuer__betrag_y: float,
    lohnsteuer__betrag_soli_y: float,
) -> float:
    """Approximate the income relevant for calculating unemployment insurance benefits.

    This target can be used as an input in another GETTSIM call to compute
    Arbeitslosengeld. In principle, the relevant gross wage for this target is the sum
    of the gross wages in the 12 months before unemployment. For most datasets, except
    those with monthly income date (IAB, DRV data), the best approximation will likely
    be the gross wage in the calendar year before unemployment.
    """
    berücksichtigungsfähige_einnahmen = min(
        einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y,
        sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_y,
    )
    pauschalierte_sozialversicherungsbeiträge = (
        sozialversicherungspauschale * berücksichtigungsfähige_einnahmen
    )
    return max(
        (
            berücksichtigungsfähige_einnahmen
            - pauschalierte_sozialversicherungsbeiträge
            - lohnsteuer__betrag_y
            - lohnsteuer__betrag_soli_y
        ),
        0.0,
    )


@param_function(start_date="1997-03-24")
def anspruchsdauer_nach_alter(
    raw_anspruchsdauer_nach_alter: dict[str | int, int],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Amount of potential months of unemployment benefit claims by age."""
    base = raw_anspruchsdauer_nach_alter.copy()
    min_age = base.pop("min_age")
    max_age = base.pop("max_age")
    return convert_sparse_dict_to_consecutive_int_lookup_table(
        raw=base,
        min_int_in_table=min_age,
        max_int_in_table=max_age,
        xnp=xnp,
    )


@param_function(start_date="1997-03-24")
def anspruchsdauer_nach_versicherungspflichtigen_monaten(
    raw_anspruchsdauer_nach_versicherungspflichtigen_monaten: dict[str | int, int],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Amount of potential months of unemployment benefit claims by months of
    compulsory insurance.
    """
    base = raw_anspruchsdauer_nach_versicherungspflichtigen_monaten.copy()
    min_months = base.pop("min_months")
    max_months = base.pop("max_months")
    return convert_sparse_dict_to_consecutive_int_lookup_table(
        raw=base,
        min_int_in_table=min_months,
        max_int_in_table=max_months,
        xnp=xnp,
    )
