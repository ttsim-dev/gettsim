"""Contribution rate to public long-term care insurance."""

from __future__ import annotations

from gettsim.tt import (
    AggType,
    agg_by_p_id_function,
    param_function,
    policy_function,
)


@param_function(start_date="1995-01-01", end_date="2004-12-31")
def beitragssatz_arbeitnehmer(beitragssatz: float) -> float:
    """Employee's long-term care insurance contribution rate."""
    return beitragssatz / 2


@policy_function(
    start_date="2005-01-01",
    end_date="2023-06-30",
    leaf_name="beitragssatz_arbeitnehmer",
)
def beitragssatz_arbeitnehmer_zusatz_kinderlos_dummy(
    zahlt_zusatzbetrag_kinderlos: bool,
    beitragssatz_nach_kinderzahl: dict[str, float],
) -> float:
    """Employee's long-term care insurance contribution rate.

    Since 2005, the contribution rate is increased for childless individuals.
    """
    # Add additional contribution for childless individuals
    if zahlt_zusatzbetrag_kinderlos:
        out = (
            beitragssatz_nach_kinderzahl["standard"] / 2
            + beitragssatz_nach_kinderzahl["zusatz_kinderlos"]
        )
    else:
        out = beitragssatz_nach_kinderzahl["standard"] / 2

    return out


@policy_function(
    start_date="2023-07-01",
    leaf_name="beitragssatz_arbeitnehmer",
)
def beitragssatz_arbeitnehmer_mit_abschlag_nach_kinderzahl(
    anzahl_kinder_bis_24: int,
    zahlt_zusatzbetrag_kinderlos: bool,
    beitragssatz_nach_kinderzahl: dict[str, float],
) -> float:
    """Employee's long-term care insurance contribution rate.

    Since July 2023, the contribution rate is reduced for individuals with children
    younger than 25.
    """
    base = beitragssatz_nach_kinderzahl["standard"] / 2

    add = 0.0
    if zahlt_zusatzbetrag_kinderlos:
        add = add + beitragssatz_nach_kinderzahl["zusatz_kinderlos"]
    if anzahl_kinder_bis_24 > 1:
        add = add - beitragssatz_nach_kinderzahl["abschlag_für_kinder_bis_24"] * min(
            anzahl_kinder_bis_24 - 1,
            4,
        )

    return base + add


@policy_function(start_date="2005-01-01")
def zahlt_zusatzbetrag_kinderlos(
    hat_kinder: bool,
    alter: int,
    zusatz_kinderlos_mindestalter: int,
) -> bool:
    """Whether additional care insurance contribution for childless individuals applies.

    Not relevant before 2005 because the contribution rate was independent of the number
    of children.
    """
    return (not hat_kinder) and alter >= zusatz_kinderlos_mindestalter


@agg_by_p_id_function(agg_type=AggType.SUM, start_date="2005-01-01")
def anzahl_kinder_bis_24_elternteil_1(
    alter_bis_24: bool,
    einkommensteuer__p_id_kinderfreibetragsempfänger_1: int,
    p_id: int,
) -> int:
    pass


@agg_by_p_id_function(agg_type=AggType.SUM, start_date="2005-01-01")
def anzahl_kinder_bis_24_elternteil_2(
    alter_bis_24: bool,
    einkommensteuer__p_id_kinderfreibetragsempfänger_2: int,
    p_id: int,
) -> int:
    pass


@policy_function(start_date="2005-01-01")
def anzahl_kinder_bis_24(
    anzahl_kinder_bis_24_elternteil_1: int,
    anzahl_kinder_bis_24_elternteil_2: int,
) -> int:
    """Number of children under 25 years of age."""
    return anzahl_kinder_bis_24_elternteil_1 + anzahl_kinder_bis_24_elternteil_2


@param_function(
    start_date="1995-01-01",
    end_date="2004-12-31",
    leaf_name="beitragssatz_arbeitgeber",
)
def beitragssatz_arbeitgeber_einheitliche_basis(beitragssatz: float) -> float:
    """Employer's long-term care insurance contribution rate."""
    return beitragssatz / 2


@param_function(start_date="2005-01-01", leaf_name="beitragssatz_arbeitgeber")
def beitragssatz_arbeitgeber_basis_nach_kinderzahl(
    beitragssatz_nach_kinderzahl: dict[str, float],
) -> float:
    """Employer's long-term care insurance contribution rate."""
    return beitragssatz_nach_kinderzahl["standard"] / 2
