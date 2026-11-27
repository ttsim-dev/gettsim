"""Pathway for the long-term insured."""

from __future__ import annotations

from ttsim.time_converters import y_to_m

from gettsim.tt import (
    ConsecutiveIntLookupTableParamValue,
    TTSIMUnit,
    policy_function,
)


@policy_function(
    start_date="1989-12-18",
    leaf_name="altersgrenze",
    unit=TTSIMUnit.YEARS,
    # `birth_month_since_ad` adds two CALENDAR_MONTH points
    # (`y_to_m(geburtsjahr) + geburtsmonat`), which pint's affine algebra forbids
    # (point + point).
    verify_units=False,
)
def altersgrenze_gestaffelt_ab_1989(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """
    Full retirement age (FRA) for long term insured.

    Calculate the age, at which a long term insured person (at least 35 years) is
    eligible to claim the full pension (without deductions). This pension scheme allows
    for early retirement (e.g. age 63) with deductions. Hence this threshold is needed
    as reference for calculating the zugangsfaktor.

    Does not check for eligibility for this pathway into retirement.

    Reference:
        - § 41 Abs. 2 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
        - § 41 Abs. 3 SGB VI idF Art. 1 Nr. 10 G. v. 25.09.1996 BGBl. I S. 1461
        - § 236 Abs. 1 SGB VI idF Art. 1 G. v. 16.12.1997 BGBl. I S. 2998
        - § 36 SGB VI idF Art. 1 G. v. 16.12.1997 BGBl. I S. 2998
        - § 236 Abs. 2 SGB VI idF Art. 1 G. v. 20.04.2007 BGBl. I S. 554
        - § 36 Satz 1 Nr. 1 SGB VI idF Art. 1 G. v. 20.04.2007 BGBl. I S. 554
    """
    birth_month_since_ad = y_to_m(geburtsjahr) + (geburtsmonat - 1)
    return altersgrenze_gestaffelt.look_up(birth_month_since_ad)


@policy_function(
    start_date="1989-12-18",
    end_date="1996-09-26",
    leaf_name="altersgrenze_vorzeitig",
    unit=TTSIMUnit.YEARS,
)
def altersgrenze_vorzeitig_gestaffelt_ab_1989_bis_1996(
    geburtsjahr: int,
    altersgrenze_vorzeitig_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Early retirement age (ERA) for Renten für langjährig Versicherte.

    Does not check for eligibility for this pathway into retirement.

    Reference: § 41 Abs. 2 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
    """
    return altersgrenze_vorzeitig_gestaffelt.look_up(geburtsjahr)


@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
def grundsätzlich_anspruchsberechtigt(
    sozialversicherung__rente__wartezeit_35_jahre_erfüllt: bool,
) -> bool:
    """Determining the eligibility for Altersrente für langjährig
    Versicherte (pension for long-term insured). Wartezeit 35 years and
    crossing the age threshold.

    Reference:
        - § 1248 Abs. 1 RVO idF Art. 1 G. v. 16.10.1972 BGBl. I S. 1965
        - § 36 Nr. 2 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
        - § 36 Nr. 2 SGB VI idF Art. 1 G. v. 16.12.1997 BGBl. I S. 2998
        - § 36 Satz 1 Nr. 2 SGB VI idF Art. 1 G. v. 20.04.2007 BGBl. I S. 554
    """
    return sozialversicherung__rente__wartezeit_35_jahre_erfüllt
