"""Public pension benefits."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def alter_bei_renteneintritt(
    jahr_renteneintritt: int,
    monat_renteneintritt: int,
    geburtsjahr: int,
    geburtsmonat: int,
) -> float:
    """Age at retirement in monthly precision.

    Calculates the age of person's retirement in monthly precision.
    As retirement is only possible at first day of month and as
    persons eligible for pension at first of month after reaching the
    age threshold (§ 99 SGB VI) persons who retire in same month will
    be considered a month too young. Hence, subtract 1/12.
    """
    return (
        jahr_renteneintritt
        - geburtsjahr
        + (monat_renteneintritt - geburtsmonat - 1) / 12
    )
