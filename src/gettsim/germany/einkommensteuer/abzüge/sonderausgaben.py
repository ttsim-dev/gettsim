"""Tax allowances for special expenses."""

from __future__ import annotations

from gettsim.tt import (
    AggType,
    RoundingSpec,
    TTSIMUnit,
    agg_by_p_id_function,
    policy_function,
)


@agg_by_p_id_function(agg_type=AggType.SUM, unit=TTSIMUnit.CURRENCY.PER_MONTH)
def kinderbetreuungskosten_elternteil_m(
    kinderbetreuungskosten_m: float,
    p_id_kinderbetreuungskostenträger: int,
    p_id: int,
) -> float:
    pass


@policy_function(
    end_date="2011-12-31",
    leaf_name="sonderausgaben_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def sonderausgaben_y_sn_nur_pauschale(
    familie__anzahl_personen_sn: int,
    sonderausgabenpauschbetrag: float,
) -> float:
    """Sonderausgaben on Steuernummer level until 2011.

    Only a lump sum payment is implemented.

    Reference:
        - § 10c Abs. 1 EStG idF Art. 1 G. v. 19.12.2000 BGBl. I S. 1790
        - § 10c Satz 1 EStG idF Art. 1 G. v. 16.07.2009 BGBl. I S. 1959
    """
    return sonderausgabenpauschbetrag * familie__anzahl_personen_sn


@policy_function(
    start_date="2012-01-01",
    leaf_name="sonderausgaben_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def sonderausgaben_y_sn_mit_kinderbetreuung(
    absetzbare_kinderbetreuungskosten_y_sn: float,
    familie__anzahl_personen_sn: int,
    sonderausgabenpauschbetrag: float,
) -> float:
    """Sonderausgaben on Steuernummer level since 2012.

    We follow § 10 Abs. 1 Nr. 5 EStG. You can find
    details here https://www.buzer.de/s1.htm?a=10&g=estg.

    Reference:
        - § 10 Abs. 1 Nr. 5 Satz 1 EStG idF Art. 1 G. v. 01.11.2011 BGBl. I S. 2131
        - § 10c Satz 1 EStG idF Art. 1 G. v. 01.11.2011 BGBl. I S. 2131
    """
    return max(
        absetzbare_kinderbetreuungskosten_y_sn,
        sonderausgabenpauschbetrag * familie__anzahl_personen_sn,
    )


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def gedeckelte_kinderbetreuungskosten_y(
    kinderbetreuungskosten_elternteil_y: float,
    parameter_absetzbare_kinderbetreuungskosten: dict[str, float],
) -> float:
    """Individual deductible childcare cost for each individual child under 14.

    Reference: § 10 Abs. 1 Nr. 5 Satz 1 EStG idF Art. 1 G. v. 01.11.2011 BGBl. I S. 2131
    """
    return min(
        kinderbetreuungskosten_elternteil_y,
        parameter_absetzbare_kinderbetreuungskosten["maximum"],
    )


@policy_function(
    start_date="2002-01-01",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR.PER_SN,
        base=1,
        direction="up",
        reference="none (rounding in the tax assessment, not set by law)",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def absetzbare_kinderbetreuungskosten_y_sn(
    gedeckelte_kinderbetreuungskosten_y_sn: float,
    parameter_absetzbare_kinderbetreuungskosten: dict[str, float],
) -> float:
    """Sonderausgaben for childcare on Steuernummer level.

    We follow § 10 Abs. 1 Nr. 5 EStG. You can find
    details here https://www.buzer.de/s1.htm?a=10&g=estg.

    Reference: § 10 Abs. 1 Nr. 5 Satz 1 EStG idF Art. 1 G. v. 01.11.2011 BGBl. I S. 2131
    """

    return (
        gedeckelte_kinderbetreuungskosten_y_sn
        * parameter_absetzbare_kinderbetreuungskosten["anteil"]
    )
