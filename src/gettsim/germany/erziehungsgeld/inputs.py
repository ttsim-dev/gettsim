"""Input columns."""

from __future__ import annotations

from gettsim.tt import FKType, Unit, policy_input


@policy_input(end_date="2008-12-31", unit=Unit.CURRENCY.PER_YEAR)
def bruttolohn_vorjahr_nach_abzug_werbungskosten_y() -> float:
    """Gross earnings of the previous calendar year minus Werbungskosten.

    To compute this value using GETTSIM set `('einkommensteuer', 'einkünfte',
    'aus_nichtselbstständiger_arbeit', 'einnahmen_nach_abzug_werbungskosten_y')` as the
    TT target and use input data from the calendar year prior to the youngest child's
    birth year.
    """


@policy_input(end_date="2008-12-31", unit=Unit.DIMENSIONLESS)
def budgetsatz() -> bool:
    """Applied for "Budgetsatz" of parental leave benefit."""


@policy_input(
    end_date="2008-12-31",
    foreign_key_type=FKType.MUST_NOT_POINT_TO_SELF,
    unit=Unit.DIMENSIONLESS,
)
def p_id_empfänger() -> int:
    pass
