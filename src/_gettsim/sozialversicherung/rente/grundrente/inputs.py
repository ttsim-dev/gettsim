"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input(start_date="2021-01-01")
def bewertungszeiten_monate() -> int:
    """Number of months determining amount of Grundrente."""


@policy_input(start_date="2021-01-01")
def grundrentenzeiten_monate() -> int:
    """Number of months determining eligibility for Grundrente."""


@policy_input(start_date="2021-01-01")
def mean_entgeltpunkte() -> float:
    """Mean Entgeltpunkte during Bewertungszeiten."""


@policy_input(start_date="2021-01-01")
def gesamteinnahmen_aus_renten_vorjahr_m() -> float:
    """Income from private and public pensions in the previous calendar year.

    GETTSIM can calculate this input based on the data of the previous calendar year using the
    target `('sozialversicherung', 'rente', 'grundrente', 'gesamteinnahmen_aus_renten_für_einkommensberechnung_im_folgejahr_m')`.
    """


@policy_input(start_date="2021-01-01")
def bruttolohn_vorjahr_y() -> float:
    """Earnings in the previous calendar year.

    Calculation is based on the 'Einnahmen' definitions of the basic tax law (EStG).
    """


@policy_input(start_date="2021-01-01")
def einnahmen_aus_selbstständiger_arbeit_vorvorjahr_y() -> float:
    """Earnings from self-employment 2 years before.

    Calculation is based on the 'Einnahmen' definitions of the basic tax law (EStG).
    """


@policy_input(start_date="2021-01-01")
def einnahmen_aus_vermietung_und_verpachtung_vorvorjahr_y() -> float:
    """Earnings from rental income 2 years before.

    Calculation is based on the 'Einnahmen' definitions of the basic tax law (EStG).
    """


@policy_input(start_date="2021-01-01")
def einnahmen_aus_kapitalvermögen_vorvorjahr_y() -> float:
    """Earnings from capital income 2 years before.

    Calculation is based on the 'Einnahmen' definitions of the basic tax law (EStG).
    """
