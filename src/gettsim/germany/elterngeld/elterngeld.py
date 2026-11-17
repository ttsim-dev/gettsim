"""Elterngeld (parental leave benefit)."""

from __future__ import annotations

from gettsim.tt import (
    AggType,
    RoundingSpec,
    TTSIMUnit,
    agg_by_group_function,
    agg_by_p_id_function,
    cast_ttsim_unit,
    policy_function,
)


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.DIMENSIONLESS)
def ist_leistungsbegründendes_kind(
    alter_monate: int,
    max_bezugsmonate: dict[str, int],
) -> bool:
    """
    Determines whether the given person is considered a 'leistungsbegründendes Kind'
    (benefit-establishing child) for the purpose of parental leave benefits.

    A 'leistungsbegründende Person' is a person whose existence or characteristics give
    rise to a potential entitlement to a transfer benefit. This person is not
    necessarily the same as the benefit recipient or the one being evaluated for
    eligibility.

    This function returns True if the person is young enough to give rise to a potential
    Elterngeld claim.
    """
    # TODO(@MImmesberger): This age threshold is not correct once we account for
    # Elterngeld plus (currently not implemented).
    # https://github.com/ttsim-dev/gettsim/issues/151
    # The month budget belongs to the FG; here it bounds one child's age.
    return alter_monate <= cast_ttsim_unit(
        max_bezugsmonate["basismonate"] + max_bezugsmonate["partnermonate"],
        unit=TTSIMUnit.MONTHS,
    )


@agg_by_group_function(agg_type=AggType.ANY, unit=TTSIMUnit.DIMENSIONLESS.PER_FG)
def leistungsbegründende_kinder_in_fg(
    ist_leistungsbegründendes_kind: bool,
    fg_id: int,
) -> bool:
    pass


@agg_by_group_function(agg_type=AggType.SUM, unit=TTSIMUnit.DIMENSIONLESS.PER_FG)
def anzahl_mehrlinge_jüngstes_kind_fg(
    jüngstes_kind_oder_mehrling: bool,
    fg_id: int,
) -> int:
    pass


@agg_by_group_function(agg_type=AggType.SUM, unit=TTSIMUnit.DIMENSIONLESS.PER_FG)
def anzahl_anträge_fg(claimed: bool, fg_id: int) -> int:
    pass


@agg_by_p_id_function(
    leaf_name="bezugsmonate_partner",
    end_date="2022-12-31",
    agg_type=AggType.SUM,
    unit=TTSIMUnit.MONTHS,
)
def bezugsmonate_partner_bis_2022(
    bisherige_bezugsmonate: int,
    arbeitslosengeld_2__p_id_einstandspartner: int,
    p_id: int,
) -> int:
    pass


@agg_by_p_id_function(
    leaf_name="bezugsmonate_partner",
    start_date="2023-01-01",
    agg_type=AggType.SUM,
    unit=TTSIMUnit.MONTHS,
)
def bezugsmonate_partner_ab_2023(
    bisherige_bezugsmonate: int,
    bürgergeld__p_id_einstandspartner: int,
    p_id: int,
) -> int:
    pass


@policy_function(
    start_date="2011-01-01",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH, base=0.01, direction="down"
    ),
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_m(
    grundsätzlich_anspruchsberechtigt: bool,
    anspruchshöhe_m: float,
    angerechnete_mutterschaftsleistungen_m: float,
) -> float:
    """Parental leave benefit (Elterngeld) received by the parent.

    Mutterschaftsgeld is credited against the Elterngeld (§ 3 Abs. 1 S. 1 Nr. 1 BEEG).
    """
    if grundsätzlich_anspruchsberechtigt:
        return anspruchshöhe_m - angerechnete_mutterschaftsleistungen_m
    else:
        return 0.0


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def angerechnete_mutterschaftsleistungen_m(
    grundsätzlich_anspruchsberechtigt: bool,
    anspruchshöhe_m: float,
    sozialversicherung__kranken__mutterschaftsgeld_m: float,
) -> float:
    """Mutterschaftsgeld credited against the Elterngeld (§ 3 Abs. 1 S. 1 Nr. 1 BEEG).

    Only Mutterschaftsgeld for the time after the birth is credited. GETTSIM assumes
    that Mutterschaftsgeld received in a month with an Elterngeld claim relates to the
    same birth.
    """
    if grundsätzlich_anspruchsberechtigt:
        return min(sozialversicherung__kranken__mutterschaftsgeld_m, anspruchshöhe_m)
    else:
        return 0.0


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def basisbetrag_m(
    mean_nettoeinkommen_in_12_monaten_vor_geburt_m: float,
    lohnersatzanteil: float,
    anzurechnendes_nettoeinkommen_m: float,
    max_zu_berücksichtigendes_einkommen_m: float,
) -> float:
    """Base parental leave benefit without accounting for floor and ceiling.

    Basisbetrag is calculated on the parental level.

    """
    berücksichtigtes_einkommen = min(
        mean_nettoeinkommen_in_12_monaten_vor_geburt_m,
        max_zu_berücksichtigendes_einkommen_m,
    )
    return (
        berücksichtigtes_einkommen - anzurechnendes_nettoeinkommen_m
    ) * lohnersatzanteil


@policy_function(
    start_date="2007-01-01",
    end_date="2010-12-31",
    leaf_name="betrag_m",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH, base=0.01, direction="down"
    ),
    fail_msg_if_included="Elterngeld is not implemented prior to 2011.",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def elterngeld_not_implemented() -> float:
    pass


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def anspruchshöhe_m(
    basisbetrag_m: float,
    geschwisterbonus_m_fg: float,
    mehrlingsbonus_m_fg: float,
    mindestbetrag_m: float,
    höchstbetrag_m: float,
) -> float:
    """Elterngeld before checking eligibility.

    Anspruchshöhe is calculated on the parental level.

    """
    # Deliberate cross-level summation: FG-level bonuses are added to the
    # individual-level base amount
    kinderboni_m = cast_ttsim_unit(
        geschwisterbonus_m_fg + mehrlingsbonus_m_fg, unit=TTSIMUnit.CURRENCY.PER_MONTH
    )
    return (
        min(
            max(basisbetrag_m, mindestbetrag_m),
            höchstbetrag_m,
        )
        + kinderboni_m
    )


@policy_function(
    start_date="2007-01-01",
    end_date="2010-12-31",
    leaf_name="grundsätzlich_anspruchsberechtigt",
    unit=TTSIMUnit.DIMENSIONLESS,
)
def grundsätzlich_anspruchsberechtigt_ohne_maximales_vorjahreseinkommen(
    claimed: bool,
    arbeitsstunden_w: float,
    leistungsbegründende_kinder_in_fg: bool,
    bezugsmonate_unter_grenze_fg: bool,
    max_arbeitsstunden_w: int,
) -> bool:
    """Parent is eligible to receive Elterngeld."""
    return (
        claimed
        and arbeitsstunden_w <= max_arbeitsstunden_w
        and leistungsbegründende_kinder_in_fg
        and bezugsmonate_unter_grenze_fg
    )


@policy_function(
    start_date="2011-01-01",
    leaf_name="grundsätzlich_anspruchsberechtigt",
    unit=TTSIMUnit.DIMENSIONLESS,
)
def grundsätzlich_anspruchsberechtigt_mit_maximales_vorjahreseinkommen(
    claimed: bool,
    arbeitsstunden_w: float,
    leistungsbegründende_kinder_in_fg: bool,
    einkommen_vorjahr_unter_bezugsgrenze_sn: bool,
    bezugsmonate_unter_grenze_fg: bool,
    max_arbeitsstunden_w: int,
) -> bool:
    """Parent is eligible to receive Elterngeld.

    Maximum income in the previous year introduced via § 1 (8) BEEG.
    """
    return (
        claimed
        and arbeitsstunden_w <= max_arbeitsstunden_w
        and einkommen_vorjahr_unter_bezugsgrenze_sn
        and leistungsbegründende_kinder_in_fg
        and bezugsmonate_unter_grenze_fg
    )


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.DIMENSIONLESS.PER_FG)
def bezugsmonate_unter_grenze_fg(
    bisherige_bezugsmonate_fg: int,
    bezugsmonate_partner: int,
    familie__alleinerziehend: bool,
    anzahl_anträge_fg: int,
    max_bezugsmonate: dict[str, int],
) -> bool:
    """Elterngeld claimed for less than the maximum number of months in the past by the
    parent.

    """
    grenze_mit_partnermonaten_fg = (
        max_bezugsmonate["basismonate"] + max_bezugsmonate["partnermonate"]
    )
    # The Partnermonate are part of the FG's budget; here they are the months one
    # parent must have claimed for the FG to reach it.
    if familie__alleinerziehend or bezugsmonate_partner >= cast_ttsim_unit(
        max_bezugsmonate["partnermonate"], unit=TTSIMUnit.MONTHS
    ):
        out = bisherige_bezugsmonate_fg < grenze_mit_partnermonaten_fg
    elif anzahl_anträge_fg > cast_ttsim_unit(1, unit=TTSIMUnit.COUNT.PER_FG):
        out = (
            bisherige_bezugsmonate_fg + cast_ttsim_unit(1, unit=TTSIMUnit.MONTHS.PER_FG)
            < grenze_mit_partnermonaten_fg
        )
    else:
        out = bisherige_bezugsmonate_fg < max_bezugsmonate["basismonate"]
    return out


@policy_function(start_date="2011-01-01", unit=TTSIMUnit.DIMENSIONLESS)
def lohnersatzanteil(
    mean_nettoeinkommen_in_12_monaten_vor_geburt_m: float,
    lohnersatzanteil_einkommen_untere_grenze_m: float,
    lohnersatzanteil_einkommen_obere_grenze_m: float,
    einkommensschritte_korrektur_m: float,
    satz: float,
    prozent_korrektur: float,
    prozent_minimum: float,
    nettoeinkommensstufen_für_lohnersatzrate: dict[str, float],
) -> float:
    """Replacement rate of Elterngeld (before applying floor and ceiling rules).

    According to § 2 (2) BEEG the percentage increases below the first step and
    decreases above the second step until prozent_minimum.

    """
    # Higher replacement rate if considered income is below a threshold
    if (
        mean_nettoeinkommen_in_12_monaten_vor_geburt_m
        < nettoeinkommensstufen_für_lohnersatzrate["lower_threshold"]
        and mean_nettoeinkommen_in_12_monaten_vor_geburt_m > 0
    ):
        out = min(
            satz
            + (
                lohnersatzanteil_einkommen_untere_grenze_m
                / einkommensschritte_korrektur_m
                * prozent_korrektur
            ),
            1.0,
        )
    # Lower replacement rate if considered income is above a threshold
    elif (
        mean_nettoeinkommen_in_12_monaten_vor_geburt_m
        > nettoeinkommensstufen_für_lohnersatzrate["upper_threshold"]
    ):
        # Replacement rate is only lowered up to a specific value
        out = max(
            satz
            - (
                lohnersatzanteil_einkommen_obere_grenze_m
                / einkommensschritte_korrektur_m
                * prozent_korrektur
            ),
            prozent_minimum,
        )
    else:
        out = satz

    return out


@policy_function(start_date="2007-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def freibetrag_paragraph_10_abs_1_beeg_m(
    betrag_m: float,
    angerechnete_mutterschaftsleistungen_m: float,
    anzahl_mehrlinge_fg: int,
    mindestbetrag_m: float,
) -> float:
    """Elterngeld that does not count as income for other transfers.

    The Elterngeld together with the Mutterschaftsgeld credited against it remains
    exempt up to the Mindestbetrag per child (§ 10 Abs. 1 and 4 BEEG). Transfers that
    use this exemption subtract it from the full Lohn- und Einkommensersatzleistungen,
    which contain the paid Elterngeld and the Mutterschaftsgeld.
    """
    return min(
        betrag_m + angerechnete_mutterschaftsleistungen_m,
        (1 + cast_ttsim_unit(anzahl_mehrlinge_fg, unit=TTSIMUnit.DIMENSIONLESS))
        * mindestbetrag_m,
    )


@policy_function(
    start_date="2011-01-01",
    end_date="2012-09-17",
    leaf_name="freibetrag_paragraph_10_abs_5_beeg_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def freibetrag_paragraph_10_abs_5_beeg_m_ohne_angerechnete_einnahmen(
    betrag_m: float,
    mean_nettoeinkommen_in_12_monaten_vor_geburt_m: float,
    mindestbetrag_m: float,
) -> float:
    """Elterngeld that does not count as income for SGB II, SGB XII and Kinderzuschlag.

    The Elterngeld remains exempt in the amount of the income from employment before
    the birth, up to the Mindestbetrag (§ 10 Abs. 5 S. 2 BEEG, inserted by Art. 14 Nr. 4
    G. v. 09.12.2010, BGBl. I S. 1896). Unlike § 10 Abs. 4 BEEG for the other transfers,
    the exemption does not multiply with the number of children of a multiple birth.
    """
    # TODO(@MImmesberger): Arbeitslosengeld II and Kinderzuschlag do not use this
    # exemption yet.
    # https://github.com/ttsim-dev/gettsim/issues/549
    höchstbetrag = min(mean_nettoeinkommen_in_12_monaten_vor_geburt_m, mindestbetrag_m)
    return min(betrag_m, höchstbetrag)


@policy_function(
    start_date="2012-09-18",
    end_date="2022-12-31",
    leaf_name="freibetrag_paragraph_10_abs_5_beeg_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def freibetrag_paragraph_10_abs_5_beeg_m_mit_angerechneten_einnahmen(
    betrag_m: float,
    angerechnete_mutterschaftsleistungen_m: float,
    mean_nettoeinkommen_in_12_monaten_vor_geburt_m: float,
    mindestbetrag_m: float,
) -> float:
    """Elterngeld that does not count as income for SGB II, SGB XII and Kinderzuschlag.

    The Elterngeld together with the Mutterschaftsgeld credited against it remains
    exempt in the amount of the income from employment before the birth, up to the
    Mindestbetrag (§ 10 Abs. 5 S. 2 BEEG, amended by Art. 1 Nr. 10 c G. v. 10.09.2012,
    BGBl. I S. 1878). Unlike § 10 Abs. 4 BEEG for the other transfers, the exemption
    does not multiply with the number of children of a multiple birth.
    """
    # TODO(@MImmesberger): Arbeitslosengeld II and Kinderzuschlag do not use this
    # exemption yet.
    # https://github.com/ttsim-dev/gettsim/issues/549
    # TODO(@MImmesberger): The exemption halves for Elterngeld Plus (§ 10 Abs. 5 S. 3
    # BEEG).
    # https://github.com/ttsim-dev/gettsim/issues/151
    höchstbetrag = min(mean_nettoeinkommen_in_12_monaten_vor_geburt_m, mindestbetrag_m)
    return min(betrag_m + angerechnete_mutterschaftsleistungen_m, höchstbetrag)


@policy_function(
    start_date="2023-01-01",
    leaf_name="freibetrag_paragraph_10_abs_5_beeg_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def freibetrag_paragraph_10_abs_5_beeg_m_ohne_mutterschaftsgeld(
    betrag_m: float,
    mean_nettoeinkommen_in_12_monaten_vor_geburt_m: float,
    mindestbetrag_m: float,
) -> float:
    """Elterngeld that does not count as income for SGB II, SGB XII and Kinderzuschlag.

    The Elterngeld remains exempt in the amount of the income from employment before
    the birth, up to the Mindestbetrag (§ 10 Abs. 5 S. 2 BEEG). Mutterschaftsgeld
    credited against the Elterngeld no longer counts towards this exemption because it
    is exempt in full (§ 10 Abs. 5 S. 4 BEEG, inserted by Art. 12 Abs. 7 G. v.
    16.12.2022, BGBl. I S. 2328); the transfers subtract it themselves.
    """
    # TODO(@MImmesberger): The exemption halves for Elterngeld Plus (§ 10 Abs. 5 S. 3
    # BEEG).
    # https://github.com/ttsim-dev/gettsim/issues/151
    höchstbetrag = min(mean_nettoeinkommen_in_12_monaten_vor_geburt_m, mindestbetrag_m)
    return min(betrag_m, höchstbetrag)


@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
def jüngstes_kind_oder_mehrling(
    alter_monate: int,
    familie__alter_monate_jüngstes_mitglied_fg: int,
    ist_leistungsbegründendes_kind: bool,
) -> bool:
    """Check if person is the youngest child in the household or a twin, triplet, etc.
    of the youngest child.

    # ToDo: Check definition as relevant for Elterngeld. Currently, it is calculated as
    # ToDo: age not being larger than 0.1 of a month

    """
    return (
        (
            alter_monate
            - cast_ttsim_unit(
                familie__alter_monate_jüngstes_mitglied_fg, unit=TTSIMUnit.MONTHS
            )
        )
        < cast_ttsim_unit(0.1, unit=TTSIMUnit.MONTHS)
    ) and ist_leistungsbegründendes_kind
