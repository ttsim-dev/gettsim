"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def anspruch_m() -> float:
    """Monthly gross alimony payments to be received as determined by the court."""


@policy_input()
def tatsächlich_erhaltener_betrag_m() -> float:
    """Alimony payments the recipient actually receives."""
