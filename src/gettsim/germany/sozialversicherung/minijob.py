"""Marginally employed."""

from __future__ import annotations

from gettsim.tt import RoundingSpec, TTSIMUnit, policy_function


@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
def geringfügig_beschäftigt(
    einnahmen__bruttolohn_m: float,
    minijobgrenze_m: float,
) -> bool:
    """Individual earns less than marginal employment threshold.

    Reference:
        - § 8 Abs. 1 Nr. 1 SGB IV idF G. v. 04.11.1982 BGBl. I S. 1450
        - § 8 Abs. 1 Nr. 1 SGB IV idF Art. 1 Nr. 2 G. v. 24.03.1999 BGBl. I S. 388
        - § 8 Abs. 1 Nr. 1 SGB IV idF Art. 5 G. v. 21.12.2000 BGBl. I S. 1983
        - § 8 Abs. 1 Nr. 1 SGB IV idF Art. 2 G. v. 23.12.2002 BGBl. I S. 4621
        - § 8 Abs. 1 Nr. 1 SGB IV idF Art. 1 G. v. 05.12.2012 BGBl. I S. 2474
        - § 8 Abs. 1 Nr. 1 SGB IV idF Art. 7 G. v. 28.06.2022 BGBl. I S. 969
    """
    return einnahmen__bruttolohn_m <= minijobgrenze_m


@policy_function(
    start_date="1990-01-01",
    end_date="1999-03-31",
    leaf_name="minijobgrenze_m",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.DM.PER_MONTH,
        base=1,
        direction="up",
        reference=(
            "none (one seventh of the Bezugsgröße, which is set as a multiple of "
            "7 DM, so the threshold is a whole DM amount)"
        ),
    ),
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def minijobgrenze_unterscheidung_ost_west(
    wohnort_ost_hh: bool,
    parameter_minijobgrenze_ost_west_unterschied: dict[str, float],
) -> float:
    """Minijob income threshold depending on place of living (East or West Germany).

    Until March 1999, the threshold is different for East and West Germany.

    Reference: § 8 Abs. 1 Nr. 1 Buchst. b SGB IV idF G. v. 04.11.1982 BGBl. I S. 1450
    """
    return (
        parameter_minijobgrenze_ost_west_unterschied["ost"]
        if wohnort_ost_hh
        else parameter_minijobgrenze_ost_west_unterschied["west"]
    )


@policy_function(
    start_date="2022-10-01",
    leaf_name="minijobgrenze_m",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH,
        base=1,
        direction="up",
        reference="§ 8 Abs. 1a Satz 2 SGB IV idF Art. 7 G. v. 28.06.2022 BGBl. I S. 969",
    ),
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def minijobgrenze_abgeleitet_von_mindestlohn(
    mindestlohn: float,
    faktoren_minijobformel: dict[str, float],
) -> float:
    """Minijob income threshold since 10/2022. Since then, it is calculated endogenously
    from the statutory minimum wage.

    Reference: § 8 Abs. 1a SGB IV idF Art. 7 G. v. 28.06.2022 BGBl. I S. 969
    """
    return (
        mindestlohn
        * faktoren_minijobformel["zähler"]
        / faktoren_minijobformel["nenner"]
    )
