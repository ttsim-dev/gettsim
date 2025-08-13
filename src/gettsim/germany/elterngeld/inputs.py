"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def bisherige_bezugsmonate() -> int:
    """Number of months the individual received Elterngeld for the current youngest child."""


@policy_input()
def claimed() -> bool:
    """Individual claims Elterngeld."""


@policy_input()
def mean_nettoeinkommen_in_12_monaten_vor_geburt_m() -> float:
    """Mean net wage in the 12 months before birth of youngest child.

    To compute this value using GETTSIM set `('elterngeld',
    'mean_nettoeinkommen_für_bemessungsgrundlage_nach_geburt_m')` as the TT target and
    use input data from the last 12 months before the birth of the youngest child.
    """


@policy_input()
def zu_versteuerndes_einkommen_vorjahr_y_sn() -> float:
    """Taxable income in the calendar year prior to the youngest child's birth year.

    To compute this value using GETTSIM set `('einkommensteuer',
    'zu_versteuerndes_einkommen_y_sn')` as the TT target and use input data from the
    calendar year prior to the youngest child's birth year.
    """
