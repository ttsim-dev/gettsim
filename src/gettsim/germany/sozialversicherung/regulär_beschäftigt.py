"""Regularly employed."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(end_date="2003-03-31", leaf_name="regulär_beschäftigt")
def regulär_beschäftigt_vor_midijob(
    einnahmen__bruttolohn_m: float,
    minijobgrenze: float,
) -> bool:
    """Employee is in regular employment, earning more than the marginal employment
    threshold."""
    return einnahmen__bruttolohn_m >= minijobgrenze


@policy_function(start_date="2003-04-01", leaf_name="regulär_beschäftigt")
def regulär_beschäftigt_mit_midijob(
    einnahmen__bruttolohn_m: float,
    midijobgrenze: float,
) -> bool:
    """Employee is in regular employment, earning more than the midijob threshold."""
    return einnahmen__bruttolohn_m >= midijobgrenze
