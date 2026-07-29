"""Functions to compute parental leave benefits (Erziehungsgeld, -2007)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any

from gettsim.tt import (
    UNSET_UNIT,
    AggType,
    RoundingSpec,
    TTSIMUnit,
    agg_by_group_function,
    agg_by_p_id_function,
    cast_ttsim_unit,
    param_function,
    policy_function,
)


@dataclass(frozen=True)
class EinkommensgrenzeNachSatz:
    """The Familiengemeinschaft's annual income thresholds, one per Satz."""

    regelsatz: Annotated[float, TTSIMUnit.CURRENCY.PER_YEAR.PER_FG]
    """Threshold applying to the Regelsatz."""
    budgetsatz: Annotated[float, TTSIMUnit.CURRENCY.PER_YEAR.PER_FG]
    """Threshold applying to the Budgetsatz."""


@dataclass(frozen=True)
class Einkommensgrenzen:
    """The income thresholds by household type and by the child's age bracket."""

    regulär_alleinerziehend: EinkommensgrenzeNachSatz
    """Single parent, child below the Reduzierungsgrenze."""
    regulär_paar: EinkommensgrenzeNachSatz
    """Couple, child below the Reduzierungsgrenze."""
    reduziert_alleinerziehend: EinkommensgrenzeNachSatz
    """Single parent, child at or above the Reduzierungsgrenze."""
    reduziert_paar: EinkommensgrenzeNachSatz
    """Couple, child at or above the Reduzierungsgrenze."""


@param_function(
    start_date="2004-02-09",
    end_date="2008-12-31",
    unit=UNSET_UNIT,
)
def einkommensgrenzen(
    parameter_einkommensgrenze: dict[str, Any],
) -> Einkommensgrenzen:
    """Parameter der Einkommensgrenze des Erziehungsgelds."""
    return Einkommensgrenzen(
        regulär_alleinerziehend=EinkommensgrenzeNachSatz(
            **parameter_einkommensgrenze["regulär_alleinerziehend"]
        ),
        regulär_paar=EinkommensgrenzeNachSatz(
            **parameter_einkommensgrenze["regulär_paar"]
        ),
        reduziert_alleinerziehend=EinkommensgrenzeNachSatz(
            **parameter_einkommensgrenze["reduziert_alleinerziehend"]
        ),
        reduziert_paar=EinkommensgrenzeNachSatz(
            **parameter_einkommensgrenze["reduziert_paar"]
        ),
    )


@agg_by_group_function(
    end_date="2008-12-31", agg_type=AggType.ANY, unit=TTSIMUnit.DIMENSIONLESS.PER_FG
)
def leistungsbegründende_kinder_fg(
    ist_leistungsbegründendes_kind: bool,
    fg_id: int,
) -> bool:
    pass


@agg_by_p_id_function(
    end_date="2008-12-31", agg_type=AggType.SUM, unit=TTSIMUnit.CURRENCY.PER_MONTH
)
def anspruchshöhe_m(
    anspruchshöhe_kind_m: float,
    p_id_empfänger: int,
    p_id: int,
) -> float:
    pass


@policy_function(
    start_date="2004-01-01", end_date="2008-12-31", unit=TTSIMUnit.CURRENCY.PER_MONTH
)
def betrag_m(
    anspruchshöhe_m: float,
    grundsätzlich_anspruchsberechtigt: bool,
) -> float:
    """Total parental leave benefits (Erziehungsgeld) received by the parent.

    Legal reference: BErzGG (BGBl. I 1985 S. 2154; BGBl. I 2004 S. 206)
    """
    return anspruchshöhe_m if grundsätzlich_anspruchsberechtigt else 0.0


@policy_function(
    start_date="2002-01-01",
    end_date="2003-12-31",
    leaf_name="anspruchshöhe_kind_m",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH, base=0.01, direction="nearest"
    ),
    fail_msg_if_included="""Erziehungsgeld is not implemented yet prior to 2004, see
https://github.com/ttsim-dev/gettsim/issues/673""",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def anspruchshöhe_kind_ohne_budgetsatz_m() -> float:
    pass


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    leaf_name="anspruchshöhe_kind_m",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH, base=0.01, direction="nearest"
    ),
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
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
        # Deliberate cross-level subtraction: The FG level income deduction is
        # subtracted from the individual level base amount
        return max(
            basisbetrag_m
            - cast_ttsim_unit(
                abzug_durch_einkommen_m_fg, unit=TTSIMUnit.CURRENCY.PER_MONTH
            ),
            0.0,
        )
    else:
        return 0.0


@policy_function(
    start_date="2004-01-01", end_date="2008-12-31", unit=TTSIMUnit.CURRENCY.PER_MONTH
)
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


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_FG,
)
def abzug_durch_einkommen_m_fg(
    anzurechnendes_einkommen_m_fg: float,
    einkommensgrenze_m_fg: float,
    alter_monate: int,
    altersgrenze_für_reduziertes_einkommenslimit_kind_monate: int,
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
    unit=TTSIMUnit.DIMENSIONLESS,
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
    unit=TTSIMUnit.DIMENSIONLESS,
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


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    unit=TTSIMUnit.DIMENSIONLESS,
)
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


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_FG,
)
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


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_FG,
)
def einkommensgrenze_y_fg(
    einkommensgrenze_ohne_geschwisterbonus_y_fg: float,
    familie__anzahl_kinder_fg: int,
    ist_leistungsbegründendes_kind: bool,
    erhöhung_einkommensgrenze_pro_kind_y: float,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld).

    Legal reference: BGBl I. v. 17.02.2004 S.208
    """
    if ist_leistungsbegründendes_kind:
        return (
            einkommensgrenze_ohne_geschwisterbonus_y_fg
            + (
                familie__anzahl_kinder_fg
                - cast_ttsim_unit(1, unit=TTSIMUnit.DIMENSIONLESS.PER_FG)
            )
            * erhöhung_einkommensgrenze_pro_kind_y
        )
    else:
        return 0.0


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_FG,
)
def einkommensgrenze_ohne_geschwisterbonus_y_fg(
    alter_monate: int,
    einkommensgrenze_ohne_geschwisterbonus_kind_jünger_als_reduzierungsgrenze_y_fg: float,
    einkommensgrenze_ohne_geschwisterbonus_kind_älter_als_reduzierungsgrenze_y_fg: float,
    altersgrenze_für_reduziertes_einkommenslimit_kind_monate: int,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld) before adding the
    bonus for additional children.

    Legal reference: BGBl I. v. 17.02.2004 S.208
    """
    if alter_monate < altersgrenze_für_reduziertes_einkommenslimit_kind_monate:
        return einkommensgrenze_ohne_geschwisterbonus_kind_jünger_als_reduzierungsgrenze_y_fg
    else:
        return einkommensgrenze_ohne_geschwisterbonus_kind_älter_als_reduzierungsgrenze_y_fg


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_FG,
)
def einkommensgrenze_ohne_geschwisterbonus_kind_jünger_als_reduzierungsgrenze_y_fg(
    familie__alleinerziehend_fg: bool,
    budgetsatz: bool,
    einkommensgrenzen: Einkommensgrenzen,
) -> float:
    """Base income threshold for parents of children younger than the age threshold.

    Legal reference: BGBl I. v. 17.02.2004 S.208
    """
    if budgetsatz and familie__alleinerziehend_fg:
        satz = einkommensgrenzen.regulär_alleinerziehend.budgetsatz
    elif budgetsatz and not familie__alleinerziehend_fg:
        satz = einkommensgrenzen.regulär_paar.budgetsatz
    elif not budgetsatz and familie__alleinerziehend_fg:
        satz = einkommensgrenzen.regulär_alleinerziehend.regelsatz
    else:
        satz = einkommensgrenzen.regulär_paar.regelsatz
    return satz


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_FG,
)
def einkommensgrenze_ohne_geschwisterbonus_kind_älter_als_reduzierungsgrenze_y_fg(
    familie__alleinerziehend_fg: bool,
    budgetsatz: bool,
    einkommensgrenzen: Einkommensgrenzen,
) -> float:
    """Base income threshold for parents of children older than age threshold.

    Legal reference: BGBl I. v. 17.02.2004 S.208
    """
    if budgetsatz and familie__alleinerziehend_fg:
        return einkommensgrenzen.reduziert_alleinerziehend.budgetsatz
    elif budgetsatz and not familie__alleinerziehend_fg:
        return einkommensgrenzen.reduziert_paar.budgetsatz
    elif not budgetsatz and familie__alleinerziehend_fg:
        return einkommensgrenzen.reduziert_alleinerziehend.regelsatz
    else:
        return einkommensgrenzen.reduziert_paar.regelsatz
