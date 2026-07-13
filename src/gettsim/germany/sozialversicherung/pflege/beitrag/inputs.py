"""Input columns."""

from __future__ import annotations

from gettsim.tt import Unit, policy_input


@policy_input(unit=Unit.DIMENSIONLESS)
def hat_kinder() -> bool:
    """Parent of at least one child (including children in other households,
    adopted, adult, and deceased children).
    """
