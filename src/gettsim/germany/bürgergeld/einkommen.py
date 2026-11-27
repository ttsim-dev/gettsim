"""Relevant income for Bürgergeld."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    PiecewisePolynomialParamValue,
    TTSIMUnit,
    piecewise_polynomial,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def anzurechnendes_einkommen_m(
    nettoeinkommen_nach_abzug_freibetrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    kindergeld_zur_bedarfsdeckung_m: float,
    kindergeldübertrag_m: float,
) -> float:
    """Relevant income according to SGB II.

    Note: If you are using GETTSIM and want to aggregate to BG/HH level (which is never
    required by the rules of the taxes and transfers system), you need to deduct
    `differenz_kindergeld_kindbedarf_m_hh` from the result of this function. This is
    necessary because the Kindergeld received by the child may enter
    `anzurechnendes_einkommen_m_hh` twice: once as Kindergeld and once as
    Kindergeldübertrag.

    Reference:
        - § 11 Abs. 1 Satz 1 SGB II idF Art. 1 G. v. 26.07.2016 BGBl. I S. 1824
        - § 11 Abs. 1 Satz 1 SGB II idF Art. 1 G. v. 16.12.2022 BGBl. I S. 2328
    """
    return (
        nettoeinkommen_nach_abzug_freibetrag_m
        + unterhalt__tatsächlich_erhaltener_betrag_m
        + unterhaltsvorschuss__betrag_m
        + kindergeld_zur_bedarfsdeckung_m
        + kindergeldübertrag_m
    )


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def nettoeinkommen_nach_abzug_freibetrag_m(
    nettoeinkommen_vor_abzug_freibetrag_m: float,
    anrechnungsfreies_einkommen_m: float,
) -> float:
    """Net income after deductions for calculation of basic subsistence.

    Reference: § 11b Abs. 3 Satz 1 SGB II idF Art. 2 G. v. 24.03.2011 BGBl. I S. 453
    """
    return nettoeinkommen_vor_abzug_freibetrag_m - anrechnungsfreies_einkommen_m


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def nettoeinkommen_vor_abzug_freibetrag_m(
    bruttoeinkommen_m: float,
    einkommensteuer__betrag_m_sn: float,
    solidaritätszuschlag__betrag_m_sn: float,
    familie__anzahl_personen_sn: int,
    sozialversicherung__beiträge_versicherter_m: float,
) -> float:
    """Net income for calculation of basic subsistence.

    Reference:
        - § 11b Abs. 1 Satz 1 Nr. 1 SGB II idF Art. 2 G. v. 24.03.2011 BGBl. I S. 453
        - § 11b Abs. 1 Satz 1 Nr. 2 SGB II idF Art. 2 G. v. 24.03.2011 BGBl. I S. 453
    """
    return (
        bruttoeinkommen_m
        - einkommensteuer__betrag_m_sn / familie__anzahl_personen_sn
        - solidaritätszuschlag__betrag_m_sn / familie__anzahl_personen_sn
        - sozialversicherung__beiträge_versicherter_m
    )


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def bruttoeinkommen_m(
    einnahmen__bruttolohn_m: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    einnahmen__kapitalerträge_m: float,
    einnahmen__renten__betrag_gesamt_m: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_m: float,
    einnahmen__lohn_und_einkommensersatzleistungen_m: float,
    elterngeld__freibetrag_paragraph_10_abs_5_beeg_m: float,
    sozialversicherung__kranken__mutterschaftsgeld_m: float,
) -> float:
    """Sum up the gross income for calculation of basic subsistence.

    Part of the Elterngeld is exempt (§ 10 Abs. 5 S. 2 BEEG). Mutterschaftsgeld is
    exempt in full (§ 10 Abs. 5 S. 4 BEEG; from 01.07.2023 also § 11a Abs. 1 Nr. 6 SGB
    II).

    Reference:
        - § 11 Abs. 1 Satz 1 SGB II idF Art. 1 G. v. 26.07.2016 BGBl. I S. 1824
        - § 11 Abs. 1 Satz 1 SGB II idF Art. 1 G. v. 16.12.2022 BGBl. I S. 2328
    """
    return (
        einnahmen__bruttolohn_m
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
        + einnahmen__kapitalerträge_m
        + einnahmen__renten__betrag_gesamt_m
        + einkommensteuer__einkünfte__sonstige__alle_weiteren_m
        + einnahmen__lohn_und_einkommensersatzleistungen_m
        - elterngeld__freibetrag_paragraph_10_abs_5_beeg_m
        - sozialversicherung__kranken__mutterschaftsgeld_m
    )


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def anrechnungsfreies_einkommen_m(
    einnahmen__bruttolohn_m: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    sozialversicherung__arbeitslosen__kurzarbeitergeld_m: float,
    sozialversicherung__arbeitslosen__insolvenzgeld_m: float,
    familie__anzahl_kinder_bis_17_bg: int,
    einkommensteuer__anzahl_kinderfreibeträge: int,
    parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg: PiecewisePolynomialParamValue,
    parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg: PiecewisePolynomialParamValue,
    xnp: ModuleType,
) -> float:
    """Share of income, which remains to the individual.

    Sozialgesetzbuch (SGB) Zweites Buch (II) - Bürgergeld, Grundsicherung für
    Arbeitsuchende. SGB II §11b Abs 3
    https://www.gesetze-im-internet.de/sgb_2/__11b.html

    Reference:
        - § 11b Abs. 2 Satz 1 SGB II idF Art. 1 G. v. 26.07.2016 BGBl. I S. 1824
        - § 11b Abs. 3 Satz 2 SGB II idF Art. 2 G. v. 02.06.2021 BGBl. I S. 1387
        - § 11b Abs. 3 Satz 2 SGB II idF Art. 1 G. v. 16.12.2022 BGBl. I S. 2328
        - § 11b Abs. 3 Satz 3 SGB II idF Art. 2 G. v. 24.03.2011 BGBl. I S. 453
    """
    # TODO(@MImmesberger): Should consider income from other sources too. Also,
    # thresholds for children might be different.
    # https://github.com/ttsim-dev/gettsim/issues/598

    # TODO(@MImmesberger): Insolvenzgeld enters as net, not as the underlying gross wage.
    # https://github.com/ttsim-dev/gettsim/issues/1244
    eink_erwerbstätigkeit = (
        einnahmen__bruttolohn_m
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        + sozialversicherung__arbeitslosen__kurzarbeitergeld_m
        + sozialversicherung__arbeitslosen__insolvenzgeld_m
    )

    if (
        familie__anzahl_kinder_bis_17_bg > 0
        or einkommensteuer__anzahl_kinderfreibeträge > 0
    ):
        out = piecewise_polynomial(
            x=eink_erwerbstätigkeit,
            parameters=parameter_anrechnungsfreies_einkommen_mit_kindern_in_bg,
            xnp=xnp,
        )
    else:
        out = piecewise_polynomial(
            x=eink_erwerbstätigkeit,
            parameters=parameter_anrechnungsfreies_einkommen_ohne_kinder_in_bg,
            xnp=xnp,
        )
    return out
