"""Tax allowances for the elderly."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    InputOutputUnits,
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
    it is also the row of the table in § 24a Satz 5 EStG.

    A year of life is completed at the end of the day before the birthday (§ 108 Abs. 1
    AO, § 187 Abs. 2 Satz 2, § 188 Abs. 2 BGB), so people born on 1 January complete it
    in the preceding calendar year.
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
    leaf_name="altersentlastungsbetrag_bemessungsgrundlage_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersentlastungsbetrag_bemessungsgrundlage_y_bis_2004(
    einnahmen__bruttolohn_y: float,
    einnahmen__kapitalerträge_y: float,
    einnahmen__renten__geförderte_private_vorsorge_y: float,
    einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y: float,
    einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__sparerfreibetrag_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__werbungskostenpauschbetrag_y: float,
) -> float:
    """Arbeitslohn plus the positive sum of all other Einkünfte.

    § 24a Sätze 1 und 2 EStG. Leibrenten (§ 22 Nr. 1 Satz 3 Buchst. a EStG) stay out.

    Not modelled:

    - Versorgungsbezüge (§ 19 Abs. 2 EStG) are not separated from the Arbeitslohn.
    - Each person deducts their own Sparer-Freibetrag only; spouses cannot use the
      part their partner leaves unused.
    - The Werbungskosten-Pauschbetrag for sonstige Einkünfte is not deducted.
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
        + einkommensteuer__einkünfte__sonstige__alle_weiteren_y
        + einnahmen__renten__geförderte_private_vorsorge_y,
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
    einnahmen__renten__geförderte_private_vorsorge_y: float,
    einnahmen__renten__betriebliche_altersvorsorge_y: float,
    einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y: float,
    einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__sparerfreibetrag_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__werbungskostenpauschbetrag_y: float,
) -> float:
    """Arbeitslohn plus the positive sum of all other Einkünfte.

    § 24a Sätze 1 und 2 EStG. Leibrenten (§ 22 Nr. 1 Satz 3 Buchst. a EStG) stay out;
    payouts of the betriebliche Altersvorsorge are fully taxed under § 22 Nr. 5 EStG
    since the Alterseinkünftegesetz and count. Wage from marginal employment is taxed
    at a flat rate outside the assessment and stays out.

    Not modelled:

    - Versorgungsbezüge (§ 19 Abs. 2 EStG) are not separated from the Arbeitslohn.
    - Each person deducts their own Sparer-Freibetrag only; spouses cannot use the
      part their partner leaves unused.
    - The Werbungskosten-Pauschbetrag for sonstige Einkünfte is not deducted.
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
        + einkommensteuer__einkünfte__sonstige__alle_weiteren_y
        + einnahmen__renten__geförderte_private_vorsorge_y
        + einnahmen__renten__betriebliche_altersvorsorge_y,
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
    einnahmen__renten__geförderte_private_vorsorge_y: float,
    einnahmen__renten__betriebliche_altersvorsorge_y: float,
    einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y: float,
    einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_y: float,
) -> float:
    """Arbeitslohn plus the positive sum of all other Einkünfte.

    § 24a Sätze 1 und 2 EStG. Capital income under the Abgeltungsteuer stays out (§ 2
    Abs. 5b EStG, Unternehmensteuerreformgesetz 2008), as do Leibrenten (§ 22 Nr. 1
    Satz 3 Buchst. a EStG). Wage from marginal employment is taxed at a flat rate
    outside the assessment and stays out.

    Not modelled:

    - Versorgungsbezüge (§ 19 Abs. 2 EStG) are not separated from the Arbeitslohn.
    - Capital income taxed at the ordinary tariff (Günstigerprüfung, § 32d Abs. 6
      EStG) belongs to the base.
    - The Werbungskosten-Pauschbetrag for sonstige Einkünfte is not deducted.
    """
    arbeitslohn = (
        0.0 if sozialversicherung__geringfügig_beschäftigt else einnahmen__bruttolohn_y
    )
    return arbeitslohn + max(
        einkommensteuer__einkünfte__aus_forst_und_landwirtschaft__betrag_y
        + einkommensteuer__einkünfte__aus_gewerbebetrieb__betrag_y
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y
        + einkommensteuer__einkünfte__sonstige__alle_weiteren_y
        + einnahmen__renten__geförderte_private_vorsorge_y
        + einnahmen__renten__betriebliche_altersvorsorge_y,
        0.0,
    )


@policy_function(
    end_date="2004-12-31",
    leaf_name="altersfreibetrag_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersfreibetrag_y_bis_2004(
    policy_year: int,
    altersentlastungsbetrag_erstes_anspruchsjahr: int,
    altersentlastungsbetrag_bemessungsgrundlage_y: float,
    maximaler_altersentlastungsbetrag_y: float,
    altersentlastungsquote: float,
    xnp: ModuleType,
) -> float:
    """Altersentlastungsbetrag, § 24a EStG: a share of the base up to a maximum.

    Rounded up to the full currency unit (Abschn. 171a Abs. 1 EStR 1990, R 171a Abs. 1
    EStR 1993 to 2003).
    """
    # Rate in per mille times base in cents is exact, so that a product which is a
    # whole currency unit is not rounded up to the next one.
    betrag = xnp.ceil(
        xnp.round(altersentlastungsquote * 1000)
        * xnp.round(altersentlastungsbetrag_bemessungsgrundlage_y * 100)
        / 100000
    )
    if policy_year >= altersentlastungsbetrag_erstes_anspruchsjahr:
        out = min(betrag, maximaler_altersentlastungsbetrag_y)
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2005-01-01",
    leaf_name="altersfreibetrag_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def altersfreibetrag_y_ab_2005(
    policy_year: int,
    altersentlastungsbetrag_erstes_anspruchsjahr: int,
    altersentlastungsbetrag_bemessungsgrundlage_y: float,
    maximaler_altersentlastungsbetrag_y_gestaffelt_nach_geburtsjahr: ConsecutiveIntLookupTableParamValue,
    altersentlastungsquote_gestaffelt_nach_geburtsjahr: ConsecutiveIntLookupTableParamValue,
    xnp: ModuleType,
) -> float:
    """Altersentlastungsbetrag, § 24a EStG (Alterseinkünftegesetz).

    Share and maximum are those of the calendar year following the completion of the
    64th year of life (§ 24a Satz 5 EStG) and stay fixed for life.

    Rounded up to the full Euro (R 24a Abs. 1 EStR).
    """
    # Rate in per mille times base in cents is exact, so that a product which is a
    # whole Euro is not rounded up to the next one.
    betrag = xnp.ceil(
        xnp.round(
            altersentlastungsquote_gestaffelt_nach_geburtsjahr.look_up(
                altersentlastungsbetrag_erstes_anspruchsjahr
            )
            * 1000
        )
        * xnp.round(altersentlastungsbetrag_bemessungsgrundlage_y * 100)
        / 100000
    )
    if policy_year >= altersentlastungsbetrag_erstes_anspruchsjahr:
        out = min(
            betrag,
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
