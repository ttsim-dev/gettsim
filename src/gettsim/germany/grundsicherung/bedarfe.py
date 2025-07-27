from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from gettsim.germany.param_types import Altersgrenzen, SatzMitAltersgrenzen
from gettsim.tt import param_function

if TYPE_CHECKING:
    from gettsim.tt import RawParam


@dataclass(frozen=True)
class Regelbedarfsstufen:
    rbs_1: float
    rbs_2: float
    rbs_3: float
    rbs_4: SatzMitAltersgrenzen
    rbs_5: SatzMitAltersgrenzen
    rbs_6: SatzMitAltersgrenzen


@param_function(start_date="2011-01-01")
def regelbedarfsstufen(
    parameter_regelbedarfsstufen: RawParam,
) -> Regelbedarfsstufen:
    """Regelbedarfsstufen nach SGB XII § 28 (Anlage)."""
    rbs_4 = SatzMitAltersgrenzen(
        satz=parameter_regelbedarfsstufen[4]["betrag"],
        altersgrenzen=Altersgrenzen(
            min_alter=parameter_regelbedarfsstufen[4]["min_alter"],
            max_alter=parameter_regelbedarfsstufen[4]["max_alter"],
        ),
    )
    rbs_5 = SatzMitAltersgrenzen(
        satz=parameter_regelbedarfsstufen[5]["betrag"],
        altersgrenzen=Altersgrenzen(
            min_alter=parameter_regelbedarfsstufen[5]["min_alter"],
            max_alter=parameter_regelbedarfsstufen[5]["max_alter"],
        ),
    )
    rbs_6 = SatzMitAltersgrenzen(
        satz=parameter_regelbedarfsstufen[6]["betrag"],
        altersgrenzen=Altersgrenzen(
            min_alter=parameter_regelbedarfsstufen[6]["min_alter"],
            max_alter=parameter_regelbedarfsstufen[6]["max_alter"],
        ),
    )
    return Regelbedarfsstufen(
        rbs_1=parameter_regelbedarfsstufen[1],
        rbs_2=parameter_regelbedarfsstufen[2],
        rbs_3=parameter_regelbedarfsstufen[3],
        rbs_4=rbs_4,
        rbs_5=rbs_5,
        rbs_6=rbs_6,
    )
