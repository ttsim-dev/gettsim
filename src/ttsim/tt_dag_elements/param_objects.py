from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

PLACEHOLDER_VALUE = object()
PLACEHOLDER_FIELD = field(default_factory=lambda: PLACEHOLDER_VALUE)

if TYPE_CHECKING:
    import datetime
    from types import ModuleType

    from jaxtyping import Array, Bool, Float, Int

    from ttsim.tt_dag_elements.typing import NestedLookupDict


@dataclass(frozen=True)
class ParamObject:
    """
    Abstract base class for all types of parameters.
    """

    leaf_name: str | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    unit: (
        None
        | Literal[
            "Euros",
            "DM",
            "Share",
            "Percent",
            "Years",
            "Months",
            "Hours",
            "Square Meters",
            "Euros / Square Meter",
        ]
    ) = None
    reference_period: None | Literal["Year", "Quarter", "Month", "Week", "Day"] = None
    name: dict[Literal["de", "en"], str] | None = None
    description: dict[Literal["de", "en"], str] | None = None

    def __post_init__(self) -> None:
        if self.value is PLACEHOLDER_VALUE:  # type: ignore[attr-defined]
            raise ValueError(
                "'value' field must be specified for any type of 'ParamObject'"
            )


@dataclass(frozen=True)
class ScalarParam(ParamObject):
    """
    A scalar parameter directly read from a YAML file.
    """

    value: bool | int | float = PLACEHOLDER_FIELD  # type: ignore[assignment]
    note: str | None = None
    reference: str | None = None


@dataclass(frozen=True)
class DictParam(ParamObject):
    """
    A parameter directly read from a YAML file that is a flat dictionary.
    """

    value: (
        dict[str, int]
        | dict[str, float]
        | dict[str, bool]
        | dict[int, int]
        | dict[int, float]
        | dict[int, bool]
    ) = PLACEHOLDER_FIELD  # type: ignore[assignment]
    note: str | None = None
    reference: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if any(x in self.value for x in ["note", "reference"]):
            raise ValueError(
                "'note' and 'reference' cannot be keys in the value dictionary"
            )


@dataclass(frozen=True)
class PiecewisePolynomialParam(ParamObject):
    """A parameter with its contents read and converted from a YAML file.

    Its value is a PiecewisePolynomialParamValue object, i.e., it contains the
    parameters for calling `piecewise_polynomial`.
    """

    value: PiecewisePolynomialParamValue = PLACEHOLDER_FIELD  # type: ignore[assignment]
    note: str | None = None
    reference: str | None = None


@dataclass(frozen=True)
class ConsecutiveIntLookupTableParam(ParamObject):
    """A parameter with its contents read and converted from a YAML file.

    Its value is a ConsecutiveIntLookupTableParamValue object, i.e., it contains the
    parameters for calling `lookup_table`.
    """

    value: ConsecutiveIntLookupTableParamValue = PLACEHOLDER_FIELD  # type: ignore[assignment]
    note: str | None = None
    reference: str | None = None


class ConsecutiveIntLookupTableParamValue:
    """The `value` for ConsecutiveIntLookupTable."""

    __slots__ = (
        "bases_to_subtract",
        "lookup_multipliers",
        "values_to_look_up",
        "xnp",
    )

    bases_to_subtract: Int[Array, "n_rows n_cols"]
    lookup_multipliers: Int[Array, "n_rows n_cols"]
    values_to_look_up: (
        Float[Array, "n_rows n_cols"]
        | Int[Array, "n_rows n_cols"]
        | Bool[Array, "n_rows n_cols"]
    )
    xnp: ModuleType

    def __init__(
        self,
        xnp: ModuleType,
        values_to_look_up: Float[Array, "n_rows n_cols"]
        | Int[Array, "n_rows n_cols"]
        | Bool[Array, "n_rows n_cols"],
        bases_to_subtract: Int[Array, "n_rows n_cols"],
    ) -> None:
        self.xnp = xnp
        self.values_to_look_up = values_to_look_up.flatten()
        self.bases_to_subtract = xnp.expand_dims(bases_to_subtract, axis=1)
        self.lookup_multipliers = xnp.concatenate(
            [
                (xnp.cumprod(xnp.asarray(values_to_look_up.shape)[::-1])[::-1])[1:],
                xnp.asarray([1]),
            ]
        )

    def look_up(
        self: ConsecutiveIntLookupTableParamValue, *args: int
    ) -> float | int | bool:
        index = self.xnp.asarray(args)
        corrected_index = self.xnp.dot(
            (index - self.bases_to_subtract).T, self.lookup_multipliers
        )
        return self.values_to_look_up[corrected_index]


@dataclass(frozen=True)
class RawParam(ParamObject):
    """
    A parameter directly read from a YAML file that is an arbitrarily nested
    dictionary.
    """

    value: dict[str | int, Any] = PLACEHOLDER_FIELD  # type: ignore[assignment]
    note: str | None = None
    reference: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if any(x in self.value for x in ["note", "reference"]):
            raise ValueError(
                "'note' and 'reference' cannot be keys in the value dictionary"
            )


@dataclass(frozen=True)
class PiecewisePolynomialParamValue:
    """The parameters expected by `piecewise_polynomial`.

    thresholds:
        Thresholds defining the pieces / different segments on the real line.
    intercepts:
        Intercepts of the polynomial on each segment.
    rates:
        Slope and higher-order coefficients of the polynomial on each segment.
    """

    thresholds: Float[Array, " n_segments"]
    intercepts: Float[Array, " n_segments"]
    rates: Float[Array, " n_segments"]


def get_consecutive_int_lookup_table_param_value(
    raw: NestedLookupDict,
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Get the parameters for a N-dimensional lookup table."""
    bases_to_substract = {}

    # Function is recursive to step through all levels of dict
    def process_level(
        i: int, level_i_dict: NestedLookupDict
    ) -> Float[Array, "n_rows n_cols"]:
        sorted_keys = sorted(level_i_dict.keys())
        bases_to_substract[i] = min(xnp.asarray(sorted_keys))
        if isinstance(level_i_dict[sorted_keys[0]], dict):
            return xnp.concatenate(
                [
                    xnp.expand_dims(process_level(i + 1, level_i_dict[key]), axis=0)
                    for key in level_i_dict
                ]
            )
        return xnp.asarray([level_i_dict[k] for k in sorted_keys])

    values = process_level(0, raw)
    return ConsecutiveIntLookupTableParamValue(
        xnp=xnp,
        values_to_look_up=values,
        bases_to_subtract=xnp.asarray(
            [bases_to_substract[key] for key in sorted(bases_to_substract.keys())]
        ),
    )


def _year_fraction(r: dict[Literal["years", "months"], int]) -> float:
    return r["years"] + r["months"] / 12


def get_month_based_phase_inout_of_age_thresholds_param_value(
    raw: dict[str | int, Any],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Get the parameters for month-based phase-in/phase-out of age thresholds.

    Fills up months for which no parameters are given with the last given value.
    """

    def _m_since_ad(y: int, m: int) -> int:
        return y * 12 + (m - 1)

    def _fill_phase_inout(
        raw: dict[int, dict[int, dict[Literal["years", "months"], int]]],
        first_m_since_ad_phase_inout: int,
        last_m_since_ad_phase_inout: int,
    ) -> dict[int, float]:
        lookup_table = {}
        for y, m_dict in raw.items():
            for m, v in m_dict.items():
                lookup_table[_m_since_ad(y=y, m=m)] = _year_fraction(v)
        for m in range(first_m_since_ad_phase_inout, last_m_since_ad_phase_inout):
            if m not in lookup_table:
                lookup_table[m] = lookup_table[m - 1]
        return lookup_table

    first_m_since_ad_to_consider = _m_since_ad(y=raw.pop("first_year_to_consider"), m=1)
    last_m_since_ad_to_consider = _m_since_ad(y=raw.pop("last_year_to_consider"), m=12)
    if not all(isinstance(k, int) for k in raw):
        raise ValueError("All keys must be integers")
    first_year_phase_inout: int = min(raw.keys())  # type: ignore[assignment]
    first_month_phase_inout: int = min(raw[first_year_phase_inout].keys())
    first_m_since_ad_phase_inout = _m_since_ad(
        y=first_year_phase_inout,
        m=first_month_phase_inout,
    )
    last_year_phase_inout: int = max(raw.keys())  # type: ignore[assignment]
    last_month_phase_inout: int = max(raw[last_year_phase_inout].keys())
    last_m_since_ad_phase_inout = _m_since_ad(
        y=last_year_phase_inout,
        m=last_month_phase_inout,
    )
    if first_m_since_ad_to_consider > first_m_since_ad_phase_inout:
        raise ValueError(
            "`first_m_since_ad_to_consider` must be less than or equal to "
            "`first_m_since_ad_phase_inout`."
        )
    if last_m_since_ad_to_consider < last_m_since_ad_phase_inout:
        raise ValueError(
            "`last_m_since_ad_to_consider` must be greater than or equal to "
            "`last_m_since_ad_phase_inout`."
        )
    before_phase_inout: dict[int, float] = {
        b_m: _year_fraction(raw[first_year_phase_inout][first_month_phase_inout])
        for b_m in range(first_m_since_ad_to_consider, first_m_since_ad_phase_inout)
    }
    during_phase_inout: dict[int, float] = _fill_phase_inout(
        raw=raw,  # type: ignore[arg-type]
        first_m_since_ad_phase_inout=first_m_since_ad_phase_inout,
        last_m_since_ad_phase_inout=last_m_since_ad_phase_inout,
    )
    after_phase_inout: dict[int, float] = {
        b_m: _year_fraction(raw[last_year_phase_inout][last_month_phase_inout])
        for b_m in range(
            last_m_since_ad_phase_inout + 1,
            last_m_since_ad_to_consider + 1,
        )
    }
    return get_consecutive_int_lookup_table_param_value(
        raw={**before_phase_inout, **during_phase_inout, **after_phase_inout},
        xnp=xnp,
    )


def get_year_based_phase_inout_of_age_thresholds_param_value(
    raw: dict[str | int, Any],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Get the parameters for year-based phase-in/phase-out of age thresholds.

    Requires all years to be given.
    """
    first_year_to_consider = raw.pop("first_year_to_consider")
    last_year_to_consider = raw.pop("last_year_to_consider")
    if not all(isinstance(k, int) for k in raw):
        raise ValueError("All keys must be integers")
    first_year_phase_inout: int = sorted(raw)[0]  # type: ignore[assignment]
    last_year_phase_inout: int = sorted(raw)[-1]  # type: ignore[assignment]
    if first_year_to_consider > first_year_phase_inout:
        raise ValueError(
            "`first_year_to_consider` must be less than or equal to "
            "`first_year_phase_inout`."
        )
    if last_year_to_consider < last_year_phase_inout:
        raise ValueError(
            "`last_year_to_consider` must be greater than or equal to "
            "`last_year_phase_inout`."
        )
    before_phase_inout: dict[int, float] = {
        b_y: _year_fraction(raw[first_year_phase_inout])
        for b_y in range(first_year_to_consider, first_year_phase_inout)
    }
    during_phase_inout: dict[int, float] = {
        b_y: _year_fraction(raw[b_y])  # type: ignore[misc]
        for b_y in raw
    }
    after_phase_inout: dict[int, float] = {
        b_y: _year_fraction(raw[last_year_phase_inout])
        for b_y in range(last_year_phase_inout + 1, last_year_to_consider + 1)
    }
    return get_consecutive_int_lookup_table_param_value(
        raw={**before_phase_inout, **during_phase_inout, **after_phase_inout},
        xnp=xnp,
    )
