"""Marginally employed."""

from __future__ import annotations

from gettsim.tt import RoundingSpec, policy_function


@policy_function()
def geringfügig_beschäftigt(
    einnahmen__bruttolohn_m: float,
    minijobgrenze: float,
) -> bool:
    """Individual earns less than marginal employment threshold.

    Legal reference: § 8 Abs. 1 Satz 1 and 2 SGB IV
    """
    return einnahmen__bruttolohn_m <= minijobgrenze


@policy_function(
    start_date="1990-01-01",
    end_date="1999-12-31",
    leaf_name="minijobgrenze",
    rounding_spec=RoundingSpec(
        base=1,
        direction="up",
        reference="§ 8 Abs. 1a Satz 2 SGB IV",
    ),
)
def minijobgrenze_unterscheidung_ost_west(
    wohnort_ost_hh: bool,
    parameter_minijobgrenze_ost_west_unterschied: dict[str, float],
) -> float:
    """Minijob income threshold depending on place of living (East or West Germany).

    Until 1999, the threshold is different for East and West Germany.
    """
    return (
        parameter_minijobgrenze_ost_west_unterschied["ost"]
        if wohnort_ost_hh
        else parameter_minijobgrenze_ost_west_unterschied["west"]
    )


@policy_function(
    start_date="2022-10-01",
    leaf_name="minijobgrenze",
    rounding_spec=RoundingSpec(
        base=1,
        direction="up",
        reference="§ 8 Abs. 1a Satz 2 SGB IV",
    ),
)
def minijobgrenze_abgeleitet_von_mindestlohn(
    mindestlohn: float,
    faktoren_minijobformel: dict[str, float],
) -> float:
    """Minijob income threshold since 10/2022. Since then, it is calculated endogenously
    from the statutory minimum wage.
    """
    return (
        mindestlohn
        * faktoren_minijobformel["zähler"]
        / faktoren_minijobformel["nenner"]
    )
