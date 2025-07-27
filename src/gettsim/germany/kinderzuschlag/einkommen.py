"""Income relevant for calculation of Kinderzuschlag."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.germany.param_types import (
    ElementExistenzminimum,
    ElementExistenzminimumNurKind,
    ExistenzminimumNachAufwendungenMitBildungUndTeilhabe,
    ExistenzminimumNachAufwendungenOhneBildungUndTeilhabe,
)
from gettsim.tt import (
    AggType,
    RoundingSpec,
    agg_by_group_function,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from gettsim.tt import RawParam


@agg_by_group_function(start_date="2005-01-01", agg_type=AggType.SUM)
def anzahl_kinder_bg(kindergeld__anzahl_ansprüche: int, bg_id: int) -> int:
    pass


@policy_function(start_date="2005-01-01")
def bruttoeinkommen_eltern_m(
    arbeitslosengeld_2__bruttoeinkommen_m: float,
    arbeitslosengeld_2__hat_kind_in_gleicher_bedarfsgemeinschaft: bool,
) -> float:
    """Calculate parental gross income for calculation of child benefit.

    This variable is used to check whether the minimum income threshold for child
    benefit is met.
    """
    # TODO(@MImmesberger): Treatment of children who live in their own BG may be wrong here.
    # https://github.com/ttsim-dev/gettsim/issues/1009
    if arbeitslosengeld_2__hat_kind_in_gleicher_bedarfsgemeinschaft:
        out = arbeitslosengeld_2__bruttoeinkommen_m
    else:
        out = 0.0

    return out


@policy_function(
    rounding_spec=RoundingSpec(base=10, direction="down", reference="§ 6a Abs. 4 BKGG"),
    start_date="2005-01-01",
    end_date="2019-06-30",
    leaf_name="nettoeinkommen_eltern_m",
)
def nettoeinkommen_eltern_m_mit_grober_rundung(
    arbeitslosengeld_2__nettoeinkommen_nach_abzug_freibetrag_m: float,
    arbeitslosengeld_2__hat_kind_in_gleicher_bedarfsgemeinschaft: bool,
) -> float:
    """Parental income (after deduction of taxes, social insurance contributions, and
    other deductions) for calculation of child benefit.
    """
    # TODO(@MImmesberger): Treatment of children who live in their own BG may be wrong here.
    # https://github.com/ttsim-dev/gettsim/issues/1009
    if arbeitslosengeld_2__hat_kind_in_gleicher_bedarfsgemeinschaft:
        out = arbeitslosengeld_2__nettoeinkommen_nach_abzug_freibetrag_m
    else:
        out = 0.0
    return out


@policy_function(
    rounding_spec=RoundingSpec(base=1, direction="down", reference="§ 11 Abs. 2 BKGG"),
    start_date="2019-07-01",
    leaf_name="nettoeinkommen_eltern_m",
)
def nettoeinkommen_eltern_m_mit_genauer_rundung(
    arbeitslosengeld_2__nettoeinkommen_nach_abzug_freibetrag_m: float,
    arbeitslosengeld_2__hat_kind_in_gleicher_bedarfsgemeinschaft: bool,
) -> float:
    """Parental income (after deduction of taxes, social insurance contributions, and
    other deductions) for calculation of child benefit.
    """
    # TODO(@MImmesberger): Treatment of children who live in their own BG may be wrong here.
    # https://github.com/ttsim-dev/gettsim/issues/1009
    if arbeitslosengeld_2__hat_kind_in_gleicher_bedarfsgemeinschaft:
        out = arbeitslosengeld_2__nettoeinkommen_nach_abzug_freibetrag_m
    else:
        out = 0.0
    return out


@policy_function(
    start_date="2005-01-01",
    end_date="2022-06-30",
    leaf_name="maximales_nettoeinkommen_m_bg",
)
def maximales_nettoeinkommen_m_bg_vor_06_2022(
    erwachsenenbedarf_m_bg: float,
    anzahl_kinder_bg: int,
    satz: float,
) -> float:
    """Calculate maximum income to be eligible for additional child benefit
    (Kinderzuschlag).

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).
    """
    return erwachsenenbedarf_m_bg + satz * anzahl_kinder_bg


@policy_function(
    start_date="2022-07-01",
    end_date="2022-12-31",
    leaf_name="maximales_nettoeinkommen_m_bg",
)
def maximales_nettoeinkommen_m_bg_ab_06_2022_bis_12_2022(
    erwachsenenbedarf_m_bg: float,
    anzahl_kinder_bg: int,
    arbeitslosengeld_2__kindersofortzuschlag: float,
    satz: float,
) -> float:
    """Calculate maximum income to be eligible for additional child benefit
    (Kinderzuschlag).

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).
    """
    return (
        erwachsenenbedarf_m_bg
        + satz * anzahl_kinder_bg
        + arbeitslosengeld_2__kindersofortzuschlag * anzahl_kinder_bg
    )


@policy_function(start_date="2023-01-01", leaf_name="maximales_nettoeinkommen_m_bg")
def maximales_nettoeinkommen_m_bg_ab_01_2023(
    erwachsenenbedarf_m_bg: float,
    anzahl_kinder_bg: int,
    satz: float,
) -> float:
    """Calculate maximum income to be eligible for additional child benefit
    (Kinderzuschlag).

    Kindersofortzuschlag is included in maximum Kinderzuschlag.

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).
    """
    return erwachsenenbedarf_m_bg + satz * anzahl_kinder_bg


@policy_function(start_date="2008-10-01")
def mindestbruttoeinkommen_m_bg(
    anzahl_kinder_bg: int,
    arbeitslosengeld_2__alleinerziehend_bg: bool,
    mindesteinkommen: dict[str, float],
) -> float:
    """Calculate minimal claim of child benefit (kinderzuschlag).

    Min income to be eligible for KIZ (different for singles and couples) (§6a (1) Nr. 2
    BKGG).
    """
    if anzahl_kinder_bg == 0:
        out = 0.0
    elif arbeitslosengeld_2__alleinerziehend_bg:
        out = mindesteinkommen["single"]
    else:
        out = mindesteinkommen["paar"]

    return out


@policy_function(start_date="2005-01-01")
def anzurechnendes_einkommen_eltern_m_bg(
    nettoeinkommen_eltern_m_bg: float,
    erwachsenenbedarf_m_bg: float,
    entzugsrate_elterneinkommen: float,
) -> float:
    """Calculate parental income subtracted from child benefit.

    (§6a (6) S. 3 BKGG)
    """
    out = entzugsrate_elterneinkommen * (
        nettoeinkommen_eltern_m_bg - erwachsenenbedarf_m_bg
    )

    return max(out, 0.0)


@policy_function(start_date="2005-01-01")
def kosten_der_unterkunft_m_bg(
    wohnbedarf_anteil_eltern_bg: float,
    arbeitslosengeld_2__bruttokaltmiete_m_bg: float,
    arbeitslosengeld_2__heizkosten_m_bg: float,
) -> float:
    """Calculate costs of living eligible to claim.

    Unlike ALG2, there is no check on whether living costs are "appropriate".
    """
    warmmiete_m_bg = (
        arbeitslosengeld_2__bruttokaltmiete_m_bg + arbeitslosengeld_2__heizkosten_m_bg
    )

    return wohnbedarf_anteil_eltern_bg * warmmiete_m_bg


@param_function(
    start_date="2005-01-01",
    end_date="2011-12-31",
    leaf_name="existenzminimum",
)
def existenzminimum_ohne_bildung_und_teilhabe(
    parameter_existenzminimum: RawParam,
) -> ExistenzminimumNachAufwendungenOhneBildungUndTeilhabe:
    """Regelsatz nach Regelbedarfsstufen."""
    regelsatz = ElementExistenzminimum(
        single=parameter_existenzminimum["regelsatz"]["single"],
        paar=parameter_existenzminimum["regelsatz"]["paar"],
        kind=parameter_existenzminimum["regelsatz"]["kind"],
    )
    kosten_der_unterkunft = ElementExistenzminimum(
        single=parameter_existenzminimum["kosten_der_unterkunft"]["single"],
        paar=parameter_existenzminimum["kosten_der_unterkunft"]["paar"],
        kind=parameter_existenzminimum["kosten_der_unterkunft"]["kind"],
    )
    heizkosten = ElementExistenzminimum(
        single=parameter_existenzminimum["heizkosten"]["single"],
        paar=parameter_existenzminimum["heizkosten"]["paar"],
        kind=parameter_existenzminimum["heizkosten"]["kind"],
    )
    return ExistenzminimumNachAufwendungenOhneBildungUndTeilhabe(
        regelsatz=regelsatz,
        kosten_der_unterkunft=kosten_der_unterkunft,
        heizkosten=heizkosten,
    )


@param_function(start_date="2012-01-01", leaf_name="existenzminimum")
def existenzminimum_mit_bildung_und_teilhabe(
    parameter_existenzminimum: RawParam,
) -> ExistenzminimumNachAufwendungenMitBildungUndTeilhabe:
    """Regelsatz nach Regelbedarfsstufen."""
    regelsatz = ElementExistenzminimum(
        single=parameter_existenzminimum["regelsatz"]["single"],
        paar=parameter_existenzminimum["regelsatz"]["paar"],
        kind=parameter_existenzminimum["regelsatz"]["kind"],
    )
    kosten_der_unterkunft = ElementExistenzminimum(
        single=parameter_existenzminimum["kosten_der_unterkunft"]["single"],
        paar=parameter_existenzminimum["kosten_der_unterkunft"]["paar"],
        kind=parameter_existenzminimum["kosten_der_unterkunft"]["kind"],
    )
    heizkosten = ElementExistenzminimum(
        single=parameter_existenzminimum["heizkosten"]["single"],
        paar=parameter_existenzminimum["heizkosten"]["paar"],
        kind=parameter_existenzminimum["heizkosten"]["kind"],
    )
    return ExistenzminimumNachAufwendungenMitBildungUndTeilhabe(
        regelsatz=regelsatz,
        kosten_der_unterkunft=kosten_der_unterkunft,
        heizkosten=heizkosten,
        bildung_und_teilhabe=ElementExistenzminimumNurKind(
            kind=parameter_existenzminimum["bildung_und_teilhabe"]["kind"],
        ),
    )


@policy_function(start_date="2005-01-01")
def wohnbedarf_anteil_eltern_bg(
    anzahl_kinder_bg: int,
    arbeitslosengeld_2__alleinerziehend_bg: bool,
    existenzminimum: ExistenzminimumNachAufwendungenOhneBildungUndTeilhabe
    | ExistenzminimumNachAufwendungenMitBildungUndTeilhabe,
    wohnbedarf_anteil_berücksichtigte_kinder: int,
) -> float:
    """Calculate living needs broken down to the parents. Defined as parents'
    subsistence level on housing, divided by sum of subsistence level from parents and
    children.

    Reference: § 6a Abs. 5 S. 3 BKGG
    """
    if arbeitslosengeld_2__alleinerziehend_bg:
        elternbetrag = (
            existenzminimum.kosten_der_unterkunft.single
            + existenzminimum.heizkosten.single
        )
    else:
        elternbetrag = (
            existenzminimum.kosten_der_unterkunft.paar + existenzminimum.heizkosten.paar
        )

    kinderbetrag = min(
        anzahl_kinder_bg,
        wohnbedarf_anteil_berücksichtigte_kinder,
    ) * (existenzminimum.kosten_der_unterkunft.kind + existenzminimum.heizkosten.kind)

    return elternbetrag / (elternbetrag + kinderbetrag)


@policy_function(start_date="2005-01-01")
def erwachsenenbedarf_m_bg(
    arbeitslosengeld_2__regelsatz_m_bg: float,
    kosten_der_unterkunft_m_bg: float,
) -> float:
    """Aggregate relevant income and rental costs."""
    return arbeitslosengeld_2__regelsatz_m_bg + kosten_der_unterkunft_m_bg
