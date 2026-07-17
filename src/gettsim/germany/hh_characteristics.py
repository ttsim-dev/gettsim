from __future__ import annotations

from gettsim.tt import AggType, TTSIMUnit, agg_by_group_function


@agg_by_group_function(agg_type=AggType.COUNT, unit=TTSIMUnit.PERSON_COUNT.PER_HH)
def anzahl_personen_hh(hh_id: int) -> int:
    pass
