from dataclasses import dataclass
from typing import Annotated

from gettsim.tt import TTSIMUnit


@dataclass(frozen=True)
class Altersgrenzen:
    min_alter: Annotated[int, TTSIMUnit.YEARS]
    max_alter: Annotated[int, TTSIMUnit.YEARS]


@dataclass(frozen=True)
class SatzMitAltersgrenzen:
    satz: Annotated[float, TTSIMUnit.CURRENCY.PER_MONTH]
    altersgrenzen: Altersgrenzen


@dataclass(frozen=True)
class ElementExistenzminimum:
    single: Annotated[float, TTSIMUnit.CURRENCY.PER_YEAR.PER_BG]
    """Annual combined amount for the sole adult of a Bedarfsgemeinschaft."""
    paar: Annotated[float, TTSIMUnit.CURRENCY.PER_YEAR.PER_BG]
    """Annual amount for a Bedarfsgemeinschaft's two adults together."""
    kind: Annotated[float, TTSIMUnit.CURRENCY.PER_YEAR]
    """Annual amount per child."""


@dataclass(frozen=True)
class ElementExistenzminimumNurKind:
    kind: Annotated[float, TTSIMUnit.CURRENCY.PER_YEAR]


@dataclass(frozen=True)
class ExistenzminimumNachAufwendungenOhneBildungUndTeilhabe:
    regelsatz: ElementExistenzminimum
    kosten_der_unterkunft: ElementExistenzminimum
    heizkosten: ElementExistenzminimum


@dataclass(frozen=True)
class ExistenzminimumNachAufwendungenMitBildungUndTeilhabe:
    regelsatz: ElementExistenzminimum
    kosten_der_unterkunft: ElementExistenzminimum
    heizkosten: ElementExistenzminimum
    bildung_und_teilhabe: ElementExistenzminimumNurKind
