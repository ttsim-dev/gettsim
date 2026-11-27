"""Sonstige Einkünfte according to § 22 EStG."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.tt import ConsecutiveIntLookupTableParamValue

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(
    end_date="2004-12-31",
    leaf_name="steuerpflichtige_einnahmen_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def steuerpflichtige_einnahmen_m_nach_ertragsanteil(
    ertragsanteil_gesetzliche_rente: float,
    ertragsanteil_berufsständische_altersvorsorge: float,
    ertragsanteil_sonstige_private_vorsorge: float,
    ertragsanteil_betriebliche_altersvorsorge: float,
    einnahmen__renten__gesetzliche_m: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
    einnahmen__renten__aus_berufsständischen_versicherungen_m: float,
) -> float:
    """Steuerpflichtige Einnahmen aus Renten i.S.d. § 22 EStG.

    Reference: § 22 Nr. 1 Satz 3 Buchst. a EStG idF B. v. 16.04.1997 BGBl. I S. 821
    """
    return (
        ertragsanteil_gesetzliche_rente * einnahmen__renten__gesetzliche_m
        + ertragsanteil_berufsständische_altersvorsorge
        * einnahmen__renten__aus_berufsständischen_versicherungen_m
        + ertragsanteil_sonstige_private_vorsorge
        * einnahmen__renten__sonstige_private_vorsorge_m
        + ertragsanteil_betriebliche_altersvorsorge
        * einnahmen__renten__betriebliche_altersvorsorge_m
        + einnahmen__renten__geförderte_private_vorsorge_m
    )


@policy_function(
    start_date="2005-01-01",
    leaf_name="steuerpflichtige_einnahmen_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def steuerpflichtige_einnahmen_m_nach_besteuerungsanteil(
    steuerpflichtiger_anteil_der_renteneinnahmen_m: float,
    ertragsanteil_sonstige_private_vorsorge: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
) -> float:
    """Steuerpflichtige Einnahmen aus Renten i.S.d. § 22 EStG.

    Reference: § 22 Nr. 1 Satz 3 Buchst. a EStG idF Art. 1 G. v. 05.07.2004 BGBl. I S. 1427
    """
    return (
        steuerpflichtiger_anteil_der_renteneinnahmen_m
        + ertragsanteil_sonstige_private_vorsorge
        * einnahmen__renten__sonstige_private_vorsorge_m
        + einnahmen__renten__betriebliche_altersvorsorge_m
        + einnahmen__renten__geförderte_private_vorsorge_m
    )


@policy_function(start_date="2005-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def steuerpflichtiger_anteil_der_renteneinnahmen_m(
    besteuerungsanteil: float,
    renten_aus_basisversorgung_m: float,
) -> float:
    """Taxable share of the pensions from the Basisversorgung.

    § 22 Nr. 1 Satz 3 Buchstabe a Doppelbuchstabe aa EStG.

    Reference: § 22 Nr. 1 Satz 3 Buchst. a EStG idF Art. 1 G. v. 05.07.2004 BGBl. I S. 1427
    """
    return besteuerungsanteil * renten_aus_basisversorgung_m


@policy_function(
    start_date="2005-01-01",
    end_date="2020-12-31",
    leaf_name="renten_aus_basisversorgung_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def renten_aus_basisversorgung_m_bis_2020(
    einnahmen__renten__gesetzliche_m: float,
    einnahmen__renten__basisrente_m: float,
    einnahmen__renten__aus_berufsständischen_versicherungen_m: float,
) -> float:
    """Pensions from the Basisversorgung, taxed at the Besteuerungsanteil.

    § 22 Nr. 1 Satz 3 Buchstabe a Doppelbuchstabe aa EStG.

    Reference: § 22 Nr. 1 Satz 3 Buchst. a EStG idF Art. 1 G. v. 05.07.2004 BGBl. I S. 1427
    """
    return (
        einnahmen__renten__gesetzliche_m
        + einnahmen__renten__basisrente_m
        + einnahmen__renten__aus_berufsständischen_versicherungen_m
    )


@policy_function(
    start_date="2021-01-01",
    leaf_name="renten_aus_basisversorgung_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def renten_aus_basisversorgung_m_ohne_grundrentenzuschlag(
    einnahmen__renten__gesetzliche_m: float,
    einnahmen__renten__basisrente_m: float,
    einnahmen__renten__aus_berufsständischen_versicherungen_m: float,
    sozialversicherung__rente__grundrente__betrag_m: float,
    sozialversicherung__rente__bezieht_altersrente: bool,
) -> float:
    """Pensions from the Basisversorgung, without the Grundrentenzuschlag.

    The pension share resting on the Grundrentenzuschlag is tax-free. The Zuschlag is
    part of the Altersrente only while the person receives it.

    If `einnahmen__renten__gesetzliche_m` is supplied as data, it must include the
    Grundrentenzuschlag that is subtracted here (`grundrente__betrag_m`, supplied or
    computed). Otherwise the difference is too small and may become negative.

    § 3 Nr. 14a EStG covers the Zuschlag in every pension from the gesetzliche
    Rentenversicherung, including Erwerbsminderungsrenten. GETTSIM models the Zuschlag
    for Altersrenten only.

    The Besteuerungsanteil applies under § 22 Nr. 1 Satz 3 Buchstabe a Doppelbuchstabe
    aa EStG. § 3 Nr. 14a EStG was inserted by Art. 3 G. v. 16.12.2022 BGBl. I S. 2294
    and applies from VZ 2021.

    Reference:
        - § 22 Nr. 1 Satz 3 Buchst. a EStG idF Art. 2 G. v. 21.12.2020 BGBl. I S. 3096
        - § 3 Nr. 14a EStG idF Art. 3 G. v. 16.12.2022 BGBl. I S. 2294
    """
    grundrentenzuschlag_m = (
        sozialversicherung__rente__grundrente__betrag_m
        if sozialversicherung__rente__bezieht_altersrente
        else 0.0
    )
    return (
        einnahmen__renten__gesetzliche_m
        - grundrentenzuschlag_m
        + einnahmen__renten__basisrente_m
        + einnahmen__renten__aus_berufsständischen_versicherungen_m
    )


@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
def ertragsanteil_sonstige_private_vorsorge(
    alter_beginn_leistungsbezug_sonstige_private_vorsorge: int,
    parameter_ertragsanteil: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Ertragsanteil.

    Since 2005, the Ertragsanteil is in § 22 Nr. 1 Satz 3 Buchstabe a Doppelbuchstabe bb
    EStG.

    Reference:
        - § 22 Nr. 1 Satz 3 Buchst. a EStG idF B. v. 16.04.1997 BGBl. I S. 821
        - § 22 Nr. 1 Satz 3 Buchst. a EStG idF Art. 1 G. v. 05.07.2004 BGBl. I S. 1427
    """
    return parameter_ertragsanteil.look_up(
        alter_beginn_leistungsbezug_sonstige_private_vorsorge
    )


@policy_function(end_date="2004-12-31", unit=TTSIMUnit.DIMENSIONLESS)
def ertragsanteil_berufsständische_altersvorsorge(
    alter_beginn_leistungsbezug_berufsständische_altersvorsorge: int,
    parameter_ertragsanteil: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Ertragsanteil.

    Reference: § 22 Nr. 1 Satz 3 Buchst. a EStG idF B. v. 16.04.1997 BGBl. I S. 821
    """
    return parameter_ertragsanteil.look_up(
        alter_beginn_leistungsbezug_berufsständische_altersvorsorge
    )


@policy_function(
    end_date="2004-12-31",
    unit=TTSIMUnit.DIMENSIONLESS,
)
def ertragsanteil_gesetzliche_rente(
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    parameter_ertragsanteil: ConsecutiveIntLookupTableParamValue,
    xnp: ModuleType,
) -> float:
    """Ertragsanteil.

    Reference: § 22 Nr. 1 Satz 3 Buchst. a EStG idF B. v. 16.04.1997 BGBl. I S. 821
    """
    return parameter_ertragsanteil.look_up(
        xnp.floor(sozialversicherung__rente__alter_bei_renteneintritt).astype(int)
    )


@policy_function(end_date="2004-12-31", unit=TTSIMUnit.DIMENSIONLESS)
def ertragsanteil_betriebliche_altersvorsorge(
    alter_beginn_leistungsbezug_betriebliche_altersvorsorge: int,
    parameter_ertragsanteil: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Ertragsanteil.

    Reference: § 22 Nr. 1 Satz 3 Buchst. a EStG idF B. v. 16.04.1997 BGBl. I S. 821
    """
    return parameter_ertragsanteil.look_up(
        alter_beginn_leistungsbezug_betriebliche_altersvorsorge
    )


@policy_function(start_date="2005-01-01", unit=TTSIMUnit.DIMENSIONLESS)
def besteuerungsanteil(
    sozialversicherung__rente__jahr_renteneintritt: int,
    parameter_besteuerungsanteil: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Share of pensions subject to income taxation.

    Reference: § 22 Nr. 1 Satz 3 Buchst. a EStG idF Art. 1 G. v. 05.07.2004 BGBl. I S. 1427
    """
    return parameter_besteuerungsanteil.look_up(
        sozialversicherung__rente__jahr_renteneintritt
    )
