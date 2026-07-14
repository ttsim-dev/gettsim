from dataclasses import dataclass
from typing import Annotated

from gettsim.tt import Unit


@dataclass(frozen=True)
class Altersgrenzen:
    min_alter: Annotated[int, Unit.YEARS]
    max_alter: Annotated[int, Unit.YEARS]


@dataclass(frozen=True)
class SatzMitAltersgrenzen:
    satz: Annotated[float, Unit.CURRENCY.PER_MONTH]
    altersgrenzen: Altersgrenzen


@dataclass(frozen=True)
class ElementExistenzminimum:
    single: Annotated[float, Unit.CURRENCY.PER_YEAR]
    paar: Annotated[float, Unit.CURRENCY.PER_YEAR]
    kind: Annotated[float, Unit.CURRENCY.PER_YEAR]


@dataclass(frozen=True)
class ElementExistenzminimumNurKind:
    kind: Annotated[float, Unit.CURRENCY.PER_YEAR]


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
