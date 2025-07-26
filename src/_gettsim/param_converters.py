from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    ConsecutiveIntLookupTableParamValue,
    get_consecutive_int_lookup_table_param_value,
)

if TYPE_CHECKING:
    from types import ModuleType


def convert_sparse_dict_to_consecutive_int_lookup_table(
    raw: dict[int, float],
    max_key_in_table: int,
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Convert sparse dict to consecutive int lookup table."""
    tmp = raw.copy()
    keys_in_raw: list[int] = sorted(tmp.keys())

    full_table: dict[int, float] = {}
    for a in range(min(keys_in_raw), max_key_in_table):
        if a not in keys_in_raw:
            full_table[a] = full_table[a - 1]
        else:
            full_table[a] = tmp[a]
    return get_consecutive_int_lookup_table_param_value(
        raw=full_table,
        xnp=xnp,
    )
