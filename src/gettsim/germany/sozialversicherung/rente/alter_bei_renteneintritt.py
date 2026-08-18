"""Public pension benefits."""

from __future__ import annotations

from ttsim.time_converters import m_to_y

from gettsim.tt import TTSIMUnit, cast_ttsim_unit, policy_function


@policy_function(unit=TTSIMUnit.YEARS)
def alter_bei_renteneintritt(
    jahr_renteneintritt: int,
    monat_renteneintritt: int,
    geburtsjahr: int,
    geburtsmonat: int,
) -> float:
    """Age at retirement in monthly precision.

    Calculates the age of person's retirement in monthly precision. As retirement is
    only possible at first day of month and as persons eligible for pension at first of
    month after reaching the age threshold (§ 99 SGB VI) persons who retire in same
    month will be considered a month too young. Hence, subtract 1 additional month from
    monat_renteneintritt.
    """
    return (
        jahr_renteneintritt
        - geburtsjahr
        + m_to_y(
            cast_ttsim_unit(monat_renteneintritt, unit=TTSIMUnit.MONTHS)
            - cast_ttsim_unit(geburtsmonat, unit=TTSIMUnit.MONTHS)
            - cast_ttsim_unit(1, unit=TTSIMUnit.MONTHS)
        )
    )
