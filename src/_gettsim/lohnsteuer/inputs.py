"""Input columns."""

from __future__ import annotations

from ttsim import policy_input


@policy_input()
def steuerklasse() -> int:
    """Tax Bracket (1 to 5) for withholding tax."""
