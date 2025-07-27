"""Functions to compute parental leave benefits (Erziehungsgeld, -2007)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from gettsim.tt import (
    AggType,
    RoundingSpec,
    agg_by_group_function,
    agg_by_p_id_function,
    param_function,
    policy_function,
)

ErziehungsgeldSätze = Literal["regelsatz", "budgetsatz"]


@dataclass(frozen=True)
class Einkommensgrenze:
    regulär_alleinerziehend: dict[ErziehungsgeldSätze, float]
    regulär_paar: dict[ErziehungsgeldSätze, float]
    reduziert_alleinerziehend: dict[ErziehungsgeldSätze, float]
    reduziert_paar: dict[ErziehungsgeldSätze, float]


@param_function(
    start_date="2004-02-09",
    end_date="2008-12-31",
)
def einkommensgrenze(
    parameter_einkommensgrenze: dict[str, Any],
) -> Einkommensgrenze:
    """Parameter der Einkommensgrenze des Erziehungsgelds."""
    return Einkommensgrenze(
        regulär_alleinerziehend=parameter_einkommensgrenze["regulär_alleinerziehend"],
        regulär_paar=parameter_einkommensgrenze["regulär_paar"],
        reduziert_alleinerziehend=parameter_einkommensgrenze[
            "reduziert_alleinerziehend"
        ],
        reduziert_paar=parameter_einkommensgrenze["reduziert_paar"],
    )


@agg_by_group_function(end_date="2008-12-31", agg_type=AggType.ANY)
def leistungsbegründende_kinder_fg(
    ist_leistungsbegründendes_kind: bool,
    fg_id: int,
) -> bool:
    pass


@agg_by_p_id_function(end_date="2008-12-31", agg_type=AggType.SUM)
def anspruchshöhe_m(
    anspruchshöhe_kind_m: float,
    p_id_empfänger: int,
    p_id: int,
) -> float:
    pass


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def betrag_m(
    anspruchshöhe_m: float,
    grundsätzlich_anspruchsberechtigt: bool,
) -> float:
    """Total parental leave benefits (Erziehungsgeld) received by the parent.

    Legal reference: BErzGG (BGBl. I 1985 S. 2154; BGBl. I 2004 S. 206)
    """
    if grundsätzlich_anspruchsberechtigt:
        out = anspruchshöhe_m
    else:
        out = 0.0

    return out


@policy_function(
    end_date="2003-12-31",
    leaf_name="anspruchshöhe_kind_m",
    rounding_spec=RoundingSpec(base=0.01, direction="nearest"),
    fail_msg_if_included="""Erziehungsgeld is not implemented yet prior to 2004, see
https://github.com/ttsim-dev/gettsim/issues/673""",
)
def anspruchshöhe_kind_ohne_budgetsatz_m() -> float:
    pass


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    leaf_name="anspruchshöhe_kind_m",
    rounding_spec=RoundingSpec(base=0.01, direction="nearest"),
)
def anspruchshöhe_kind_mit_budgetsatz_m(
    ist_leistungsbegründendes_kind: bool,
    abzug_durch_einkommen_m_fg: float,
    basisbetrag_m: float,
) -> float:
    """Parental leave benefit (Erziehungsgeld) on child level.

    For the calculation, the relevant income, the age of the youngest child, the income
    threshold and the eligibility for erziehungsgeld is needed.

    Legal reference: BGBl I. v. 17.02.2004
    """
    if ist_leistungsbegründendes_kind:
        return max(basisbetrag_m - abzug_durch_einkommen_m_fg, 0.0)
    else:
        return 0.0


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def basisbetrag_m(
    budgetsatz: bool,
    anzurechnendes_einkommen_y_fg: float,
    einkommensgrenze_y_fg: float,
    alter_monate: int,
    altersgrenze_für_reduziertes_einkommenslimit_kind_monate: int,
    satz: dict[str, float],
) -> float:
    """Parental leave benefit (Erziehungsgeld) without means-test on child level."""
    if (
        anzurechnendes_einkommen_y_fg > einkommensgrenze_y_fg
        and alter_monate < altersgrenze_für_reduziertes_einkommenslimit_kind_monate
    ):
        out = 0.0
    elif budgetsatz:
        out = satz["budgetsatz"]
    else:
        out = satz["regelsatz"]

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def abzug_durch_einkommen_m_fg(
    anzurechnendes_einkommen_m_fg: float,
    einkommensgrenze_m_fg: float,
    alter_monate: int,
    altersgrenze_für_reduziertes_einkommenslimit_kind_monate: float,
    abschlagsfaktor: float,
) -> float:
    """Reduction of parental leave benefits (means-test).

    Legal reference: BGBl I. v. 17.02.2004 S.209
    """
    if (
        anzurechnendes_einkommen_m_fg > einkommensgrenze_m_fg
        and alter_monate >= altersgrenze_für_reduziertes_einkommenslimit_kind_monate
    ):
        out = anzurechnendes_einkommen_m_fg * abschlagsfaktor
    else:
        out = 0.0
    return out


@policy_function(
    start_date="2004-01-01",
    end_date="2006-12-10",
    leaf_name="ist_leistungsbegründendes_kind",
)
def _leistungsbegründendes_kind_vor_abschaffung(
    p_id_empfänger: int,
    alter_monate: int,
    budgetsatz: bool,
    maximales_kindsalter_budgetsatz: float,
    maximales_kindsalter_regelsatz: float,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on child level.

    Legal reference: BGBl I. v. 17.02.2004 S.207
    """
    if budgetsatz:
        out = p_id_empfänger >= 0 and alter_monate <= maximales_kindsalter_budgetsatz

    else:
        out = p_id_empfänger >= 0 and alter_monate <= maximales_kindsalter_regelsatz

    return out


@policy_function(
    start_date="2006-12-11",
    end_date="2008-12-31",
    leaf_name="ist_leistungsbegründendes_kind",
)
def _leistungsbegründendes_kind_nach_abschaffung(
    p_id_empfänger: int,
    geburtsjahr: int,
    alter_monate: int,
    budgetsatz: bool,
    abolishment_cohort: int,
    maximales_kindsalter_budgetsatz: float,
    maximales_kindsalter_regelsatz: float,
) -> bool:
    """
    Determines whether the given person is considered a 'leistungsbegründendes Kind'
    (benefit-establishing child) for the purpose of parental leave benefits.

    A 'leistungsbegründende Person' is a person whose existence or characteristics give
    rise to a potential entitlement to a transfer benefit. This person is not
    necessarily the same as the benefit recipient or the one being evaluated for
    eligibility.

    Abolished for children born after the cut-off date.

    Legal reference: BGBl I. v. 17.02.2004 S.207
    """
    if budgetsatz and geburtsjahr <= abolishment_cohort:
        out = p_id_empfänger >= 0 and alter_monate <= maximales_kindsalter_budgetsatz

    elif geburtsjahr <= abolishment_cohort:
        out = p_id_empfänger >= 0 and alter_monate <= maximales_kindsalter_regelsatz

    else:
        out = False

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def grundsätzlich_anspruchsberechtigt(
    arbeitsstunden_w: float,
    leistungsbegründende_kinder_fg: bool,
    maximale_wochenarbeitszeit: float,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on parental level.

    Legal reference: BGBl I. v. 17.02.2004 S.207
    """
    return leistungsbegründende_kinder_fg and (
        arbeitsstunden_w <= maximale_wochenarbeitszeit
    )


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def anzurechnendes_einkommen_y_fg(
    bruttolohn_vorjahr_nach_abzug_werbungskosten_y_fg: float,
    ist_leistungsbegründendes_kind: bool,
    pauschaler_abzug_vom_einkommen: float,
) -> float:
    """Income relevant for means testing for parental leave benefit (Erziehungsgeld).

    Legal reference: BGBl I. v. 17.02.2004 S.209

    There is special rule for "Beamte, Soldaten und Richter" which is not
    implemented yet.
    """
    if ist_leistungsbegründendes_kind:
        out = (
            bruttolohn_vorjahr_nach_abzug_werbungskosten_y_fg
            * pauschaler_abzug_vom_einkommen
        )
    else:
        out = 0.0
    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def einkommensgrenze_y_fg(
    einkommensgrenze_ohne_geschwisterbonus: float,
    familie__anzahl_kinder_fg: float,
    ist_leistungsbegründendes_kind: bool,
    aufschlag_einkommen: float,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld).

    Legal reference: BGBl I. v. 17.02.2004 S.208
    """
    if ist_leistungsbegründendes_kind:
        return (
            einkommensgrenze_ohne_geschwisterbonus
            + (familie__anzahl_kinder_fg - 1) * aufschlag_einkommen
        )
    else:
        return 0.0


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def einkommensgrenze_ohne_geschwisterbonus(
    alter_monate: int,
    einkommensgrenze_ohne_geschwisterbonus_kind_jünger_als_reduzierungsgrenze: float,
    einkommensgrenze_ohne_geschwisterbonus_kind_älter_als_reduzierungsgrenze: float,
    altersgrenze_für_reduziertes_einkommenslimit_kind_monate: float,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld) before adding the
    bonus for additional children.

    Legal reference: BGBl I. v. 17.02.2004 S.208
    """
    if alter_monate < altersgrenze_für_reduziertes_einkommenslimit_kind_monate:
        return einkommensgrenze_ohne_geschwisterbonus_kind_jünger_als_reduzierungsgrenze
    else:
        return einkommensgrenze_ohne_geschwisterbonus_kind_älter_als_reduzierungsgrenze


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def einkommensgrenze_ohne_geschwisterbonus_kind_jünger_als_reduzierungsgrenze(
    familie__alleinerziehend_fg: bool,
    budgetsatz: bool,
    einkommensgrenze: Einkommensgrenze,
) -> float:
    """Base income threshold for parents of children younger than the age threshold.

    Legal reference: BGBl I. v. 17.02.2004 S.208
    """
    if budgetsatz and familie__alleinerziehend_fg:
        return einkommensgrenze.regulär_alleinerziehend["budgetsatz"]
    elif budgetsatz and not familie__alleinerziehend_fg:
        return einkommensgrenze.regulär_paar["budgetsatz"]
    elif not budgetsatz and familie__alleinerziehend_fg:
        return einkommensgrenze.regulär_alleinerziehend["regelsatz"]
    else:
        return einkommensgrenze.regulär_paar["regelsatz"]


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def einkommensgrenze_ohne_geschwisterbonus_kind_älter_als_reduzierungsgrenze(
    familie__alleinerziehend_fg: bool,
    budgetsatz: bool,
    einkommensgrenze: Einkommensgrenze,
) -> float:
    """Base income threshold for parents of children older than age threshold.

    Legal reference: BGBl I. v. 17.02.2004 S.208
    """
    if budgetsatz and familie__alleinerziehend_fg:
        return einkommensgrenze.reduziert_alleinerziehend["budgetsatz"]
    elif budgetsatz and not familie__alleinerziehend_fg:
        return einkommensgrenze.reduziert_paar["budgetsatz"]
    elif not budgetsatz and familie__alleinerziehend_fg:
        return einkommensgrenze.reduziert_alleinerziehend["regelsatz"]
    else:
        return einkommensgrenze.reduziert_paar["regelsatz"]
