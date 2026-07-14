from __future__ import annotations

from gettsim.tt import Unit, policy_function


@policy_function(
    end_date="2024-12-31",
    leaf_name="neue_entgeltpunkte_y",
    unit=Unit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_nach_wohnort(
    einnahmen__bruttolohn_y: float,
    wohnort_ost_hh: bool,
    beitrag__beitragsbemessungsgrenze_y: float,
    beitragspflichtiges_durchschnittsentgelt_y: float,
    umrechnung_entgeltpunkte_beitrittsgebiet: float,
) -> float:
    """Earnings points for the wages earned in the current year."""
    # Scale bruttolohn up if earned in eastern Germany
    if wohnort_ost_hh:
        umgerechneter_bruttolohn = (
            einnahmen__bruttolohn_y * umrechnung_entgeltpunkte_beitrittsgebiet
        )
    else:
        umgerechneter_bruttolohn = einnahmen__bruttolohn_y

    # Calculate the (scaled) wage, which is subject to pension contributions.
    if umgerechneter_bruttolohn > beitrag__beitragsbemessungsgrenze_y:
        versicherungspflichtiger_bruttolohn_y = beitrag__beitragsbemessungsgrenze_y
    else:
        versicherungspflichtiger_bruttolohn_y = umgerechneter_bruttolohn

    return (
        versicherungspflichtiger_bruttolohn_y
        / beitragspflichtiges_durchschnittsentgelt_y
    )


@policy_function(
    start_date="2025-01-01",
    leaf_name="neue_entgeltpunkte_y",
    unit=Unit.DIMENSIONLESS.PER_YEAR,
)
def neue_entgeltpunkte_einheitlich(
    einnahmen__bruttolohn_y: float,
    beitrag__beitragsbemessungsgrenze_y: float,
    beitragspflichtiges_durchschnittsentgelt_y: float,
) -> float:
    """Earning points for the wages earned in this year."""
    if einnahmen__bruttolohn_y > beitrag__beitragsbemessungsgrenze_y:
        versicherungspflichtiger_bruttolohn_y = beitrag__beitragsbemessungsgrenze_y
    else:
        versicherungspflichtiger_bruttolohn_y = einnahmen__bruttolohn_y

    return (
        versicherungspflichtiger_bruttolohn_y
        / beitragspflichtiges_durchschnittsentgelt_y
    )


@policy_function(
    start_date="1992-01-01",
    end_date="2023-06-30",
    leaf_name="rentenwert_m",
    unit=Unit.CURRENCY.PER_MONTH,
)
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
