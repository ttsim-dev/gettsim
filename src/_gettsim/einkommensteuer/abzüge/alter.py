"""Tax allowances for the elderly."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ttsim import (
    get_consecutive_int_1d_lookup_table_param_value,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from ttsim import ConsecutiveInt1dLookupTableParamValue


@policy_function(end_date="2004-12-31", leaf_name="altersfreibetrag_y")
def altersfreibetrag_y_bis_2004(
    alter: int,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    altersentlastungsbetrag_altersgrenze: int,
    maximaler_altersentlastungsbetrag_einheitlich: float,
    altersentlastungsquote_einheitlich: float,
) -> float:
    """Calculate tax deduction allowance for elderly until 2004."""
    altersgrenze = altersentlastungsbetrag_altersgrenze
    weiteres_einkommen = max(
        einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_y
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y,
        0.0,
    )
    if alter > altersgrenze:
        out = min(
            altersentlastungsquote_einheitlich
            * (
                einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y
                + weiteres_einkommen
            ),
            maximaler_altersentlastungsbetrag_einheitlich,
        )
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2005-01-01",
    leaf_name="altersfreibetrag_y",
    vectorization_strategy="loop",
)
def altersfreibetrag_y_ab_2005(
    alter: int,
    geburtsjahr: int,
    sozialversicherung__geringfügig_beschäftigt: bool,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    altersentlastungsbetrag_altersgrenze: int,
    maximaler_altersentlastungsbetrag_gestaffelt: ConsecutiveInt1dLookupTableParamValue,
    altersentlastungsquote_gestaffelt: ConsecutiveInt1dLookupTableParamValue,
) -> float:
    """Calculate tax deduction allowance for elderly since 2005."""
    betrag_max = maximaler_altersentlastungsbetrag_gestaffelt.values_to_look_up[
        geburtsjahr - maximaler_altersentlastungsbetrag_gestaffelt.base_to_subtract
    ]

    einkommen_lohn = (
        0
        if sozialversicherung__geringfügig_beschäftigt
        else einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y
    )
    weiteres_einkommen = max(
        einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_y
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y,
        0.0,
    )
    betrag = altersentlastungsquote_gestaffelt.values_to_look_up[
        geburtsjahr - altersentlastungsquote_gestaffelt.base_to_subtract
    ] * (einkommen_lohn + weiteres_einkommen)

    if alter > altersentlastungsbetrag_altersgrenze:
        out = min(betrag, betrag_max)
    else:
        out = 0.0

    return out


@param_function(start_date="2005-01-01")
def altersentlastungsquote_gestaffelt(
    raw_altersentlastungsquote_gestaffelt: dict[str | int, int | float],
) -> ConsecutiveInt1dLookupTableParamValue:
    """Convert the raw parameters for the age-based tax deduction allowance to a dict."""
    spec = raw_altersentlastungsquote_gestaffelt.copy()
    first_birthyear_to_consider: int = int(spec.pop("first_birthyear_to_consider"))
    last_birthyear_to_consider: int = int(spec.pop("last_birthyear_to_consider"))
    spec_int_float: dict[int, float] = {int(k): float(v) for k, v in spec.items()}
    return get_consecutive_int_1d_lookup_table_with_filled_up_tails(
        raw=spec_int_float,
        left_tail_key=first_birthyear_to_consider,
        right_tail_key=last_birthyear_to_consider,
    )


@param_function(start_date="2005-01-01")
def maximaler_altersentlastungsbetrag_gestaffelt(
    raw_maximaler_altersentlastungsbetrag_gestaffelt: dict[str | int, int | float],
) -> ConsecutiveInt1dLookupTableParamValue:
    """Convert the raw parameters for the age-based tax deduction allowance to a dict."""
    spec = raw_maximaler_altersentlastungsbetrag_gestaffelt.copy()
    first_birthyear_to_consider: int = int(spec.pop("first_birthyear_to_consider"))
    last_birthyear_to_consider: int = int(spec.pop("last_birthyear_to_consider"))
    spec_int_float: dict[int, float] = {int(k): float(v) for k, v in spec.items()}
    return get_consecutive_int_1d_lookup_table_with_filled_up_tails(
        raw=spec_int_float,
        left_tail_key=first_birthyear_to_consider,
        right_tail_key=last_birthyear_to_consider,
    )


def get_consecutive_int_1d_lookup_table_with_filled_up_tails(
    raw: dict[int, float],
    left_tail_key: int,
    right_tail_key: int,
) -> ConsecutiveInt1dLookupTableParamValue:
    """Create a consecutive integer lookup table with filled tails.

    This function takes a dictionary of consecutive integer keys and their corresponding
    values, and extends it to include all integers between left_tail_key and
    right_tail_key by filling the gaps with the minimum and maximum values from the
    original dictionary.
    """
    min_key_in_spec = min(raw.keys())
    max_key_in_spec = max(raw.keys())
    assert all(isinstance(k, int) for k in raw)
    assert len(list(raw.keys())) == max_key_in_spec - min_key_in_spec + 1, (
        "Dictionary keys must be consecutive integers."
    )
    consecutive_dict_start = dict.fromkeys(
        range(left_tail_key, min_key_in_spec), raw[min_key_in_spec]
    )
    consecutive_dict_end = dict.fromkeys(
        range(max_key_in_spec + 1, right_tail_key + 1), raw[max_key_in_spec]
    )
    return get_consecutive_int_1d_lookup_table_param_value(
        {**consecutive_dict_start, **raw, **consecutive_dict_end}
    )
