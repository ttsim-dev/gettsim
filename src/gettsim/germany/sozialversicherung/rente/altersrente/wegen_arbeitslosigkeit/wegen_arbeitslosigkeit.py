"""Pathway for unemployed individuals.

Revoked for birth cohorts after 1951.

In GETTSIM, this pathway becomes inactive at 2017-12-31 because by then statutory
retirement ages of this pathway were irrelevant (all potentially eligible individuals
are older than the Regelaltersgrenze).
"""

from __future__ import annotations

from gettsim.tt import ConsecutiveIntLookupTableParamValue, policy_function


@policy_function(
    start_date="1989-12-18",
    end_date="1996-07-28",
    leaf_name="altersgrenze",
)
def altersgrenze_bis_1996(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Does not check for eligibility for this pathway into retirement.
    """
    birth_month_since_ad = geburtsjahr * 12 + (geburtsmonat - 1)

    return altersgrenze_gestaffelt.look_up(birth_month_since_ad)


@policy_function(
    start_date="1996-07-29",
    end_date="2009-12-31",
    leaf_name="altersgrenze",
)
def altersgrenze_mit_vertrauensschutzprüfung(
    vertrauensschutz_1997: bool,
    altersgrenze_mit_vertrauensschutz: float,
    altersgrenze_ohne_vertrauensschutz: float,
) -> float:
    """Full retirement age for unemployed with Vertrauensschutz.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2010
    because then all potential beneficiaries have reached the Regelaltersgrenze.

    Does not check for eligibility for this pathway into retirement.
    """
    if vertrauensschutz_1997:
        return altersgrenze_mit_vertrauensschutz
    else:
        return altersgrenze_ohne_vertrauensschutz


@policy_function(
    start_date="2010-01-01",
    end_date="2017-12-31",
    leaf_name="altersgrenze",
)
def altersgrenze_ab_2010(
    altersgrenze_ohne_vertrauensschutz: float,
) -> float:
    """Full retirement age for unemployed.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2017
    because then all potential beneficiaries have reached the Regelaltersgrenze.

    Does not check for eligibility for this pathway into retirement.
    """
    return altersgrenze_ohne_vertrauensschutz


@policy_function(
    start_date="1989-12-18",
    end_date="1996-07-28",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_ohne_vertrauensschutz_bis_1996_07(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_vorzeitig_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Early retirement age of pension for unemployed.

    Does not check for eligibility for this pathway into retirement.
    """
    birth_month_since_ad = geburtsjahr * 12 + (geburtsmonat - 1)

    return altersgrenze_vorzeitig_gestaffelt.look_up(birth_month_since_ad)


@policy_function(
    start_date="1996-07-29",
    end_date="1996-09-26",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_mit_vertrauensschutzprüfung_ab_07_1996_bis_09_1996(
    vertrauensschutz_1997: bool,
    altersgrenze_vorzeitig_ohne_vertrauensschutz: float,
    altersgrenze_vorzeitig_mit_vertrauensschutz: float,
) -> float:
    """Early retirement age of pension for unemployed.

    Includes Vertrauensschutz rules implemented from July to September 1996.

    Does not check for eligibility for this pathway into retirement.
    """
    if vertrauensschutz_1997:
        return altersgrenze_vorzeitig_mit_vertrauensschutz
    else:
        return altersgrenze_vorzeitig_ohne_vertrauensschutz


@policy_function(
    start_date="2004-07-26",
    end_date="2017-12-31",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_mit_vertrauensschutzprüfung_ab_07_2004(
    vertrauensschutz_2004: bool,
    altersgrenze_vorzeitig_ohne_vertrauensschutz: float,
    altersgrenze_vorzeitig_mit_vertrauensschutz: float,
) -> float:
    """Early retirement age of pension for unemployed.

    Includes Vertrauensschutz rules implemented in July 2004. Policy becomes inactive in
    2018 because then all potential beneficiaries have reached the normal retirement
    age.

    Does not check for eligibility for this pathway into retirement.
    """
    if vertrauensschutz_2004:
        return altersgrenze_vorzeitig_mit_vertrauensschutz
    else:
        return altersgrenze_vorzeitig_ohne_vertrauensschutz


@policy_function(start_date="1989-12-18", end_date="2017-12-31")
def altersgrenze_ohne_vertrauensschutz(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Full retirement age depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.
    """
    birth_month_since_ad = geburtsjahr * 12 + (geburtsmonat - 1)

    return altersgrenze_gestaffelt.look_up(birth_month_since_ad)


@policy_function(start_date="1996-07-29", end_date="2009-12-31")
def altersgrenze_mit_vertrauensschutz(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_gestaffelt_vertrauensschutz: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Full retirement age for unemployed for individuals under Vertrauensschutz."""
    birth_month_since_ad = geburtsjahr * 12 + (geburtsmonat - 1)

    return altersgrenze_gestaffelt_vertrauensschutz.look_up(birth_month_since_ad)


@policy_function(
    start_date="1989-12-18",
    end_date="1996-09-26",
    leaf_name="altersgrenze_vorzeitig_ohne_vertrauensschutz",
)
def altersgrenze_vorzeitig_ohne_vertrauensschutz_ab_12_1989_bis_09_1996(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_vorzeitig_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Early retirement age of pension for unemployed without Vertrauensschutz.

    Relevant if the early retirement age depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.
    """
    birth_month_since_ad = geburtsjahr * 12 + (geburtsmonat - 1)

    return altersgrenze_vorzeitig_gestaffelt.look_up(birth_month_since_ad)


@policy_function(
    start_date="2004-07-26",
    end_date="2017-12-31",
    leaf_name="altersgrenze_vorzeitig_ohne_vertrauensschutz",
)
def altersgrenze_vorzeitig_ohne_vertrauensschutz_ab_07_2004(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_vorzeitig_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Early retirement age of pension for unemployed without Vertrauensschutz.

    Relevant if the early retirement age depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.
    """
    birth_month_since_ad = geburtsjahr * 12 + (geburtsmonat - 1)

    return altersgrenze_vorzeitig_gestaffelt.look_up(birth_month_since_ad)


@policy_function(end_date="2007-04-29", leaf_name="grundsätzlich_anspruchsberechtigt")
def grundsätzlich_anspruchsberechtigt_ohne_prüfung_geburtsjahr(
    arbeitslos_für_1_jahr_nach_alter_58_ein_halb: bool,
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt: bool,
    pflichtbeitragsjahre_8_von_10: bool,
) -> bool:
    """Eligibility for Altersrente für Arbeitslose (pension for unemployed).

    Wartezeit 15 years, 8 contribution years past 10 years, being unemployed for at
    least 1 year after age 58 and 6 months. The person is also required to be
    unemployed at the time of claiming the pension. As there are no restrictions
    regarding voluntary unemployment this requirement may be viewed as always satisfied
    and is therefore not included when checking for eligibility.
    """
    return (
        arbeitslos_für_1_jahr_nach_alter_58_ein_halb
        and sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        and pflichtbeitragsjahre_8_von_10
    )


@policy_function(
    start_date="2007-04-30",
    end_date="2017-12-31",
    leaf_name="grundsätzlich_anspruchsberechtigt",
)
def grundsätzlich_anspruchsberechtigt_mit_prüfung_geburtsjahr(
    arbeitslos_für_1_jahr_nach_alter_58_ein_halb: bool,
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt: bool,
    pflichtbeitragsjahre_8_von_10: bool,
    geburtsjahr: int,
    kohorte_abschaffung: int,
) -> bool:
    """Eligibility for Altersrente für Arbeitslose (pension for unemployed).

    Wartezeit 15 years, 8 contributionyears past 10 years, being at least 1 year
    unemployed after age 58 and 6 months and being born before 1952. The person is also
    required to be unemployed at the time of claiming the pension. As there are no
    restrictions regarding voluntary unemployment this requirement may be viewed as
    always satisfied and is therefore not included when checking for eligibility. Policy
    becomes inactive in 2018 because then all potential beneficiaries have reached the
    Regelaltersgrenze.
    """
    return (
        arbeitslos_für_1_jahr_nach_alter_58_ein_halb
        and sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        and pflichtbeitragsjahre_8_von_10
        and geburtsjahr < kohorte_abschaffung
    )
