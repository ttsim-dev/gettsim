"""Regularly employed."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(
    end_date="2003-03-31",
    leaf_name="regulär_beschäftigt",
    unit=TTSIMUnit.DIMENSIONLESS,
)
def regulär_beschäftigt_vor_midijob(
    einnahmen__bruttolohn_m: float,
    minijobgrenze_m: float,
) -> bool:
    """Employee is in regular employment, earning more than the marginal employment
    threshold.

    Reference:
        - § 8 Abs. 1 Nr. 1 SGB IV idF G. v. 04.11.1982 BGBl. I S. 1450
        - § 8 Abs. 1 Nr. 1 SGB IV idF Art. 1 Nr. 2 G. v. 24.03.1999 BGBl. I S. 388
    """
    return einnahmen__bruttolohn_m >= minijobgrenze_m


@policy_function(
    start_date="2003-04-01",
    leaf_name="regulär_beschäftigt",
    unit=TTSIMUnit.DIMENSIONLESS,
)
def regulär_beschäftigt_mit_midijob(
    einnahmen__bruttolohn_m: float,
    midijobgrenze_m: float,
) -> bool:
    """Employee is in regular employment, earning more than the midijob threshold.

    Reference:
        - § 20 Abs. 2 SGB IV idF Art. 2 Nr. 5 G. v. 23.12.2002 BGBl. I S. 4621
        - § 20 Abs. 2 SGB IV idF Art. 4 G. v. 28.11.2018 BGBl. I S. 2016
    """
    return einnahmen__bruttolohn_m >= midijobgrenze_m
