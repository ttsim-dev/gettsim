"""Input columns."""

from __future__ import annotations

from ttsim import policy_input


@policy_input()
def betrag_m() -> float:
    """Monthly rental income net of deductions."""
