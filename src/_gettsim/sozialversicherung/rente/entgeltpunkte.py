from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(end_date="2023-06-30")
def entgeltpunkte_west_updated(
    wohnort_ost_hh: bool,
    entgeltpunkte_west: float,
    neue_entgeltpunkte: float,
) -> float:
    """Updated Entgeltpunkte from West Germany based on current income.

    Given earnings, social insurance rules, average earnings in a particular year and
    potentially other variables (e.g., benefits for raising children, informal care),
    return the new earnings points.
    """
    if wohnort_ost_hh:
        out = entgeltpunkte_west
    else:
        out = entgeltpunkte_west + neue_entgeltpunkte
    return out


@policy_function(end_date="2023-06-30")
def entgeltpunkte_ost_updated(
    wohnort_ost_hh: bool,
    entgeltpunkte_ost: float,
    neue_entgeltpunkte: float,
) -> float:
    """Updated Entgeltpunkte from East Germany based on current income.

    Given earnings, social insurance rules, average earnings in a particular year and
    potentially other variables (e.g., benefits for raising children, informal care),
    return the new earnings points.
    """
    if wohnort_ost_hh:
        out = entgeltpunkte_ost + neue_entgeltpunkte
    else:
        out = entgeltpunkte_ost
    return out


@policy_function(start_date="2023-07-01")
def entgeltpunkte_updated(
    entgeltpunkte: float,
    neue_entgeltpunkte: float,
) -> float:
    """Updated Entgeltpunkte based on current income."""
    return entgeltpunkte + neue_entgeltpunkte


@policy_function(end_date="2024-12-31", leaf_name="neue_entgeltpunkte")
def neue_entgeltpunkte_nach_wohnort(
    einnahmen__bruttolohn_m: float,
    wohnort_ost_hh: bool,
    beitrag__beitragsbemessungsgrenze_m: float,
    beitragspflichtiges_durchschnittsentgelt_y: float,
    umrechnung_entgeltpunkte_beitrittsgebiet: float,
) -> float:
    """Earnings points for the wages earned in the current year."""
    # Scale bruttolohn up if earned in eastern Germany
    if wohnort_ost_hh:
        umgerechneter_bruttolohn = (
            einnahmen__bruttolohn_m * umrechnung_entgeltpunkte_beitrittsgebiet
        )
    else:
        umgerechneter_bruttolohn = einnahmen__bruttolohn_m

    # Calculate the (scaled) wage, which is subject to pension contributions.
    if umgerechneter_bruttolohn > beitrag__beitragsbemessungsgrenze_m:
        versicherungspflichtiger_bruttolohn = beitrag__beitragsbemessungsgrenze_m
    else:
        versicherungspflichtiger_bruttolohn = umgerechneter_bruttolohn

    return versicherungspflichtiger_bruttolohn / (
        beitragspflichtiges_durchschnittsentgelt_y / 12
    )


@policy_function(start_date="2025-01-01", leaf_name="neue_entgeltpunkte")
def neue_entgeltpunkte_einheitlich(
    einnahmen__bruttolohn_m: float,
    beitrag__beitragsbemessungsgrenze_m: float,
    beitragspflichtiges_durchschnittsentgelt_y: float,
) -> float:
    """Earning points for the wages earned in this year."""
    if einnahmen__bruttolohn_m > beitrag__beitragsbemessungsgrenze_m:
        versicherungspflichtiger_bruttolohn = beitrag__beitragsbemessungsgrenze_m
    else:
        versicherungspflichtiger_bruttolohn = einnahmen__bruttolohn_m

    return versicherungspflichtiger_bruttolohn / (
        beitragspflichtiges_durchschnittsentgelt_y / 12
    )


@policy_function(start_date="1992-01-01", end_date="2023-06-30", leaf_name="rentenwert")
def rentenwert_nach_wohnort(
    wohnort_ost_hh: bool,
    sozialversicherung__rente__parameter_rentenwert_nach_wohnort: dict[str, float],
) -> float:
    """Rentenwert."""
    return (
        sozialversicherung__rente__parameter_rentenwert_nach_wohnort["ost"]
        if wohnort_ost_hh
        else sozialversicherung__rente__parameter_rentenwert_nach_wohnort["west"]
    )
