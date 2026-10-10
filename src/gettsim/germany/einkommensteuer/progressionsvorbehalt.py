"""Progressionsvorbehalt for wage-replacement benefits (§ 32b EStG).

The benefits of § 32b Abs. 1 S. 1 Nr. 1 EStG are exempt from income tax but enter the
calculation of the tax rate via the Steuersatzeinkommen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    RoundingSpec,
    TTSIMUnit,
    cast_ttsim_unit,
    piecewise_polynomial,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType


@policy_function(start_date="1990-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def nicht_abziehbarer_arbeitnehmerpauschbetrag_y(
    einkünfte__aus_nichtselbstständiger_arbeit__werbungskosten_y: float,
    einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag: float,
    einnahmen__bruttolohn_y: float,
) -> float:
    """Part of the Arbeitnehmer-Pauschbetrag not deductible from wage income.

    § 32b Abs. 2 S. 1 Nr. 1 EStG deducts the Pauschbetrag from the benefits "soweit er
    nicht bei der Ermittlung der Einkünfte aus nichtselbständiger Arbeit abziehbar
    ist". Against wages it is deductible up to the amount of the wages (§ 9a S. 2
    EStG), so the remainder above the wages is left for the benefits. Nothing is left
    when actual Werbungskosten above the Pauschbetrag are deducted from wages (H 32b
    EStH 'Arbeitnehmer-Pauschbetrag'; BFH v. 25.09.2014, III R 61/12).
    """
    if (
        einkünfte__aus_nichtselbstständiger_arbeit__werbungskosten_y
        > einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag
    ):
        out = 0.0
    else:
        out = max(
            einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag
            - einnahmen__bruttolohn_y,
            0.0,
        )
    return out


@policy_function(start_date="1990-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def dem_progressionsvorbehalt_unterliegende_leistungen_y(
    einnahmen__lohn_und_einkommensersatzleistungen_y: float,
    einnahmen__zurückgezahlte_lohn_und_einkommensersatzleistungen_y: float,
    nicht_abziehbarer_arbeitnehmerpauschbetrag_y: float,
) -> float:
    """Benefits subject to the Progressionsvorbehalt.

    The benefits net of repayments, less the part of the Arbeitnehmer-Pauschbetrag
    not deductible from wage income (§ 32b Abs. 2 S. 1 Nr. 1 EStG). The Pauschbetrag
    reduces positive net benefits to zero at most and is not subtracted from a net
    repayment. The sum over the Steuernummer is added to the taxable income to obtain
    the Steuersatzeinkommen and may be negative.

    The 1990 wording ("die Summe der bezogenen Leistungen", Steuerreformgesetz 1990,
    BT-Drs. 11/2157) was rephrased by the Jahressteuergesetz 1996 to "vermehrt oder
    vermindert"; for wage-replacement benefits this codified the existing procedure
    ("insoweit entsprechend dem bisher angewendeten Verfahren", BT-Drs. 13/901, p.
    136), so one rule applies throughout.
    """
    netto = (
        einnahmen__lohn_und_einkommensersatzleistungen_y
        - einnahmen__zurückgezahlte_lohn_und_einkommensersatzleistungen_y
    )
    if netto > 0.0:
        out = max(netto - nicht_abziehbarer_arbeitnehmerpauschbetrag_y, 0.0)
    else:
        out = netto
    return out


@policy_function(start_date="1990-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def steuersatzeinkommen_ohne_kinderfreibetrag_y_sn(
    gesamteinkommen_y_sn: float,
    dem_progressionsvorbehalt_unterliegende_leistungen_y_sn: float,
) -> float:
    """Steuersatzeinkommen without Kinderfreibetrag (§ 32b Abs. 2 EStG)."""
    return (
        gesamteinkommen_y_sn + dem_progressionsvorbehalt_unterliegende_leistungen_y_sn
    )


@policy_function(start_date="1990-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def steuersatzeinkommen_mit_kinderfreibetrag_y_sn(
    zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn: float,
    dem_progressionsvorbehalt_unterliegende_leistungen_y_sn: float,
) -> float:
    """Steuersatzeinkommen with Kinderfreibetrag (§ 32b Abs. 2 EStG)."""
    return (
        zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
        + dem_progressionsvorbehalt_unterliegende_leistungen_y_sn
    )


@policy_function(
    start_date="2002-01-01",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S. 1 und Abs. 5 EStG",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def steuersatzeinkommen_je_person_ohne_kinderfreibetrag_y(
    steuersatzeinkommen_ohne_kinderfreibetrag_y_sn: float,
    familie__anzahl_personen_sn: int,
) -> float:
    """Steuersatzeinkommen per person of the Steuernummer, without Kinderfreibetrag.

    The amount the tariff is applied to under the splitting procedure, rounded down to
    a full Euro amount.
    """
    return steuersatzeinkommen_ohne_kinderfreibetrag_y_sn / familie__anzahl_personen_sn


@policy_function(
    start_date="2002-01-01",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S. 6 EStG",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def steuer_auf_steuersatzeinkommen_je_person_ohne_kinderfreibetrag_y(
    steuersatzeinkommen_je_person_ohne_kinderfreibetrag_y: float,
    parameter_einkommensteuertarif: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Tariff tax on the Steuersatzeinkommen per person, without Kinderfreibetrag.

    Summed over the Steuernummer, this is the tariff tax on the Steuersatzeinkommen
    (§ 32a Abs. 5 EStG).
    """
    return piecewise_polynomial(
        x=steuersatzeinkommen_je_person_ohne_kinderfreibetrag_y,
        parameters=parameter_einkommensteuertarif,
        xnp=xnp,
    )


@policy_function(
    start_date="2002-01-01",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S. 1 und Abs. 5 EStG",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def steuersatzeinkommen_je_person_mit_kinderfreibetrag_y(
    steuersatzeinkommen_mit_kinderfreibetrag_y_sn: float,
    familie__anzahl_personen_sn: int,
) -> float:
    """Steuersatzeinkommen per person of the Steuernummer, with Kinderfreibetrag.

    The amount the tariff is applied to under the splitting procedure, rounded down to
    a full Euro amount.
    """
    return steuersatzeinkommen_mit_kinderfreibetrag_y_sn / familie__anzahl_personen_sn


@policy_function(
    start_date="2002-01-01",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR,
        base=1,
        direction="down",
        reference="§ 32a Abs. 1 S. 6 EStG",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def steuer_auf_steuersatzeinkommen_je_person_mit_kinderfreibetrag_y(
    steuersatzeinkommen_je_person_mit_kinderfreibetrag_y: float,
    parameter_einkommensteuertarif: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Tariff tax on the Steuersatzeinkommen per person, with Kinderfreibetrag.

    Summed over the Steuernummer, this is the tariff tax on the Steuersatzeinkommen
    (§ 32a Abs. 5 EStG).
    """
    return piecewise_polynomial(
        x=steuersatzeinkommen_je_person_mit_kinderfreibetrag_y,
        parameters=parameter_einkommensteuertarif,
        xnp=xnp,
    )


@policy_function(
    start_date="1990-01-01",
    rounding_spec=RoundingSpec(
        base=1e-6,
        direction="down",
        reference=(
            "H 32b EStH 'Allgemeines', Beispiele (Fall B: 11,9567 %); "
            "Bescheid in FG Brandenburg, VZ 2017 (19,3919 %)"
        ),
    ),
    unit=TTSIMUnit.DIMENSIONLESS,
)
def besonderer_steuersatz_ohne_kinderfreibetrag(
    steuer_auf_steuersatzeinkommen_je_person_ohne_kinderfreibetrag_y_sn: float,
    steuersatzeinkommen_ohne_kinderfreibetrag_y_sn: float,
) -> float:
    """Besonderer Steuersatz (§ 32b Abs. 2 EStG) without Kinderfreibetrag.

    The tariff tax on the Steuersatzeinkommen divided by the Steuersatzeinkommen,
    truncated to four decimals of a percent; zero when the Steuersatzeinkommen is zero
    or negative.
    """
    if steuersatzeinkommen_ohne_kinderfreibetrag_y_sn > 0.0:
        # A share of two Steuernummer totals; GEP 10 ('Restricted group calculations',
        # rule 5) requires an explicit cast for dividing two group quantities.
        out = cast_ttsim_unit(
            steuer_auf_steuersatzeinkommen_je_person_ohne_kinderfreibetrag_y_sn,
            unit=TTSIMUnit.CURRENCY.PER_YEAR,
        ) / cast_ttsim_unit(
            steuersatzeinkommen_ohne_kinderfreibetrag_y_sn,
            unit=TTSIMUnit.CURRENCY.PER_YEAR,
        )
    else:
        out = 0.0
    return out


@policy_function(
    start_date="1990-01-01",
    rounding_spec=RoundingSpec(
        base=1e-6,
        direction="down",
        reference=(
            "H 32b EStH 'Allgemeines', Beispiele (Fall B: 11,9567 %); "
            "Bescheid in FG Brandenburg, VZ 2017 (19,3919 %)"
        ),
    ),
    unit=TTSIMUnit.DIMENSIONLESS,
)
def besonderer_steuersatz_mit_kinderfreibetrag(
    steuer_auf_steuersatzeinkommen_je_person_mit_kinderfreibetrag_y_sn: float,
    steuersatzeinkommen_mit_kinderfreibetrag_y_sn: float,
) -> float:
    """Besonderer Steuersatz (§ 32b Abs. 2 EStG) with Kinderfreibetrag.

    The tariff tax on the Steuersatzeinkommen divided by the Steuersatzeinkommen,
    truncated to four decimals of a percent; zero when the Steuersatzeinkommen is zero
    or negative.
    """
    if steuersatzeinkommen_mit_kinderfreibetrag_y_sn > 0.0:
        # A share of two Steuernummer totals; GEP 10 ('Restricted group calculations',
        # rule 5) requires an explicit cast for dividing two group quantities.
        out = cast_ttsim_unit(
            steuer_auf_steuersatzeinkommen_je_person_mit_kinderfreibetrag_y_sn,
            unit=TTSIMUnit.CURRENCY.PER_YEAR,
        ) / cast_ttsim_unit(
            steuersatzeinkommen_mit_kinderfreibetrag_y_sn,
            unit=TTSIMUnit.CURRENCY.PER_YEAR,
        )
    else:
        out = 0.0
    return out
