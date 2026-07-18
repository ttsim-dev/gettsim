from __future__ import annotations

from pathlib import Path

from ttsim.tt import UnitSystem

ROOT_PATH = Path(__file__).parent


UNIT_SYSTEM = UnitSystem(
    base_currency="EUR",
    other_currencies={"DM": "EUR / 1.95583"},
    statutory_currencies={"0001-01-01": "DM", "2002-01-01": "EUR"},
    grouping_levels=["hh", "ehe", "fg", "bg", "eg", "wthh", "sn"],
)


WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC = """
You requested (at least one of)

    - `bg_id`
    - `wthh_id`
    - `vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger`

from GETTSIM directly. Results will be correct only if there is exactly one
Familiengemeinschaft in one household and the Familiengemeinschaft coincides with the
Bedarfsgemeinschaft and the wohngeldrechtlicher Teilhaushalt.

If you plan to use more complex household and family structures (e.g. multiple families
within a household, households consisting of more than one generation -- with the
exception of parents and their children if they do not count as adults --, or families
with children who have enough income to fend for themselves, you can compute these IDs
by following the instructions in this repo:

    https://github.com/ttsim-dev/gettsim-crazy-grouping-rules

You can then pass the IDs obtained from there as input data to your main GETTSIM call.
"""
