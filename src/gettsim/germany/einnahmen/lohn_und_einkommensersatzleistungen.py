"""Lohn- und Einkommensersatzleistungen (§ 32b Abs. 1 S. 1 Nr. 1 EStG).

The wage-replacement benefits that are exempt from income tax but subject to the
Progressionsvorbehalt. Their sum also counts as income for several transfers.

Implemented benefits of the catalogue:

- Buchst. a: Arbeitslosengeld, Kurzarbeitergeld, Insolvenzgeld
- Buchst. b and c: Krankengeld, Mutterschaftsgeld, Verletztengeld
- Buchst. j: Elterngeld

Not implemented: the other benefits of Buchst. a to c (e.g. Übergangsgeld, the
Zuschuss zum Mutterschaftsgeld) and Buchst. d to i and k.
"""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def lohn_und_einkommensersatzleistungen_ohne_elterngeld_m(
    sozialversicherung__arbeitslosen__betrag_m: float,
    sozialversicherung__arbeitslosen__kurzarbeitergeld_m: float,
    sozialversicherung__arbeitslosen__insolvenzgeld_m: float,
    sozialversicherung__kranken__krankengeld_m: float,
    sozialversicherung__kranken__mutterschaftsgeld_m: float,
    sozialversicherung__unfall__verletztengeld_m: float,
) -> float:
    """Sum of the benefits under § 32b Abs. 1 S. 1 Nr. 1 EStG except Elterngeld.

    Reference:
        - § 32b Abs. 1 Nr. 1 EStG idF Art. 1 G. v. 15.12.2003 BGBl. I S. 2645
        - § 32b Abs. 1 Nr. 1 EStG idF Art. 2 G. v. 05.12.2006 BGBl. I S. 2748
        - § 32b Abs. 1 Satz 1 Nr. 1 EStG idF Art. 1 G. v. 19.12.2008 BGBl. I S. 2794
    """
    return (
        sozialversicherung__arbeitslosen__betrag_m
        + sozialversicherung__arbeitslosen__kurzarbeitergeld_m
        + sozialversicherung__arbeitslosen__insolvenzgeld_m
        + sozialversicherung__kranken__krankengeld_m
        + sozialversicherung__kranken__mutterschaftsgeld_m
        + sozialversicherung__unfall__verletztengeld_m
    )


@policy_function(
    end_date="2006-12-31",
    leaf_name="lohn_und_einkommensersatzleistungen_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def lohn_und_einkommensersatzleistungen_m_bis_2006(
    lohn_und_einkommensersatzleistungen_ohne_elterngeld_m: float,
) -> float:
    """Sum of the benefits under § 32b Abs. 1 S. 1 Nr. 1 EStG.

    Before Elterngeld exists, the catalogue is the sum without it.

    Reference: § 32b Abs. 1 Nr. 1 EStG idF Art. 1 G. v. 15.12.2003 BGBl. I S. 2645
    """
    return lohn_und_einkommensersatzleistungen_ohne_elterngeld_m


@policy_function(
    start_date="2007-01-01",
    leaf_name="lohn_und_einkommensersatzleistungen_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def lohn_und_einkommensersatzleistungen_m_ab_2007(
    lohn_und_einkommensersatzleistungen_ohne_elterngeld_m: float,
    elterngeld__betrag_m: float,
) -> float:
    """Sum of the benefits under § 32b Abs. 1 S. 1 Nr. 1 EStG.

    Elterngeld is Buchstabe j of the catalogue (Art. 2 Abs. 6 Nr. 2 G. v. 05.12.2006
    BGBl. I S. 2748) and enters in full, including the Sockelbetrag (BFH v. 21.09.2009,
    VI B 31/09, on § 32b Abs. 1 Nr. 1 Buchst. j EStG).

    Reference:
        - § 32b Abs. 1 Nr. 1 EStG idF Art. 2 G. v. 05.12.2006 BGBl. I S. 2748
        - § 32b Abs. 1 Satz 1 Nr. 1 EStG idF Art. 1 G. v. 19.12.2008 BGBl. I S. 2794
    """
    return lohn_und_einkommensersatzleistungen_ohne_elterngeld_m + elterngeld__betrag_m
