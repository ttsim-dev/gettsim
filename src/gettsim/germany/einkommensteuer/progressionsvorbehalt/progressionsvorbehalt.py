"""Progressionsvorbehalt for wage-replacement benefits (§ 32b EStG).

The benefits of § 32b Abs. 1 S. 1 Nr. 1 EStG (summed in
`einnahmen__lohn_und_einkommensersatzleistungen_y`) are exempt from income tax but
enter the rate that applies to the taxable income. The Steuersatzeinkommen is the
taxable income plus these benefits, less repayments of such benefits
(`zurückgezahlte_leistungen_y`); the besonderer Steuersatz is the tariff tax on the
Steuersatzeinkommen divided by the Steuersatzeinkommen. Foreign income under the
Progressionsvorbehalt (§ 32b Abs. 1 S. 1 Nr. 2 to 5 EStG) is not modelled.
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
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__werbungskosten_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag: float,
    einnahmen__bruttolohn_y: float,
) -> float:
    """Arbeitnehmer-Pauschbetrag not deductible from wage income.

    § 32b Abs. 2 Nr. 1 EStG deducts the Pauschbetrag from the benefits "soweit er nicht
    bei der Ermittlung der Einkünfte aus nichtselbständiger Arbeit abziehbar ist".
    Nothing is left when Werbungskosten above the Pauschbetrag were deducted from
    wages.
    """
    if (
        einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__werbungskosten_y
        > einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag
    ):
        out = 0.0
    else:
        out = max(
            einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__arbeitnehmerpauschbetrag
            - einnahmen__bruttolohn_y,
            0.0,
        )
    return out


@policy_function(start_date="1990-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def leistungen_nach_abzug_arbeitnehmerpauschbetrag_y(
    einnahmen__lohn_und_einkommensersatzleistungen_y: float,
    zurückgezahlte_leistungen_y: float,
    nicht_abziehbarer_arbeitnehmerpauschbetrag_y: float,
) -> float:
    """Benefits net of repayments, less the Arbeitnehmer-Pauschbetrag not deductible
    from wage income.

    § 32b Abs. 2 Nr. 1 EStG. The deduction reduces a positive net amount to zero at
    most; a negative net amount is not reduced further.
    """
    netto = (
        einnahmen__lohn_und_einkommensersatzleistungen_y - zurückgezahlte_leistungen_y
    )
    if netto > 0.0:
        out = max(netto - nicht_abziehbarer_arbeitnehmerpauschbetrag_y, 0.0)
    else:
        out = netto
    return out


@policy_function(
    start_date="1990-01-01",
    end_date="1995-12-31",
    leaf_name="einzubeziehende_leistungen_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def einzubeziehende_leistungen_y_sn_nur_erhöhend(
    leistungen_nach_abzug_arbeitnehmerpauschbetrag_y_sn: float,
) -> float:
    """Benefits added to the taxable income to obtain the Steuersatzeinkommen.

    § 32b Abs. 2 Nr. 1 EStG as of the Steuerreformgesetz 1990 (Art. 1 Nr. 28 G. v.
    25.07.1988 BGBl. I S. 1093): the benefits are "einbezogen", so a negative sum does
    not lower the rate.
    """
    return max(leistungen_nach_abzug_arbeitnehmerpauschbetrag_y_sn, 0.0)


@policy_function(
    start_date="1996-01-01",
    leaf_name="einzubeziehende_leistungen_y_sn",
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def einzubeziehende_leistungen_y_sn_erhöhend_oder_mindernd(
    leistungen_nach_abzug_arbeitnehmerpauschbetrag_y_sn: float,
) -> float:
    """Benefits added to the taxable income to obtain the Steuersatzeinkommen.

    § 32b Abs. 2 EStG as of the Jahressteuergesetz 1996 (Art. 1 Nr. 30 G. v. 11.10.1995
    BGBl. I S. 1250): the taxable income is "vermehrt oder vermindert", so a negative
    sum lowers the rate.
    """
    return leistungen_nach_abzug_arbeitnehmerpauschbetrag_y_sn


@policy_function(start_date="1990-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def steuersatzeinkommen_ohne_kinderfreibetrag_y_sn(
    einkommensteuer__gesamteinkommen_y_sn: float,
    einzubeziehende_leistungen_y_sn: float,
) -> float:
    """Steuersatzeinkommen without Kinderfreibetrag.

    The income on which the besonderer Steuersatz is computed: the taxable income plus
    `einzubeziehende_leistungen_y_sn` (§ 32b Abs. 2 EStG).
    """
    return einkommensteuer__gesamteinkommen_y_sn + einzubeziehende_leistungen_y_sn


@policy_function(start_date="1990-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def steuersatzeinkommen_mit_kinderfreibetrag_y_sn(
    einkommensteuer__zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn: float,
    einzubeziehende_leistungen_y_sn: float,
) -> float:
    """Steuersatzeinkommen with Kinderfreibetrag.

    The income on which the besonderer Steuersatz is computed: the taxable income plus
    `einzubeziehende_leistungen_y_sn` (§ 32b Abs. 2 EStG).
    """
    return (
        einkommensteuer__zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
        + einzubeziehende_leistungen_y_sn
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
    einkommensteuer__parameter_einkommensteuertarif: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Tariff tax on the Steuersatzeinkommen per person, without Kinderfreibetrag."""
    return piecewise_polynomial(
        x=steuersatzeinkommen_je_person_ohne_kinderfreibetrag_y,
        parameters=einkommensteuer__parameter_einkommensteuertarif,
        xnp=xnp,
    )


@policy_function(start_date="2002-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def steuer_auf_steuersatzeinkommen_ohne_kinderfreibetrag_y_sn(
    steuer_auf_steuersatzeinkommen_je_person_ohne_kinderfreibetrag_y: float,
    familie__anzahl_personen_sn: int,
) -> float:
    """Tariff tax on the Steuersatzeinkommen of the Steuernummer, without Kinderfreibetrag.

    The tax per person times the number of persons (§ 32a Abs. 5 EStG).
    """
    return (
        familie__anzahl_personen_sn
        * steuer_auf_steuersatzeinkommen_je_person_ohne_kinderfreibetrag_y
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
    einkommensteuer__parameter_einkommensteuertarif: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Tariff tax on the Steuersatzeinkommen per person, with Kinderfreibetrag."""
    return piecewise_polynomial(
        x=steuersatzeinkommen_je_person_mit_kinderfreibetrag_y,
        parameters=einkommensteuer__parameter_einkommensteuertarif,
        xnp=xnp,
    )


@policy_function(start_date="2002-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def steuer_auf_steuersatzeinkommen_mit_kinderfreibetrag_y_sn(
    steuer_auf_steuersatzeinkommen_je_person_mit_kinderfreibetrag_y: float,
    familie__anzahl_personen_sn: int,
) -> float:
    """Tariff tax on the Steuersatzeinkommen of the Steuernummer, with Kinderfreibetrag.

    The tax per person times the number of persons (§ 32a Abs. 5 EStG).
    """
    return (
        familie__anzahl_personen_sn
        * steuer_auf_steuersatzeinkommen_je_person_mit_kinderfreibetrag_y
    )


@policy_function(
    start_date="1990-01-01",
    rounding_spec=RoundingSpec(
        base=1e-6,
        direction="down",
        reference="H 32b EStH 'Allgemeines', Beispiele",
    ),
    unit=TTSIMUnit.DIMENSIONLESS,
)
def besonderer_steuersatz_ohne_kinderfreibetrag(
    steuer_auf_steuersatzeinkommen_ohne_kinderfreibetrag_y_sn: float,
    steuersatzeinkommen_ohne_kinderfreibetrag_y_sn: float,
) -> float:
    """Besonderer Steuersatz (§ 32b Abs. 2 EStG) without Kinderfreibetrag.

    The tariff tax on the Steuersatzeinkommen divided by the Steuersatzeinkommen,
    truncated to four decimals of a percent as in the examples of H 32b EStH
    'Allgemeines'; zero when the Steuersatzeinkommen is zero or negative.
    """
    if steuersatzeinkommen_ohne_kinderfreibetrag_y_sn > 0.0:
        # The ratio of two totals of the same Steuernummer carries no level.
        out = cast_ttsim_unit(
            steuer_auf_steuersatzeinkommen_ohne_kinderfreibetrag_y_sn,
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
        reference="H 32b EStH 'Allgemeines', Beispiele",
    ),
    unit=TTSIMUnit.DIMENSIONLESS,
)
def besonderer_steuersatz_mit_kinderfreibetrag(
    steuer_auf_steuersatzeinkommen_mit_kinderfreibetrag_y_sn: float,
    steuersatzeinkommen_mit_kinderfreibetrag_y_sn: float,
) -> float:
    """Besonderer Steuersatz (§ 32b Abs. 2 EStG) with Kinderfreibetrag.

    The tariff tax on the Steuersatzeinkommen divided by the Steuersatzeinkommen,
    truncated to four decimals of a percent as in the examples of H 32b EStH
    'Allgemeines'; zero when the Steuersatzeinkommen is zero or negative.
    """
    if steuersatzeinkommen_mit_kinderfreibetrag_y_sn > 0.0:
        # The ratio of two totals of the same Steuernummer carries no level.
        out = cast_ttsim_unit(
            steuer_auf_steuersatzeinkommen_mit_kinderfreibetrag_y_sn,
            unit=TTSIMUnit.CURRENCY.PER_YEAR,
        ) / cast_ttsim_unit(
            steuersatzeinkommen_mit_kinderfreibetrag_y_sn,
            unit=TTSIMUnit.CURRENCY.PER_YEAR,
        )
    else:
        out = 0.0
    return out
