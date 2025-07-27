from dataclasses import dataclass


@dataclass(frozen=True)
class Altersgrenzen:
    min_alter: int
    max_alter: int


@dataclass(frozen=True)
class SatzMitAltersgrenzen:
    satz: float
    altersgrenzen: Altersgrenzen


@dataclass(frozen=True)
class ElementExistenzminimum:
    single: float
    paar: float
    kind: float


@dataclass(frozen=True)
class ElementExistenzminimumNurKind:
    kind: float


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
