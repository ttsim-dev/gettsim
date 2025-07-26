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
    min_int_in_table: int,
    max_int_in_table: int,
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Convert sparse dict to consecutive int lookup table.

    Converts a dict with sparse integer keys to a consecutive int lookup table by
    filling in the gaps with the last defined value.

    Args:
        raw: Dictionary with sparse integer keys and float values min_int_in_table:
        Minimum integer value in the lookup table max_int_in_table: Maximum integer
        value in the lookup table (exclusive) xnp: NumPy-like module (numpy or
        jax.numpy)

    Returns:
        ConsecutiveIntLookupTableParamValue: A lookup table with consecutive integer
        keys
            from min_int_in_table to max_int_in_table - 1, with gaps filled using the
            last defined value.

    Example:
        >>> result = convert_sparse_dict_to_consecutive_int_lookup_table(
        ...     raw={0: 1, 3: 3},
        ...     min_int_in_table=0,
        ...     max_int_in_table=5,
        ...     xnp=xnp,
        ... )
        >>> result.value
        {0: 1, 1: 1, 2: 1, 3: 3, 4: 3}
    """
    _fail_if_raw_not_dict_with_int_keys(raw)
    _fail_if_raw_incompatible_with_min_max_int_in_table(
        raw=raw,
        min_int_in_table=min_int_in_table,
        max_int_in_table=max_int_in_table,
    )
    tmp = raw.copy()
    keys_in_raw: list[int] = sorted(tmp.keys())
    full_table: dict[int, float] = {}
    for a in range(min_int_in_table, max_int_in_table):
        if a < min(keys_in_raw):
            full_table[a] = tmp[min(keys_in_raw)]
        elif a not in keys_in_raw:
            full_table[a] = full_table[a - 1]
        else:
            full_table[a] = tmp[a]
    return get_consecutive_int_lookup_table_param_value(
        raw=full_table,
        xnp=xnp,
    )


def _fail_if_raw_incompatible_with_min_max_int_in_table(
    raw: dict[int, float],
    min_int_in_table: int,
    max_int_in_table: int,
) -> None:
    if min(raw.keys()) < min_int_in_table:
        msg = (
            "The smallest integer in the lookup table must not be larger than the "
            "smallest key in the raw dictionary. You provided the following values: "
            f"min_int_in_table={min_int_in_table}, min(raw.keys())={min(raw.keys())}"
        )
        raise ValueError(msg)
    if max(raw.keys()) >= max_int_in_table:
        msg = (
            "The largest integer in the lookup table must not be smaller than the "
            "largest key in the raw dictionary. You provided the following values: "
            f"max_int_in_table={max_int_in_table}, max(raw.keys())={max(raw.keys())}"
        )
        raise ValueError(msg)


def _fail_if_raw_not_dict_with_int_keys(raw: dict[int, float]) -> None:
    if not isinstance(raw, dict):
        msg = f"The raw dictionary must be a dictionary. You provided: {type(raw)}"
        raise TypeError(msg)
    key_types = {type(k) for k in raw}
    if key_types != {int}:
        msg = (
            "The raw dictionary must be a dictionary with int keys. You provided keys "
            f"of type: {key_types}"
        )
        raise TypeError(msg)
