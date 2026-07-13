from __future__ import annotations

from pathlib import Path

from ttsim.tt import (
    register_currency,
    register_statutory_currencies,
    register_unit_builder_levels,
)

ROOT_PATH = Path(__file__).parent

# Germany's currencies. Registered on import so the [currency] dimension has
# concrete currencies before the policy environment is assembled (GEP 10). The
# euro is the base currency; the Deutsche Mark is worth 1/1.95583 euro, the rate
# fixed by the Euro-Einführungsgesetz. The statutory-currency mapping tells the
# engine which currency each policy date computes in; it declares the euro for
# all dates, matching how pre-2002 parameters are stored today (hand-converted
# to euro). A follow-up flips it to DM through 2001 and re-transcribes those
# parameters to their statutory DM values.
register_currency(name="EUR", base=True)
register_currency(name="DM", definition="EUR / 1.95583")
register_statutory_currencies({"0001-01-01": "EUR"})

# Germany's grouping levels. Registered on import so the fluent unit builder
# offers `Unit.X.PER_HH` / `per_bg` / … before the policy modules (whose
# decorators use them) are loaded (GEP 10 compositional units).
register_unit_builder_levels(["hh", "ehe", "fg", "bg", "eg", "wthh", "sn"])


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
