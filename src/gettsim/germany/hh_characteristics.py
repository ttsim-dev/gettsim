from __future__ import annotations

from gettsim.tt import AggType, agg_by_group_function, policy_function


@agg_by_group_function(agg_type=AggType.SUM)
def anzahl_volljährige_hh(familie__volljährig: bool, hh_id: int) -> int:
    pass


@agg_by_group_function(agg_type=AggType.SUM)
def anzahl_rentenbezieher_hh(
    sozialversicherung__rente__bezieht_rente: bool,
    hh_id: int,
) -> int:
    pass


@agg_by_group_function(agg_type=AggType.COUNT)
def anzahl_personen_hh(hh_id: int) -> int:
    pass


@policy_function()
def hat_regelaltersgrenze_erreicht(
    alter: int,
    sozialversicherung__rente__altersrente__regelaltersrente__altersgrenze: float,
) -> bool:
    """Whether the person has reached the Regelaltersgrenze.

    Reference: §41 Abs. 1 SGB XII, §7 Abs. 1 Satz 1 Nr. 1 SGB II
    """
    return (
        alter >= sozialversicherung__rente__altersrente__regelaltersrente__altersgrenze
    )


@policy_function()
def volljährige_alle_rentenbezieher_hh(
    anzahl_volljährige_hh: int,
    anzahl_rentenbezieher_hh: int,
) -> bool:
    """Calculate if all adults in the household are pensioners."""
    return anzahl_volljährige_hh == anzahl_rentenbezieher_hh
