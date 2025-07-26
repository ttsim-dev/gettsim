"""Tax allowances for the elderly."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    get_consecutive_int_lookup_table_param_value,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.tt import ConsecutiveIntLookupTableParamValue


@policy_function(end_date="2004-12-31", leaf_name="altersfreibetrag_y")
def altersfreibetrag_y_bis_2004(
    alter: int,
    einnahmen__bruttolohn_y: float,
    einnahmen__kapitalerträge_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    altersentlastungsbetrag_altersgrenze: int,
    maximaler_altersentlastungsbetrag: float,
    altersentlastungsquote: float,
) -> float:
    """Calculate tax deduction allowance for elderly until 2004."""
    altersgrenze = altersentlastungsbetrag_altersgrenze
    weiteres_einkommen = max(
        einnahmen__kapitalerträge_y
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y,
        0.0,
    )
    if alter > altersgrenze:
        out = min(
            altersentlastungsquote * (einnahmen__bruttolohn_y + weiteres_einkommen),
            maximaler_altersentlastungsbetrag,
        )
    else:
        out = 0.0

    return out


@policy_function(start_date="2005-01-01", leaf_name="altersfreibetrag_y")
def altersfreibetrag_y_ab_2005(
    alter: int,
    geburtsjahr: int,
    sozialversicherung__geringfügig_beschäftigt: bool,
    einnahmen__bruttolohn_y: float,
    einnahmen__kapitalerträge_y: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y: float,
    altersentlastungsbetrag_altersgrenze: int,
    maximaler_altersentlastungsbetrag_gestaffelt: ConsecutiveIntLookupTableParamValue,
    altersentlastungsquote_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Calculate tax deduction allowance for elderly since 2005."""
    maximaler_altersentlastungsbetrag = (
        maximaler_altersentlastungsbetrag_gestaffelt.look_up(geburtsjahr)
    )

    einkommen_lohn = (
        0 if sozialversicherung__geringfügig_beschäftigt else einnahmen__bruttolohn_y
    )
    weiteres_einkommen = max(
        einnahmen__kapitalerträge_y
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y,
        0.0,
    )
    betrag = altersentlastungsquote_gestaffelt.look_up(geburtsjahr) * (
        einkommen_lohn + weiteres_einkommen
    )

    if alter > altersentlastungsbetrag_altersgrenze:
        out = min(betrag, maximaler_altersentlastungsbetrag)
    else:
        out = 0.0

    return out


@param_function(start_date="2005-01-01")
def altersentlastungsquote_gestaffelt(
    raw_altersentlastungsquote_gestaffelt: dict[str | int, int | float],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Convert the raw parameters for the age-based tax deduction allowance to a dict."""
    spec = raw_altersentlastungsquote_gestaffelt.copy()
    first_birthyear_to_consider: int = int(spec.pop("first_birthyear_to_consider"))
    last_birthyear_to_consider: int = int(spec.pop("last_birthyear_to_consider"))
    spec_int_float: dict[int, float] = {int(k): float(v) for k, v in spec.items()}
    return get_consecutive_int_1d_lookup_table_with_filled_up_tails(
        raw=spec_int_float,
        left_tail_key=first_birthyear_to_consider,
        right_tail_key=last_birthyear_to_consider,
        xnp=xnp,
    )


@param_function(start_date="2005-01-01")
def maximaler_altersentlastungsbetrag_gestaffelt(
    raw_maximaler_altersentlastungsbetrag_gestaffelt: dict[str | int, int | float],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Convert the raw parameters for the age-based tax deduction allowance to a dict."""
    spec = raw_maximaler_altersentlastungsbetrag_gestaffelt.copy()
    first_birthyear_to_consider: int = int(spec.pop("first_birthyear_to_consider"))
    last_birthyear_to_consider: int = int(spec.pop("last_birthyear_to_consider"))
    spec_int_float: dict[int, float] = {int(k): float(v) for k, v in spec.items()}
    return get_consecutive_int_1d_lookup_table_with_filled_up_tails(
        raw=spec_int_float,
        left_tail_key=first_birthyear_to_consider,
        right_tail_key=last_birthyear_to_consider,
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
    if not all(isinstance(k, int) for k in raw):
        raise ValueError("All dictionary keys must be integers")
    min_key_in_spec = min(raw.keys())
    max_key_in_spec = max(raw.keys())
    if len(list(raw.keys())) != max_key_in_spec - min_key_in_spec + 1:
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
