"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def ist_hauptberuflich_selbstständig() -> bool:
    """Self-employed (main occupation).

    A person is self-employed as a main occupation if the self-employed activity clearly
    exceeds the other gainful activities in terms of economic significance and time use.
    """
