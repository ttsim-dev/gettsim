"""Renting costs relevant for housing benefit calculation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from gettsim.tt import (
    UNSET_UNIT,
    ConsecutiveIntLookupTableParamValue,
    TTSIMUnit,
    cast_unit,
    get_consecutive_int_lookup_table_param_value,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from jaxtyping import Array, Int


@dataclass(frozen=True)
class LookupTableBaujahr:
    baujahre: Int[Array, " n_baujahr_categories"]
    lookup_table: ConsecutiveIntLookupTableParamValue


@param_function(
    start_date="1984-01-01",
    end_date="2008-12-31",
    leaf_name="max_miete_m_lookup",
    unit=UNSET_UNIT,
)
def max_miete_m_lookup_mit_baujahr(
    raw_max_miete_m_nach_baujahr: dict[int | str, dict[int, dict[int, float]]],
    max_anzahl_personen: dict[str, int],
    xnp: ModuleType,
) -> LookupTableBaujahr:
    """Maximum rent considered in Wohngeld calculation."""
    tmp = raw_max_miete_m_nach_baujahr.copy()
    per_additional_person = tmp.pop("jede_weitere_person")
    max_n_p_defined = max(tmp.keys())
    if not all(isinstance(i, int) for i in tmp):  # pragma: no cover
        raise ValueError("All keys must be integers")
    baujahre = sorted(tmp[1].keys())
    lookup_dict = {}
    for i, baujahr in enumerate(baujahre):
        this_dict = {n_p: tmp[n_p][baujahr] for n_p in tmp}
        for n_p in range(max_n_p_defined + 1, max_anzahl_personen["indizierung"] + 1):  # ty: ignore[unsupported-operator]
            this_dict[n_p] = {
                ms: this_dict[max_n_p_defined][ms]
                + (n_p - max_n_p_defined) * per_additional_person[baujahr][ms]  # ty: ignore[unsupported-operator]
                for ms in this_dict[max_n_p_defined]
            }
        lookup_dict[i] = this_dict

    return LookupTableBaujahr(
        baujahre=xnp.asarray(baujahre),
        lookup_table=get_consecutive_int_lookup_table_param_value(
            raw=lookup_dict, xnp=xnp
        ),
    )


@param_function(
    start_date="2009-01-01", leaf_name="max_miete_m_lookup", unit=UNSET_UNIT
)
def max_miete_m_lookup_ohne_baujahr(
    raw_max_miete_m: dict[int | str, dict[int, float]],
    max_anzahl_personen: dict[str, int],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Maximum rent considered in Wohngeld calculation."""
    expanded = raw_max_miete_m.copy()
    per_additional_person = expanded.pop("jede_weitere_person")
    max_n_p_defined = max(expanded.keys())
    if not all(isinstance(i, int) for i in expanded):  # pragma: no cover
        raise ValueError("All keys must be integers")
    for n_p in range(max_n_p_defined + 1, max_anzahl_personen["indizierung"] + 1):  # ty: ignore[unsupported-operator]
        expanded[n_p] = {
            ms: expanded[max_n_p_defined][ms]
            + (n_p - max_n_p_defined) * per_additional_person[ms]  # ty: ignore[unsupported-operator]
            for ms in expanded[max_n_p_defined]
        }
    return get_consecutive_int_lookup_table_param_value(raw=expanded, xnp=xnp)  # ty: ignore[invalid-argument-type]


@param_function(start_date="1984-01-01", unit=UNSET_UNIT)
def min_miete_lookup(
    raw_min_miete_m: dict[int, float],
    max_anzahl_personen: dict[str, int],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Minimum rent considered in Wohngeld calculation."""
    max_n_p_normal = max_anzahl_personen["normale_berechnung"]
    if max(raw_min_miete_m.keys()) != max_n_p_normal:  # pragma: no cover
        raise ValueError(
            "The maximum number of persons for the normal calculation of the basic"
            "Wohngeld formula `max_anzahl_personen['normale_berechnung'] "
            f"(got: {max_n_p_normal}) must be the same as the maximum number of household "
            "members in `koeffizienten_berechnungsformel` "
            f"(got: {max(raw_min_miete_m.keys())})"
        )
    expanded = raw_min_miete_m.copy()
    for n_p in range(max_n_p_normal + 1, max_anzahl_personen["indizierung"] + 1):
        expanded[n_p] = raw_min_miete_m[max_n_p_normal]
    return get_consecutive_int_lookup_table_param_value(raw=expanded, xnp=xnp)


@param_function(start_date="2021-01-01", unit=UNSET_UNIT)
def heizkostenentlastung_m_lookup(
    raw_heizkostenentlastung_m: dict[int | str, float],
    max_anzahl_personen: dict[str, int],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Heizkostenentlastung as a lookup table."""
    expanded = raw_heizkostenentlastung_m.copy()
    per_additional_person = expanded.pop("jede_weitere_person")
    max_n_p_defined = max(expanded.keys())
    if not all(isinstance(i, int) for i in expanded):  # pragma: no cover
        raise ValueError("All keys must be integers")
    for n_p in range(max_n_p_defined + 1, max_anzahl_personen["indizierung"] + 1):  # ty: ignore[unsupported-operator]
        expanded[n_p] = (
            expanded[max_n_p_defined] + (n_p - max_n_p_defined) * per_additional_person  # ty: ignore[unsupported-operator]
        )
    return get_consecutive_int_lookup_table_param_value(raw=expanded, xnp=xnp)  # ty: ignore[invalid-argument-type]


@param_function(start_date="2023-01-01", unit=UNSET_UNIT)
def dauerhafte_heizkostenkomponente_m_lookup(
    raw_dauerhafte_heizkostenkomponente_m: dict[int | str, float],
    max_anzahl_personen: dict[str, int],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Dauerhafte Heizkostenenkomponente as a lookup table."""
    expanded = raw_dauerhafte_heizkostenkomponente_m.copy()
    per_additional_person = expanded.pop("jede_weitere_person")
    max_n_p_defined = max(expanded.keys())
    if not all(isinstance(i, int) for i in expanded):  # pragma: no cover
        raise ValueError("All keys must be integers")
    for n_p in range(max_n_p_defined + 1, max_anzahl_personen["indizierung"] + 1):  # ty: ignore[unsupported-operator]
        expanded[n_p] = (
            expanded[max_n_p_defined] + (n_p - max_n_p_defined) * per_additional_person  # ty: ignore[unsupported-operator]
        )
    return get_consecutive_int_lookup_table_param_value(raw=expanded, xnp=xnp)  # ty: ignore[invalid-argument-type]


@param_function(start_date="2023-01-01", unit=UNSET_UNIT)
def klimakomponente_m_lookup(
    raw_klimakomponente_m: dict[int | str, float],
    max_anzahl_personen: dict[str, int],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Klimakomponente as a lookup table."""
    expanded = raw_klimakomponente_m.copy()
    per_additional_person = expanded.pop("jede_weitere_person")
    max_n_p_defined = max(expanded.keys())
    if not all(isinstance(i, int) for i in expanded):  # pragma: no cover
        raise ValueError("All keys must be integers")
    for n_p in range(max_n_p_defined + 1, max_anzahl_personen["indizierung"] + 1):  # ty: ignore[unsupported-operator]
        expanded[n_p] = (
            expanded[max_n_p_defined] + (n_p - max_n_p_defined) * per_additional_person  # ty: ignore[unsupported-operator]
        )
    return get_consecutive_int_lookup_table_param_value(raw=expanded, xnp=xnp)  # ty: ignore[invalid-argument-type]


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def miete_m_wthh(
    miete_m_hh: float,
    anzahl_personen_wthh: int,
    anzahl_personen_hh: int,
) -> float:
    """Rent considered in housing benefit calculation on wohngeldrechtlicher
    Teilhaushalt level.
    """
    return cast_unit(
        miete_m_hh * (anzahl_personen_wthh / anzahl_personen_hh),
        TTSIMUnit.CURRENCY.PER_MONTH,
    )


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH)
def min_miete_m_hh(
    anzahl_personen_hh: int,
    min_miete_lookup: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Minimum rent considered in Wohngeld calculation."""
    return cast_unit(
        min_miete_lookup.look_up(anzahl_personen_hh),
        TTSIMUnit.CURRENCY.PER_MONTH.PER_HH,
    )


@policy_function(
    start_date="1984-01-01",
    end_date="2008-12-31",
    leaf_name="miete_m_hh",
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH,
    # Three input axes with different units resolved via `xnp.searchsorted`, which
    # the dry-run cannot evaluate symbolically.
    verify_units=False,
)
def miete_m_hh_mit_baujahr(
    mietstufe_hh: int,
    wohnen__baujahr_immobilie_hh: int,
    anzahl_personen_hh: int,
    wohnen__bruttokaltmiete_m_hh: float,
    min_miete_m_hh: float,
    max_miete_m_lookup: LookupTableBaujahr,
    xnp: ModuleType,
) -> float:
    """Rent considered in housing benefit calculation on household level until 2008."""
    baujahr_index = xnp.searchsorted(
        max_miete_m_lookup.baujahre,
        wohnen__baujahr_immobilie_hh,
        side="left",
    )
    max_miete_m = max_miete_m_lookup.lookup_table.look_up(
        baujahr_index, anzahl_personen_hh, mietstufe_hh
    )
    return max(min(wohnen__bruttokaltmiete_m_hh, max_miete_m), min_miete_m_hh)


@policy_function(
    start_date="2009-01-01",
    end_date="2020-12-31",
    leaf_name="miete_m_hh",
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH,
)
def miete_m_hh_ohne_baujahr_ohne_heizkostenentlastung(
    mietstufe_hh: int,
    anzahl_personen_hh: int,
    wohnen__bruttokaltmiete_m_hh: float,
    min_miete_m_hh: float,
    max_miete_m_lookup: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Rent considered in housing benefit since 2009."""
    anzahl_personen = cast_unit(anzahl_personen_hh, TTSIMUnit.DIMENSIONLESS)
    max_miete_m = cast_unit(
        max_miete_m_lookup.look_up(anzahl_personen, mietstufe_hh),
        TTSIMUnit.CURRENCY.PER_MONTH.PER_HH,
    )

    return max(min(wohnen__bruttokaltmiete_m_hh, max_miete_m), min_miete_m_hh)


@policy_function(
    start_date="2021-01-01",
    end_date="2022-12-31",
    leaf_name="miete_m_hh",
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH,
)
def miete_m_hh_mit_heizkostenentlastung(
    mietstufe_hh: int,
    anzahl_personen_hh: int,
    wohnen__bruttokaltmiete_m_hh: float,
    min_miete_m_hh: float,
    max_miete_m_lookup: ConsecutiveIntLookupTableParamValue,
    heizkostenentlastung_m_lookup: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Rent considered in housing benefit since 2009."""
    anzahl_personen = cast_unit(anzahl_personen_hh, TTSIMUnit.DIMENSIONLESS)
    max_miete_m = cast_unit(
        max_miete_m_lookup.look_up(anzahl_personen, mietstufe_hh),
        TTSIMUnit.CURRENCY.PER_MONTH.PER_HH,
    )

    heating_allowance_m = heizkostenentlastung_m_lookup.look_up(anzahl_personen)

    return (
        max(min(wohnen__bruttokaltmiete_m_hh, max_miete_m), min_miete_m_hh)
        + heating_allowance_m
    )


@policy_function(
    start_date="2023-01-01",
    leaf_name="miete_m_hh",
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH,
)
def miete_m_hh_mit_heizkostenentlastung_dauerhafte_heizkostenkomponente_klimakomponente(
    mietstufe_hh: int,
    anzahl_personen_hh: int,
    wohnen__bruttokaltmiete_m_hh: float,
    min_miete_m_hh: float,
    max_miete_m_lookup: ConsecutiveIntLookupTableParamValue,
    heizkostenentlastung_m_lookup: ConsecutiveIntLookupTableParamValue,
    dauerhafte_heizkostenkomponente_m_lookup: ConsecutiveIntLookupTableParamValue,
    klimakomponente_m_lookup: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Rent considered in housing benefit since 2009."""
    anzahl_personen = cast_unit(anzahl_personen_hh, TTSIMUnit.DIMENSIONLESS)
    max_miete_m = cast_unit(
        max_miete_m_lookup.look_up(anzahl_personen, mietstufe_hh),
        TTSIMUnit.CURRENCY.PER_MONTH.PER_HH,
    )

    heizkostenentlastung = heizkostenentlastung_m_lookup.look_up(anzahl_personen)
    dauerhafte_heizkostenkomponente = dauerhafte_heizkostenkomponente_m_lookup.look_up(
        anzahl_personen
    )
    klimakomponente = klimakomponente_m_lookup.look_up(anzahl_personen)
    return (
        max(
            min(wohnen__bruttokaltmiete_m_hh, max_miete_m + klimakomponente),
            min_miete_m_hh,
        )
        + heizkostenentlastung
        + dauerhafte_heizkostenkomponente
    )
