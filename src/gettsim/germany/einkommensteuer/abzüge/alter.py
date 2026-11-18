"""Tax allowances for the elderly."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    InputOutputUnits,
    RoundingSpec,
    TTSIMUnit,
    cast_ttsim_unit,
    get_consecutive_int_lookup_table_param_value,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.tt import ConsecutiveIntLookupTableParamValue


@policy_function(unit=TTSIMUnit.CALENDAR_YEAR)
def altersentlastungsbetrag_erstes_anspruchsjahr(
    geburtsjahr: int,
    geburtsmonat: int,
    geburtstag: int,
    altersentlastungsbetrag_altersgrenze: int,
) -> int:
    """Calendar year following the completion of the 64th year of life.

    § 24a Satz 3 EStG grants the Altersentlastungsbetrag from this year on; from 2005
    it is also the row of the table in § 24a Satz 5 EStG. People born on 1 January
    complete a year of life in the preceding calendar year (§ 108 Abs. 1 AO, § 187
    Abs. 2 Satz 2, § 188 Abs. 2 BGB).
    """
    if geburtsmonat == 1 and geburtstag == 1:
        out = geburtsjahr + altersentlastungsbetrag_altersgrenze
    else:
        out = (
            geburtsjahr
            + altersentlastungsbetrag_altersgrenze
            + cast_ttsim_unit(1, unit=TTSIMUnit.YEARS)
        )
    return out


@policy_function(
    end_date="2004-12-31",
    leaf_name="altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y_bis_2004(
    einkommensteuer__einkünfte__sonstige__werbungskostenpauschbetrag_y: float,
    einkommensteuer__einkünfte__sonstige__rente__steuerpflichtige_einnahmen_y: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_y: float,
    einnahmen__renten__geförderte_private_vorsorge_y: float,
) -> float:
    """Sonstige Einkünfte (§ 22 EStG) other than Leibrenten, for § 24a EStG.

    The Werbungskosten-Pauschbetrag of § 9a Satz 1 Nr. 3 EStG comes off the taxable
    part of the Leibrenten first, and only the remainder off the other § 22 Einnahmen
    (R 24a Abs. 1 Satz 3 EStR). Before 2005, payouts of the betriebliche
    Altersvorsorge are taxed with their Ertragsanteil and count as Leibrenten.
    """
    einnahmen_ohne_leibrenten = (
        einkommensteuer__einkünfte__sonstige__alle_weiteren_y
        + einnahmen__renten__geförderte_private_vorsorge_y
    )
    leibrenten_steuerpflichtiger_teil = max(
        einkommensteuer__einkünfte__sonstige__rente__steuerpflichtige_einnahmen_y
        - einnahmen__renten__geförderte_private_vorsorge_y,
        0.0,
    )
    nicht_verbrauchter_pauschbetrag = max(
        einkommensteuer__einkünfte__sonstige__werbungskostenpauschbetrag_y
        - leibrenten_steuerpflichtiger_teil,
        0.0,
    )
    return max(einnahmen_ohne_leibrenten - nicht_verbrauchter_pauschbetrag, 0.0)


@policy_function(
    start_date="2005-01-01",
    leaf_name="altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y_ab_2005(
    einkommensteuer__einkünfte__sonstige__werbungskostenpauschbetrag_y: float,
    einkommensteuer__einkünfte__sonstige__rente__steuerpflichtige_einnahmen_y: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_y: float,
    einnahmen__renten__geförderte_private_vorsorge_y: float,
    einnahmen__renten__betriebliche_altersvorsorge_y: float,
) -> float:
    """Sonstige Einkünfte (§ 22 EStG) other than Leibrenten, for § 24a EStG.

    The Werbungskosten-Pauschbetrag of § 9a Satz 1 Nr. 3 EStG comes off the taxable
    part of the Leibrenten first, and only the remainder off the other § 22 Einnahmen
    (R 24a Abs. 1 Satz 3 EStR).

    Simplification: the whole `betriebliche_altersvorsorge` input counts. Under the
    statute, Betriebsrenten from a Direktzusage or Unterstützungskasse are
    Versorgungsbezüge (§ 19 Abs. 2 EStG) and stay out (§ 24a Satz 2 Nr. 1 EStG), as do
    parts taxed like a Leibrente (§ 24a Satz 2 Nr. 4 und 5 EStG).
    """
    einnahmen_ohne_leibrenten = (
        einkommensteuer__einkünfte__sonstige__alle_weiteren_y
        + einnahmen__renten__geförderte_private_vorsorge_y
        + einnahmen__renten__betriebliche_altersvorsorge_y
    )
    leibrenten_steuerpflichtiger_teil = max(
        einkommensteuer__einkünfte__sonstige__rente__steuerpflichtige_einnahmen_y
        - einnahmen__renten__geförderte_private_vorsorge_y
        - einnahmen__renten__betriebliche_altersvorsorge_y,
        0.0,
    )
    nicht_verbrauchter_pauschbetrag = max(
        einkommensteuer__einkünfte__sonstige__werbungskostenpauschbetrag_y
        - leibrenten_steuerpflichtiger_teil,
        0.0,
    )
    return max(einnahmen_ohne_leibrenten - nicht_verbrauchter_pauschbetrag, 0.0)


@policy_function(
    end_date="2004-12-31",
    leaf_name="altersentlastungsbetrag_bemessungsgrundlage_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersentlastungsbetrag_bemessungsgrundlage_y_bis_2004(
    einnahmen__bruttolohn_y: float,
    einnahmen__kapitalerträge_y: float,
    einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y: float,
    einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__sparerfreibetrag_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__werbungskostenpauschbetrag_y: float,
    altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y: float,
) -> float:
    """Arbeitslohn plus the positive sum of all other Einkünfte.

    § 24a Sätze 1 und 2 EStG. Leibrenten (§ 22 Nr. 1 Satz 3 Buchst. a EStG) stay out.
    """
    einkünfte_aus_kapitalvermögen = max(
        einnahmen__kapitalerträge_y
        - einkommensteuer__einkünfte__aus_kapitalvermögen__sparerfreibetrag_y
        - einkommensteuer__einkünfte__aus_kapitalvermögen__werbungskostenpauschbetrag_y,
        0.0,
    )
    return einnahmen__bruttolohn_y + max(
        einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y
        + einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y
        + einkünfte_aus_kapitalvermögen
        + altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y,
        0.0,
    )


@policy_function(
    start_date="2005-01-01",
    end_date="2008-12-31",
    leaf_name="altersentlastungsbetrag_bemessungsgrundlage_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersentlastungsbetrag_bemessungsgrundlage_y_2005_bis_2008(
    sozialversicherung__geringfügig_beschäftigt: bool,
    einnahmen__bruttolohn_y: float,
    einnahmen__kapitalerträge_y: float,
    einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y: float,
    einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__sparerfreibetrag_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__werbungskostenpauschbetrag_y: float,
    altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y: float,
) -> float:
    """Arbeitslohn plus the positive sum of all other Einkünfte.

    § 24a Sätze 1 und 2 EStG. Leibrenten (§ 22 Nr. 1 Satz 3 Buchst. a EStG) stay out.
    Wage from marginal employment is taxed at a flat rate outside the assessment and
    stays out.
    """
    arbeitslohn = (
        0.0 if sozialversicherung__geringfügig_beschäftigt else einnahmen__bruttolohn_y
    )
    einkünfte_aus_kapitalvermögen = max(
        einnahmen__kapitalerträge_y
        - einkommensteuer__einkünfte__aus_kapitalvermögen__sparerfreibetrag_y
        - einkommensteuer__einkünfte__aus_kapitalvermögen__werbungskostenpauschbetrag_y,
        0.0,
    )
    return arbeitslohn + max(
        einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y
        + einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y
        + einkünfte_aus_kapitalvermögen
        + altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y,
        0.0,
    )


@policy_function(
    start_date="2009-01-01",
    leaf_name="altersentlastungsbetrag_bemessungsgrundlage_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersentlastungsbetrag_bemessungsgrundlage_y_ab_2009(
    sozialversicherung__geringfügig_beschäftigt: bool,
    einnahmen__bruttolohn_y: float,
    einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y: float,
    einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y: float,
) -> float:
    """Arbeitslohn plus the positive sum of all other Einkünfte.

    § 24a Sätze 1 und 2 EStG. Capital income under the Abgeltungsteuer stays out (§ 2
    Abs. 5b EStG, Unternehmensteuerreformgesetz 2008), as do Leibrenten (§ 22 Nr. 1
    Satz 3 Buchst. a EStG). Wage from marginal employment is taxed at a flat rate
    outside the assessment and stays out.
    """
    arbeitslohn = (
        0.0 if sozialversicherung__geringfügig_beschäftigt else einnahmen__bruttolohn_y
    )
    return arbeitslohn + max(
        einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y
        + einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y
        + altersentlastungsbetrag_sonstige_einkünfte_ohne_leibrenten_y,
        0.0,
    )


@policy_function(
    end_date="2001-12-31",
    leaf_name="altersfreibetrag_y",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.DM.PER_YEAR,
        base=1,
        direction="up",
        reference="Abschn. 171a Abs. 1 EStR 1990, R 171a Abs. 1 EStR 1993 bis 2003",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersfreibetrag_y_bis_2001(
    evaluation_year: int,
    altersentlastungsbetrag_erstes_anspruchsjahr: int,
    altersentlastungsbetrag_bemessungsgrundlage_y: float,
    maximaler_altersentlastungsbetrag_y: float,
    altersentlastungsquote: float,
) -> float:
    """Altersentlastungsbetrag, § 24a EStG: a share of the base up to a maximum."""
    if evaluation_year >= altersentlastungsbetrag_erstes_anspruchsjahr:
        out = min(
            altersentlastungsquote * altersentlastungsbetrag_bemessungsgrundlage_y,
            maximaler_altersentlastungsbetrag_y,
        )
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2002-01-01",
    end_date="2004-12-31",
    leaf_name="altersfreibetrag_y",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR,
        base=1,
        direction="up",
        reference="Abschn. 171a Abs. 1 EStR 1990, R 171a Abs. 1 EStR 1993 bis 2003",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersfreibetrag_y_2002_bis_2004(
    evaluation_year: int,
    altersentlastungsbetrag_erstes_anspruchsjahr: int,
    altersentlastungsbetrag_bemessungsgrundlage_y: float,
    maximaler_altersentlastungsbetrag_y: float,
    altersentlastungsquote: float,
) -> float:
    """Altersentlastungsbetrag, § 24a EStG: a share of the base up to a maximum."""
    if evaluation_year >= altersentlastungsbetrag_erstes_anspruchsjahr:
        out = min(
            altersentlastungsquote * altersentlastungsbetrag_bemessungsgrundlage_y,
            maximaler_altersentlastungsbetrag_y,
        )
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2005-01-01",
    leaf_name="altersfreibetrag_y",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_YEAR,
        base=1,
        direction="up",
        reference="R 24a Abs. 1 Satz 4 EStR",
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersfreibetrag_y_ab_2005(
    evaluation_year: int,
    altersentlastungsbetrag_erstes_anspruchsjahr: int,
    altersentlastungsbetrag_bemessungsgrundlage_y: float,
    maximaler_altersentlastungsbetrag_y_gestaffelt_nach_geburtsjahr: ConsecutiveIntLookupTableParamValue,
    altersentlastungsquote_gestaffelt_nach_geburtsjahr: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Altersentlastungsbetrag, § 24a EStG (Alterseinkünftegesetz).

    Share and maximum are those of the calendar year following the completion of the
    64th year of life (§ 24a Satz 5 EStG) and stay fixed for life.
    """
    if evaluation_year >= altersentlastungsbetrag_erstes_anspruchsjahr:
        out = min(
            altersentlastungsquote_gestaffelt_nach_geburtsjahr.look_up(
                altersentlastungsbetrag_erstes_anspruchsjahr
            )
            * altersentlastungsbetrag_bemessungsgrundlage_y,
            maximaler_altersentlastungsbetrag_y_gestaffelt_nach_geburtsjahr.look_up(
                altersentlastungsbetrag_erstes_anspruchsjahr
            ),
        )
    else:
        out = 0.0

    return out


@param_function(
    start_date="2005-01-01",
    unit=InputOutputUnits(
        input_unit=TTSIMUnit.CALENDAR_YEAR,
        output_unit=TTSIMUnit.DIMENSIONLESS,
    ),
    # Mandatory for schedule builders: the body builds a table, so it cannot be
    # unit-verified. The declared axes screen the look_up call sites (GEP 10).
    verify_units=False,
)
def altersentlastungsquote_gestaffelt_nach_geburtsjahr(
    raw_altersentlastungsquote_gestaffelt: dict[str | int, int | float],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Table of § 24a Satz 5 EStG by the year following completion of the 64th year."""
    spec = raw_altersentlastungsquote_gestaffelt.copy()
    first_calendar_year_to_consider: int = int(
        spec.pop("first_calendar_year_to_consider")
    )
    last_calendar_year_to_consider: int = int(
        spec.pop("last_calendar_year_to_consider")
    )
    spec_int_float: dict[int, float] = {int(k): float(v) for k, v in spec.items()}
    return get_consecutive_int_1d_lookup_table_with_filled_up_tails(
        raw=spec_int_float,
        left_tail_key=first_calendar_year_to_consider,
        right_tail_key=last_calendar_year_to_consider,
        xnp=xnp,
    )


@param_function(
    start_date="2005-01-01",
    unit=InputOutputUnits(
        input_unit=TTSIMUnit.CALENDAR_YEAR,
        output_unit=TTSIMUnit.CURRENCY.PER_YEAR,
    ),
    # Mandatory for schedule builders: the body builds a table, so it cannot be
    # unit-verified. The declared axes screen the look_up call sites (GEP 10).
    verify_units=False,
)
def maximaler_altersentlastungsbetrag_y_gestaffelt_nach_geburtsjahr(
    raw_maximaler_altersentlastungsbetrag_y_gestaffelt: dict[str | int, int | float],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Table of § 24a Satz 5 EStG by the year following completion of the 64th year."""
    spec = raw_maximaler_altersentlastungsbetrag_y_gestaffelt.copy()
    first_calendar_year_to_consider: int = int(
        spec.pop("first_calendar_year_to_consider")
    )
    last_calendar_year_to_consider: int = int(
        spec.pop("last_calendar_year_to_consider")
    )
    spec_int_float: dict[int, float] = {int(k): float(v) for k, v in spec.items()}
    return get_consecutive_int_1d_lookup_table_with_filled_up_tails(
        raw=spec_int_float,
        left_tail_key=first_calendar_year_to_consider,
        right_tail_key=last_calendar_year_to_consider,
        xnp=xnp,
    )


def get_consecutive_int_1d_lookup_table_with_filled_up_tails(
    raw: dict[int, float],
    left_tail_key: int,
    right_tail_key: int,
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Create a consecutive integer lookup table with filled tails.

    This function takes a dictionary of consecutive integer keys and their corresponding
    values, and extends it to include all integers between left_tail_key and
    right_tail_key by filling the gaps with the minimum and maximum values from the
    original dictionary.
    """
    if not all(isinstance(k, int) for k in raw):  # pragma: no cover
        raise ValueError("All dictionary keys must be integers")
    min_key_in_spec = min(raw.keys())
    max_key_in_spec = max(raw.keys())
    if (
        len(list(raw.keys())) != max_key_in_spec - min_key_in_spec + 1
    ):  # pragma: no cover
        raise ValueError("Dictionary keys must be consecutive integers.")
    consecutive_dict_start = dict.fromkeys(
        range(left_tail_key, min_key_in_spec),
        raw[min_key_in_spec],
    )
    consecutive_dict_end = dict.fromkeys(
        range(max_key_in_spec + 1, right_tail_key + 1),
        raw[max_key_in_spec],
    )
    return get_consecutive_int_lookup_table_param_value(
        raw={**consecutive_dict_start, **raw, **consecutive_dict_end},
        xnp=xnp,
    )
