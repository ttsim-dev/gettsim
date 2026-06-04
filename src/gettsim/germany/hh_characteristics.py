from __future__ import annotations

from gettsim.tt import AggType, agg_by_group_function


@agg_by_group_function(agg_type=AggType.COUNT)
def anzahl_personen_hh(hh_id: int) -> int:
    pass
