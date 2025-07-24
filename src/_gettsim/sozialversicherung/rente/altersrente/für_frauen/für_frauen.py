"""Pathway for women.

Revoked for birth cohorts after 1951.
"""

from __future__ import annotations

from gettsim.tt import ConsecutiveIntLookupTableParamValue, policy_function


@policy_function(
    start_date="1989-12-18",
    end_date="2017-12-31",
    leaf_name="altersgrenze",
)
def altersgrenze_mit_staffelung(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Full retirement age (FRA) for women.

    FRA differs by birth cohort.

    Does not check for eligibility for this pathway into retirement.
    """
    birth_month_since_ad = geburtsjahr * 12 + (geburtsmonat - 1)
    return altersgrenze_gestaffelt.look_up(birth_month_since_ad)


@policy_function(
    start_date="1989-12-18",
    end_date="1996-09-26",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_mit_staffelung(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_vorzeitig_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Early retirement age (ERA) for Renten für Frauen.

    ERA depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.
    """
    birth_month_since_ad = geburtsjahr * 12 + (geburtsmonat - 1)
    return altersgrenze_vorzeitig_gestaffelt.look_up(birth_month_since_ad)


@policy_function(end_date="1997-12-15", leaf_name="grundsätzlich_anspruchsberechtigt")
def grundsätzlich_anspruchsberechtigt_ohne_prüfung_geburtsjahr(
    weiblich: bool,
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt: bool,
    pflichtsbeitragsjahre_ab_alter_40: float,
    mindestpflichtbeitragsjahre_ab_alter_40: int,
) -> bool:
    """Eligibility for Altersrente für Frauen (pension for women).

    Eligibility does not depend on birth year.

    Policy becomes inactive in 2018 because then all potential beneficiaries have
    reached the normal retirement age.
    """
    return (
        weiblich
        and sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        and pflichtsbeitragsjahre_ab_alter_40 > mindestpflichtbeitragsjahre_ab_alter_40
    )


@policy_function(
    start_date="1997-12-16",
    end_date="2017-12-31",
    leaf_name="grundsätzlich_anspruchsberechtigt",
)
def grundsätzlich_anspruchsberechtigt_mit_prüfung_geburtsjahr(
    weiblich: bool,
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt: bool,
    pflichtsbeitragsjahre_ab_alter_40: float,
    geburtsjahr: int,
    kohorte_abschaffung: int,
    mindestpflichtbeitragsjahre_ab_alter_40: int,
) -> bool:
    """Eligibility for Altersrente für Frauen (pension for women).

    Only individuals born before a certain year are eligible.

    Wartezeit 15 years, contributions for 10 years after age 40, being a woman. Policy
    becomes inactive in 2018 because then all potential beneficiaries have reached the
    normal retirement age.
    """
    return (
        weiblich
        and sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        and pflichtsbeitragsjahre_ab_alter_40 > mindestpflichtbeitragsjahre_ab_alter_40
        and geburtsjahr < kohorte_abschaffung
    )
