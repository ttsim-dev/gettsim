(gep-10)=

# GEP 10 — Units and Dimensionality

```{list-table}
- * Author
  * [Marvin Immesberger](https://github.com/MImmesberger)
- * Status
  * Draft
- * Type
  * Standards Track
- * Created
  * 2026-06-03
- * Resolution
  * (none yet)
```

## Abstract

This GEP introduces explicit units for all nodes in GETTSIM. A unit records what a value
measures, its reference period, and, where relevant, the group to which it belongs.
Examples are Euros per month or square meters per household.

These declarations allow GETTSIM to detect whether a policy function actually computes
the quantity it claims to compute and helps to detect inconsistent calculations before a
simulation is run. For example, GETTSIM will reject operations that add a monthly euro
amount to a yearly euro amount or adding a household total to a Bedarfsgemeinschaft
total without an explicit conversion.

Unit declarations also make historical currency handling explicit. GETTSIM calculates a
policy using the currency in which the applicable law specifies its parameters. Users
supply monetary data and request computed results in either Deutsche Mark or Euro, while
statutory parameter values remain unchanged.

## Motivation and scope

Four problems motivate this GEP.

1. **Arithmetic is not dimensionally validated.** GETTSIM currently treats values with
   different meanings as ordinary numbers. A calculation can therefore add a monthly
   amount to rent per square meter without failing immediately.
1. **Grouping levels are not part of arithmetic validation.** A household total and a
   Bedarfsgemeinschaft total can be combined without an explicit conversion. A missing
   division by the number of people in a group is also not detected.
1. **Historical currencies are represented inconsistently.** Some historical monetary
   parameters retain their statutory Deutsche-Mark values, while others are stored as
   mechanically converted Euro values with the original amount recorded only in
   free-text metadata. However, storing DM values in their converted Euro form violates
   GETTSIM's law-to-code principle.
1. **Reference-period conversion factors are maintained separately.** GETTSIM already
   converts between annual, quarterly, monthly, weekly, and daily values. The numerical
   ratios for those conversions should come from the same unit system that validates
   policy calculations.

The GEP covers the unit infrastructure in TTSIM and the currency and policy declarations
in GETTSIM. It treats Deutsche Mark as the earliest statutory currency modeled by this
proposal.

Notably, the naming conventions defined in {ref}`GEP 1 <gep-1>` (group and time
suffixes) and their automatic conversion are not superseded by this GEP, they remain in
effect.

(gep-10-usage)=

## Usage and impact

### Model users

Most users continue to call `main()` with ordinary arrays or a DataFrame. Users may
provide a `data_currency` argument to specify the currency of their monetary input and
the desired currency of computed results. The default is Euro. Data currency may take up
one of two registered currencies: `EUR` or `DM`.

```python
results = main(
    policy_date_str="1999-01-01",
    data_currency="EUR",
    # Other arguments omitted.
)
```

For this run, GETTSIM:

1. converts currency-denominated input columns from Euro to Deutsche Mark;
1. evaluates the 1999 policy in Deutsche Mark using the statutory parameters; and
1. converts computed currency-denominated results back to Euro.

Input columns without a currency component, requested parameters, and requested input
columns are not converted on output.

(gep-10-trees)=

### Unit-annotated data

Input unit annotations are optional. They are useful when users want GETTSIM to validate
the units of their data in addition to converting its currency. When this input mode is
selected, every leaf must be a `UnitAnnotatedColumn`, including identifiers and
dimensionless columns.

```python
from gettsim import InputData, MainTarget, TTTargets, main
from gettsim.tt import TTSIMUnit, UnitAnnotatedColumn

input_tree = {
    "p_id": UnitAnnotatedColumn(values=[0, 1], unit=TTSIMUnit.DIMENSIONLESS),
    "bg_id": UnitAnnotatedColumn(values=[0, 0], unit=TTSIMUnit.DIMENSIONLESS),
    "geburtsjahr": UnitAnnotatedColumn(
        values=[1980, 2015],
        unit=TTSIMUnit.CALENDAR_YEAR,
    ),
    "einkommen_m": UnitAnnotatedColumn(
        values=[2000.0, 0.0],
        unit=TTSIMUnit.EUR.PER_MONTH,
    ),
}

results = main(
    main_target=MainTarget.results.tree_with_unit_annotations,
    policy_date_str="2025-01-01",
    input_data=InputData.tree_with_unit_annotations(input_tree),
    tt_targets=TTTargets(tree={"transfer": {"betrag_m": None}}),
)
```

The unit tag's physical dimension, period, and grouping level must agree with the
declaration of the corresponding input in GETTSIM's DAG. Only the currency may differ,
in which case the value is converted.

The annotated result tree has the same structure. Computed currency values are tagged
with the concrete data currency, while requested parameters retain their statutory
currency.

### Contributors

Contributors declare units on policy functions, policy inputs, parameters, rounding
specifications, and hand-written aggregations.

#### Policy functions

A policy function declares the unit of its return value. TTSIM validates the function
body against that declaration when the policy environment is checked.

The following function declares the unit `CURRENCY_PER_MONTH_PER_BG`, which means
currency per month and per Bedarfsgemeinschaft. Policy functions are currency agnostic,
i.e. they do not declare the concrete currency they are evaluted in. Only parameters
(and input data) need to declare a concrete currency. This way, functions do not need to
be redefined when the statutory currency changes.

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_BG)
def regelsatz_m_bg(...) -> float: ...

@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_BG)
def mehrbedarf_m_bg(...) -> float: ...

@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_BG)
def betrag_m_bg(regelsatz_m_bg: float, mehrbedarf_m_bg: float) -> float:
    return regelsatz_m_bg + mehrbedarf_m_bg
```

The declaration means currency per month and Bedarfsgemeinschaft. The `_m` suffix must
agree with `PER_MONTH`. The operation is valid because both operands have the same unit.
The result is also `CURRENCY_PER_MONTH_PER_BG`.

The following function is rejected because its operands have different physical units:

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def amount_m(...) -> float: ...

@policy_input(unit=TTSIMUnit.CURRENCY.PER_SQUARE_METER_PER_MONTH)
def rent_per_square_meter_m(...) -> float: ...

@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def incorrect_amount_m(
    amount_m: float,
    rent_per_square_meter_m: float,
) -> float:
    return amount_m + rent_per_square_meter_m
```

**Opting out of unit validation.**

Sometimes, policy function perform correct operations that also violate unit arithmetic,
e.g. cross-level operations (sum a HH and BG amount). In these cases, users can either

1. opt-out of unit validation for the entire policy function by setting
   `verify_units=False` in the decorator, or
1. use `cast_ttsim_unit` to explicitly convert the unit of an operand to the expected
   unit.

For example, the following function is valid because it explicitly converts the unit of
`bg_amount_m` to `CURRENCY_PER_MONTH_PER_HH` before adding it to `hh_amount_m`.

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH)
def hh_amount_m(...) -> float: ...

@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_BG)
def bg_amount_m(...) -> float: ...

@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH_PER_HH)
def correct_amount_m(
    hh_amount_m: float,
    bg_amount_m: float,
) -> float:
    return hh_amount_m + cast_ttsim_unit(
        bg_amount_m,
        TTSIMUnit.CURRENCY.PER_MONTH.PER_HH
    )
```

#### Parameters

Parameter files record the currency and period in which the statute specifies a value.

```yaml
einkommensgrenze_m:
  unit: EUR_PER_MONTH
  type: scalar
  2024-01-01:
    value: 1000.0
```

Currency-denominated parameters must use a concrete currency. A build-time check
requires that currency to equal the statutory currency at the parameter's policy date.

## Backward compatibility

- Bare arrays and the DataFrame/mapper input interface remain supported.
- `data_currency` defaults to Euro in GETTSIM, so current-policy Euro inputs and outputs
  retain their existing denomination.
- The former `reference_period` and `reference_level` fields are removed. Their
  information becomes part of the compositional unit, for example `EUR_PER_YEAR_PER_FG`.
- Existing policy functions, policy inputs, parameter files, and hand-written
  aggregations require unit declarations.
- There is no environment variable that disables all unit validation. Exceptions are
  local to an expression or function. As always, users can turn off **all** validation
  by passing `include_fail_nodes=False` to `main()` (but this is not recommended).

## Detailed description

### Terminology

| Term               | Meaning                                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| quantity           | A value with a declared unit, such as an income, age, share, or head count.                             |
| base               | The numerator of a compositional unit, such as `CURRENCY`, `DIMENSIONLESS`, or `YEARS`.                 |
| period             | The denominator that distinguishes a flow from a stock, such as `MONTH` or `YEAR`.                      |
| grouping level     | The entity to which a group property belongs, such as a household (`hh`) or Bedarfsgemeinschaft (`bg`). |
| bare               | A quantity without a grouping-level denominator. Personal quantities are bare.                          |
| stock              | A quantity without a period denominator, such as wealth or an age.                                      |
| flow               | A quantity with a period denominator, such as income per month.                                         |
| statutory currency | The currency in which the applicable statute specifies monetary amounts at a policy date.               |
| data currency      | The currency of user-provided monetary columns and returned computed results.                           |
| body validation    | Evaluation of a policy-function body with unit-carrying test values instead of data values.             |

(gep-10-vocabulary)=

### Compositional unit vocabulary

A unit consists of one base followed by at most one denominator of each category. The
categories have a fixed order.

```text
base        := CURRENCY
             | EUR | DM | ...
             | DIMENSIONLESS
             | HOURS
             | SQUARE_METER | HECTARE
             | YEARS | MONTHS | DAYS
             | CALENDAR_YEAR | CALENDAR_MONTH | CALENDAR_DAY

physical    := SQUARE_METER | HOURS
period      := MONTH | YEAR | QUARTER | WEEK | DAY
level       := HH | BG | FG | SN | ...

unit        := base
             | base _PER_ physical
             | base _PER_ period
             | base _PER_ level
             | base _PER_ physical _PER_ period
             | base _PER_ physical _PER_ level
             | base _PER_ period _PER_ level
             | base _PER_ physical _PER_ period _PER_ level
```

The parser rejects repeated denominators and non-canonical orderings such as
`EUR_PER_BG_PER_MONTH`. The fluent Python builder enforces the same order through its
return types.

```python
TTSIMUnit.CURRENCY.PER_MONTH.PER_BG
TTSIMUnit.CURRENCY
TTSIMUnit.DIMENSIONLESS
TTSIMUnit.DIMENSIONLESS.PER_FG
TTSIMUnit.HOURS.PER_WEEK
```

The Python representation and the YAML representation are two syntaxes for the same
declaration. For example, `TTSIMUnit.CURRENCY.PER_MONTH.PER_BG` corresponds to
`CURRENCY_PER_MONTH_PER_BG`.

#### Common declarations

| Declaration                           | Resolved dimensionality         | Example                                   |
| ------------------------------------- | ------------------------------- | ----------------------------------------- |
| `CURRENCY_PER_MONTH`                  | `CURRENCY / month` (bare)       | personal monthly income                   |
| `CURRENCY_PER_MONTH_PER_BG`           | `CURRENCY / month / [bg]`       | benefit assigned to a Bedarfsgemeinschaft |
| `CURRENCY`                            | `CURRENCY` (bare)               | personal wealth                           |
| `DIMENSIONLESS`                       | `dimensionless`                 | share, rate, indicator, or personal count |
| `DIMENSIONLESS_PER_FG`                | `1 / [fg]`                      | Familiengemeinschaft indicator            |
| `DIMENSIONLESS_PER_YEAR`              | `1 / year`                      | annual rate applied to a stock            |
| `DIMENSIONLESS_PER_BG`                | `1 / [bg]`                      | persons in a Bedarfsgemeinschaft          |
| `HOURS_PER_WEEK`                      | `[hours] / week` (bare)         | personal weekly working hours             |
| `CURRENCY_PER_HOURS`                  | `CURRENCY / [hours]`            | hourly wage                               |
| `CURRENCY_PER_SQUARE_METER_PER_MONTH` | `CURRENCY / meter**2 / month`   | monthly rent ceiling per square meter     |
| `YEARS`                               | calendar-year duration          | age in years                              |
| `CALENDAR_YEAR`                       | point on the calendar-year axis | birth year                                |

`CURRENCY` is valid only in code-side declarations whose concrete currency depends on
the policy date. Parameter YAML, rounding specifications, and input tags use a concrete
registered currency.

(gep-10-levels)=

### Grouping levels

GETTSIM data has an individual level, identified by `p_id`, and grouping levels
identified by `*_id` columns. Current examples include households (`hh`),
Familiengemeinschaften (`fg`), Bedarfsgemeinschaften (`bg`), tax units (`sn`),
Einsatzgemeinschaften (`eg`), Ehegemeinschaften (`ehe`), and wohngeldrechtliche
Teilhaushalte (`wthh`). See {ref}`GEP 2 <gep-2>`.

A policy package registers the grouping levels used in declarations when it constructs
its unit system. The framework also discovers levels from `*_id` columns in the policy
environment. Each level becomes a separate Pint base dimension. There is no individual
dimension: a quantity that is a property of a person carries no grouping level at all
and is simply bare.

The domain model contains subset and membership relationships between some groups. The
unit system does not encode these relationships. It treats `[hh]`, `[bg]`, and other
levels as non-interconvertible dimensions because group sizes and memberships vary
across observations.

#### Head counts as level conversions

A head count is dimensionless; at a group level it is a count per group, `1 / [group]`.
This makes explicit per-capita calculations dimensionally valid: dividing a group total
by its head count cancels the group level and lands at a bare per-person amount.

```text
wohnen__bruttokaltmiete_m_hh / anzahl_personen_hh
  = (CURRENCY / month / [hh]) / (1 / [hh])
  = CURRENCY / month
```

Multiplication by a head count converts a bare per-person amount to a group total.

```text
familie__anzahl_personen_sn * sparerfreibetrag_y
  = (1 / [sn]) * (CURRENCY / year)
  = CURRENCY / year / [sn]
```

Some policy expressions intentionally interpret a group property at another level. Such
an expression requires `cast_ttsim_unit`, as described in
{ref}`Explicit exceptions <gep-10-opt-out>`.

(gep-10-booleans)=

#### Booleans

A boolean describes an entity. At the individual grain it is bare; at a group level it
carries that level.

| Boolean             | Declaration            | Resolved dimensionality |
| ------------------- | ---------------------- | ----------------------- |
| person indicator    | `DIMENSIONLESS`        | `dimensionless` (bare)  |
| family indicator    | `DIMENSIONLESS_PER_FG` | `1 / [fg]`              |
| household indicator | `DIMENSIONLESS_PER_HH` | `1 / [hh]`              |

The logical operators `&`, `|`, and `^` preserve the level when both operands have the
same level. When their levels differ, the result is bare — the individual "level" —
because the expression is evaluated once per person.

```text
child & requirement_fulfilled_fg
  = dimensionless & (1 / [fg])
  = dimensionless
```

`~` preserves its operand's level. Ordering comparisons require equivalent operand units
and produce a boolean at the operands' level. Equality comparisons are not unit-checked;
see {ref}`Limitations <gep-10-limitations>`.

(gep-10-hours)=

### Physical and calendar dimensions

#### Working hours

Working hours use a dedicated `[hours]` dimension rather than Pint's `[time]` dimension.
Otherwise, hours per week would reduce to a dimensionless ratio and could not be
distinguished from a share.

`HOURS_PER_WEEK` therefore resolves to `[hours] / [time]`.

#### Calendar points and durations

A calendar point and a duration are different kinds of quantities. In TTSIM we denote
points in time with `CALENDAR_YEAR`, `CALENDAR_MONTH`, and `CALENDAR_DAY`. Durations are
denoted with `YEARS`, `MONTHS`, and `DAYS`. For example, a birth year would be
`CALENDAR_YEAR`, while an age in years would be `YEARS`.

The following table defines their supported algebra, where `P` is a point and `D` a
duration on the same calendar axis.

| Operation                      | Result   | Example                        |
| ------------------------------ | -------- | ------------------------------ |
| `P - P`                        | duration | `policy_year - geburtsjahr`    |
| `P + D`, `P - D`               | point    | `geburtsjahr + statutory_age`  |
| `P < P`                        | boolean  | `geburtsjahr <= policy_year`   |
| `P + P`                        | error    | addition of two birth years    |
| `P * n`, `P / n`               | error    | scaling a calendar point       |
| point ordered against duration | error    | birth year compared with age   |
| operation across calendar axes | error    | year point plus month duration |

A month-of-year, day-of-week, or quarter is a cyclic ordinal rather than an absolute
calendar point and therefore uses `DIMENSIONLESS`.

(gep-10-parameters)=

### Parameter declarations

Units are declared at the time of parameter definition. Given the various parameter
types, the declaration rules differ slightly.

#### Scalars and dictionaries

A scalar parameter and a dictionary with homogeneous leaves use one unit declaration.

```yaml
satz:
  unit: EUR_PER_MONTH
  type: scalar
  2023-01-01:
    value: 250.0
  2024-01-01:
    note: Depends on the number of children since 2024.
satz_nach_kindanzahl:
  unit: EUR_PER_MONTH
  type: dict
  2024-01-01:
    1: 250.0
    2: 250.0
```

A dictionary with heterogeneous leaves uses a mapping from leaf keys to units.

```yaml
schedule:
  unit:
    child_amount_y: EUR_PER_YEAR
    max_age: YEARS
  type: dict
  2024-01-01:
    child_amount_y: 3000.0
    max_age: 18
```

The mapping is the union of leaves that can occur over the parameter's complete date
range. At a given policy date, validation requires declarations only for leaves present
in the resolved value.

#### Mapping parameters

A schedule or lookup table is a mapping between quantities. It declares input and output
axes rather than one scalar unit.

```yaml
tarif:
  input_unit: EUR_PER_YEAR
  output_unit: EUR_PER_YEAR
  type: piecewise_quadratic
  # Values omitted.
```

The parameter schema rejects `unit:` on a mapping type that requires `input_unit:` and
`output_unit:`. A time suffix in the parameter name describes the output axis and must
agree with `output_unit`.

`require_converter` parameters use one of three forms:

- one `unit:` token for homogeneous content;
- a per-leaf `unit:` mapping for heterogeneous content; or
- `input_unit:` and `output_unit:` when the blob encodes a mapping between quantities.

Units of `require_converter` parameters can be declared independently from the units of
the corresponding `@param_function` as they may differ depending on the conversions in
the param function.

#### Parameter functions

**Mapping parameters.**

Parameter functions exposing mapping parameters (of type `PiecewisePolynomialParamValue`
or `ConsecutiveIntLookupTableParamValue`) declare their input and output unit via
`unit=InputOutputUnit(...)`:

```python
@param_function(
    unit=InputOutputUnit(
        input_unit=TTSIMUnit.CURRENCY.PER_YEAR,
        output_unit=TTSIMUnit.CURRENCY.PER_YEAR,
    ),
)
def tarif(...) -> PiecewisePolynomialParamValue: ...
```

A converter-produced schedule carries the axes declared by its producing
`@param_function`'s `unit=InputOutputUnit(...)`. Every `look_up` or
`piecewise_polynomial` call on it screens each domain argument against the declared
input axis and yields the declared output axis; no cast is needed at the call.

For a multidimensional lookup table, `InputOutputUnit.input_unit` may be a tuple. Each
tuple element declares the unit of the corresponding positional argument to `look_up`,
and the number of declared axes must match the number of arguments. A
`piecewise_polynomial` has exactly one input axis and therefore does not accept a tuple.
Raw YAML mapping parameters use one `input_unit` token; a tuple is available only on a
converter-produced schedule or an annotated schedule field.

**Structured parameters.**

Parameter functiuons exposing structured parameters in the form of generated dataclasses
declare `unit=UNSET_UNIT` and annotate the fields of the dataclass with units:

```python
@dataclass(frozen=True)
class SatzMitAltersgrenzen:
    satz: Annotated[float, TTSIMUnit.CURRENCY.PER_MONTH]
    altersgrenzen: Altersgrenzen
    nach_anzahl_kinder: Annotated[
        ConsecutiveIntLookupTableParamValue,
        InputOutputUnit(
            input_unit=TTSIMUnit.DIMENSIONLESS,
            output_unit=TTSIMUnit.CURRENCY.PER_MONTH,
        ),
    ]

@param_function(unit=UNSET_UNIT)
def satz_mit_altersgrenzen(...) -> SatzMitAltersgrenzen: ...
```

When a policy function accesses an annotated scalar field, the field's unit is used in
body validation.

If a YAML leaf path matches an annotated field path, validation compares the two
declarations. This detects, for example, a YAML leaf declared as `YEARS` whose matching
field is declared as `TTSIMUnit.CURRENCY`. Renamed or derived fields have no matching
source path and cannot be compared automatically.

(gep-10-auto)=

### Generated nodes and aggregations

#### Reference-period conversions

A generated time-conversion node preserves its source base and grouping level and
changes the period according to its target suffix. For example, `CURRENCY_PER_MONTH`
becomes `CURRENCY_PER_YEAR` for a generated `_y` node. Pint supplies the period ratios
used by the numerical converter functions.

#### Aggregations

| Aggregation         | Base                    | Result level                             |
| ------------------- | ----------------------- | ---------------------------------------- |
| `SUM`, `MIN`, `MAX` | preserved               | target group (a bare source acquires it) |
| `SUM` of a boolean  | `dimensionless`         | target group (`1 / [target]`)            |
| `MEAN`              | preserved               | bare (individual level)                  |
| `COUNT`             | `dimensionless`         | target group (`1 / [target]`)            |
| `ANY`, `ALL`        | boolean `DIMENSIONLESS` | target group                             |

`COUNT` and a `SUM` over a boolean mint a dimensionless count at the target group level
(`1 / [target]`), and are bare at an individual target. `SUM`, `MIN`, and `MAX` over a
non-boolean resolve to the target group level, so a bare source acquires it. A mean is
bare because it is equivalent to a group sum divided by a head count.

```text
(CURRENCY / [hh]) / (1 / [hh])
  = CURRENCY
```

A hand-written aggregation declares its unit. By default, that declaration must exactly
match the unit derived from the source, aggregation type, and target level. An
aggregation whose policy interpretation cannot be represented by these rules may set
`verify_units=False`.

`@agg_by_p_id_function` aggregates to the individual grain, which is bare, so its
results carry no level: a summed or counted `agg_by_p_id` head count is a bare
`dimensionless`. `@group_creation_function` produces identifiers and has no unit
declaration.

(gep-10-declarations)=

### Declaration rules

#### Declaration matrix

| Object                               | Declaration                                        | Currency base                         | Validation                                    |
| ------------------------------------ | -------------------------------------------------- | ------------------------------------- | --------------------------------------------- |
| `@policy_function`                   | required `unit=`                                   | `CURRENCY` for monetary values        | body result, time suffix, and grouping level  |
| `@policy_input`                      | required `unit=`                                   | `CURRENCY` for monetary values        | time suffix and grouping level                |
| scalar or dictionary parameter       | `unit:`                                            | concrete currency for monetary values | schema, time suffix, and statutory currency   |
| mapping parameter                    | `input_unit:` and `output_unit:`                   | concrete currency where applicable    | schema, axes, suffix of the output            |
| structured `@param_function`         | `unit=UNSET_UNIT`                                  | units on fields                       | field use and matching parameter leaves       |
| schedule-producing `@param_function` | required `unit=InputOutputUnit(...)`               | agnostic `CURRENCY` only              | schedule call sites screened against axes     |
| generated time conversion            | assigned automatically                             | inherited agnostic base               | period derived from target suffix             |
| generated aggregation                | assigned automatically                             | inherited agnostic base               | aggregation rule and target level             |
| hand-written aggregation             | required `unit=`                                   | `CURRENCY` for monetary values        | exact match with derived unit unless disabled |
| group-creation function              | none                                               | not applicable                        | exempt because it produces identifiers        |
| rounding specification               | unit required when attached to a monetary function | concrete currency                     | function unit and statutory currency          |
| unit-annotated input column          | required on every leaf in that input mode          | concrete currency                     | declared node unit and data currency          |

`UNSET_UNIT` has two uses that are distinguished by context:

- On a parameter or aggregation for which a unit is required, it denotes a missing
  declaration and causes validation to fail.
- On a structured `@param_function`, it explicitly states that the returned object has
  no single scalar unit. Units are then declared on the return type's fields or at use
  sites.

(gep-10-literals)=

### Numerical literals

A dimensionless numerical literal cannot be added to, subtracted from, or ordered
against a dimensioned quantity. Multiplication and division by a dimensionless factor
are valid.

```python
betrag_m * 0.5  # Valid: the unit remains CURRENCY_PER_MONTH.
einkommen_m < 1000.0  # Invalid: the operands have different units.
```

A dimensioned threshold should normally be a parameter. If it must remain in the
function body, `cast_ttsim_unit` assigns its intended unit.

```python
einkommen_m < cast_ttsim_unit(1000.0, TTSIMUnit.CURRENCY.PER_MONTH)
```

Zero is the only dimensioned-literal exception. It is accepted as an additive identity,
return value, comparison bound, or `min`/`max`/`clip` bound and assumes the other
operand's unit.

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_m(einkommen_m: float, befreit: bool) -> float:
    return 0.0 if befreit else einkommen_m
```

(gep-10-currency)=

### Currency

#### Registration and statutory currency

A policy package constructs one `UnitSystem` containing its currencies, statutory
currency history, and grouping levels. GETTSIM uses Euro as the base currency and
defines Deutsche Mark as `EUR / 1.95583`.

Exactly one currency in a unit system is the base. Every other currency is defined
relative to a currency already present in that system. The statutory-currency mapping is
mandatory.

```python
UNIT_SYSTEM = UnitSystem(
    base_currency="EUR",
    other_currencies={"DM": "EUR / 1.95583"},
    statutory_currencies={
        "0001-01-01": "DM",
        "2002-01-01": "EUR",
    },
    grouping_levels=("hh", "bg", "fg", "sn", "eg", "ehe", "wthh"),
)
```

The first entry treats Deutsche Mark as the earliest statutory currency modeled by this
GEP; it does not attempt to model earlier German currencies.

The policy date determines the computation currency.

#### Parameter and data currencies

Parameters are not converted. Validation instead requires each parameter's concrete
currency to equal the statutory currency at its policy date. This preserves the values
specified by the statute, including legally rounded values introduced at a currency
changeover. The rejected alternative of converting parameters is discussed in
{ref}`Alternatives <gep-10-alternatives>`.

#### Currency changes in parameter histories

A dated parameter entry inherits the most recent earlier unit declaration. A new
declaration replaces the previous declaration from its date onward.

```yaml
arbeitnehmerpauschbetrag_y:
  type: scalar
  1990-01-01:
    unit: DM_PER_YEAR
    value: 2000
  2002-01-01:
    unit: EUR_PER_YEAR
    value: 1044
  2011-01-01:
    value: 1000
```

Resolution uses only declarations at or before the policy date. If neither a top-level
declaration nor an earlier dated declaration exists, the unit is missing.

A dated per-leaf mapping replaces the previous mapping completely and must declare every
leaf present at that date. This rule is independent of `updates_previous`, which
controls merging of parameter values.

(gep-10-rounding)=

#### Rounding specifications

A monetary rounding specification declares the concrete currency and complete unit of
its numerical magnitudes.

```python
@policy_function(
    end_date="2001-12-31",
    leaf_name="zu_versteuerndes_einkommen_y_sn",
    rounding_spec=RoundingSpec(
        base=54,
        direction="down",
        to_add_after_rounding=27,
        reference="§ 32a Abs. 2 EStG",
        unit=TTSIMUnit.DM.PER_YEAR.PER_SN,
    ),
    unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN,
)
def zu_versteuerndes_einkommen_y_sn(): ...
```

The rounding unit must equal the function unit after replacing `CURRENCY` with the
concrete statutory currency. A function that remains active across a statutory-currency
change must be split and receive separate rounding specifications.

(gep-10-checks)=

### Validation and limitations

#### Validation stages

| Stage                         | When                                        | Input                                 | Validates                                                            |
| ----------------------------- | ------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------- |
| declaration validation        | decoration or parameter loading             | declarations                          | required fields, grammar, suffixes, allowed currency bases           |
| environment validation        | policy-environment assembly                 | unit-carrying test values             | function bodies, returns, branches, aggregations, statutory currency |
| input-boundary validation     | processing unit-annotated input in `main()` | user tags and node declarations       | physical dimension, period, level, and source currency               |
| numerical boundary conversion | before and after TT computation             | ordinary arrays and conversion factor | input to statutory currency; computed results to data currency       |

The implementation uses Pint while declarations and policy environments are validated,
while explicitly annotated input is processed, and while numerical conversion factors
are derived. Pint quantities do not enter the compiled tax and transfer function or a
JAX trace. Currency conversion of input and result arrays is ordinary numerical
multiplication at the interface boundary.

#### Function-body validation

For each function argument, TTSIM creates a test value with magnitude one and the unit
of the argument's producer. It evaluates the function body with these values and
compares the result with the function's declared unit.

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH)
def bruttokaltmiete_m_hh(...) -> float: ...

@policy_function(unit=TTSIMUnit.DIMENSIONLESS_PER_HH)
def anzahl_personen_hh(...) -> int: ...

@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def bruttokaltmiete_m(
    bruttokaltmiete_m_hh: float,
    anzahl_personen_hh: int,
) -> float:
    return bruttokaltmiete_m_hh / anzahl_personen_hh
```

The arguments resolve to `CURRENCY / month / [hh]` and `1 / [hh]`. Their division
resolves to `CURRENCY / month` (bare), which matches the declaration.

Conditional branches are explored by re-evaluating the body with different branch
decisions. Each explored return path is checked separately. Vectorized `xnp` operations
implemented by the validator use the same unit rules as their scalar equivalents.

Body validation rejects:

- addition, subtraction, or ordering of non-equivalent quantities;
- a non-zero bare literal used as a dimensioned value;
- a return unit that differs from the declaration in physical dimension, period, or
  grouping level;
- logical operators applied to non-boolean values;
- an untyped numerical value accessed from a structured parameter;
- inconsistent schedule input and output axes; and
- unsupported operations unless the function explicitly disables body validation.

(gep-10-limitations)=

#### Limitations

| Limitation                                                               | Consequence                                                                                                                   | Required action                                                                                |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Equality operators (`==`, `!=`) do not compare units.                    | Sentinel comparisons such as `p_id_empfänger == -1` remain possible, but an incompatible equality comparison is not detected. | Use ordering or an explicit policy condition where dimensional equivalence matters.            |
| Branch exploration is limited to 1,024 paths and 64 decisions per run.   | A body above either limit is not validated automatically.                                                                     | Simplify the body or use `verify_units=False`.                                                 |
| Not every NumPy/JAX or Python operation has a validation implementation. | The environment check rejects an unsupported body.                                                                            | Add validator support, use a local `cast_ttsim_unit`, or use `verify_units=False`.             |
| Group nesting and membership are not represented in the unit registry.   | No automatic conversion exists between group levels.                                                                          | Use a head count, an explicit aggregation, or `cast_ttsim_unit` where substantively justified. |
| A cast is an assertion, not a conversion or proof.                       | An incorrect cast can hide a unit error in that expression.                                                                   | Keep casts local and review them as policy assumptions.                                        |
| `verify_units=False` skips the complete function body.                   | Consumers still use the declared return unit, but the producer body is not validated.                                         | Restrict the opt-out to functions that cannot be represented by the validator.                 |

(gep-10-opt-out)=

#### Explicit exceptions

`cast_ttsim_unit(value, unit)` changes the inferred unit of one expression during body
validation. At numerical execution it returns `value` unchanged. It is appropriate for:

- policy-defined arithmetic whose grouping interpretation differs from the general
  aggregation rules;
- an explicit calendar-granularity conversion; or
- a dimensioned constant that cannot be represented as a parameter.

Because a cast replaces the complete inferred unit, including its grouping level, it
should apply to the smallest expression that requires it.

`verify_units=False` disables body validation for one decorated function or aggregation.
Its declared output unit remains the contract used by consumers. It is appropriate only
when the body uses an unsupported operation, exceeds branch-exploration limits, or
cannot express its policy interpretation using the standard aggregation rules.

## Related work

- {ref}`GEP 1 <gep-1>` defines the time and grouping suffixes validated here.
- {ref}`GEP 2 <gep-2>` defines the `*_id` columns from which grouping levels are found.
- {ref}`GEP 4 <gep-4>` defines the DAG, aggregations, and reference-period conversions.
- {ref}`GEP 5 <gep-5>` defines rounding specifications.
- {ref}`GEP 9 <gep-9>` defines runtime type validation and the user/canonical data
  split.
- [pint](https://pint.readthedocs.io) supplies the unit registry and dimensional
  algebra.

## Implementation

The implementation is divided between TTSIM infrastructure and policy-system
annotations.

- TTSIM [#138](https://github.com/ttsim-dev/ttsim/pull/138) is the open infrastructure
  PR. It contains the registry, compositional vocabulary, dimensions, mandatory
  declarations, aggregation validation, function-body validation, and input-boundary
  validation.
- TTSIM [#141](https://github.com/ttsim-dev/ttsim/pull/141) is the open worked-example
  PR. It annotates the bundled fictional `METTSIM` policy system and validates it across
  policy dates.
- GETTSIM [#1193](https://github.com/ttsim-dev/gettsim/pull/1193) contains this draft
  GEP.
- GETTSIM [#1212](https://github.com/ttsim-dev/gettsim/pull/1212) contains the GETTISM
  rollout.

(gep-10-alternatives)=

## Alternatives

### Keep grouping levels outside Pint

Rejected. A separate grouping tag could reject some incompatible operations but would
duplicate dimensional algebra. Representing levels as dimensions allows head counts to
perform explicit conversions:

```text
(CURRENCY / [hh]) / (1 / [hh]) = CURRENCY
```

### A person level, implied or spelled

Rejected. Earlier drafts kept a distinct individual level `[person]`: an implied leaf on
every individual quantity, so a per-person monthly amount resolved to
`CURRENCY / month / [person]`, head counts were `[person] / [group]`, and the `[person]`
dimension doubled as the count dimension. A spelled variant
(`CURRENCY_PER_MONTH_PER_PERSON`) was considered too, for full symmetry with the group
levels, but two spellings — the bare form and the `_PER_PERSON` form — would then denote
the same unit, violating the one-spelling-per-unit invariant.

The adopted model removes the person level entirely: an individual quantity is simply
bare, and a head count is dimensionless (`1 / [group]` at a group level). This is a
deliberate simplification with a real tradeoff. A person level bought two things: a
level-neutral rate or share (bare `dimensionless`) could be told apart from a per-person
amount (`.../[person]`), and per-capita divisions produced a typed per-person residue
rather than cancelling to bare. Its cost was a more complex model — an implied leaf
whose attachment depended on an extensive-vs-intensive classification of every base, the
`PER_PERSON` spelling duplicating a bare form, and booleans carrying `1 / [person]` at
the individual grain.

### Convert all parameters to a selected run currency

Rejected. Some statutory formulas contain coefficients whose numerical values depend on
the currency convention even when the statute prints them as bare numbers. The Wohngeld
basic formula is an example:

```text
1.15 * (M - (a + b*M + c*Y) * Y)
```

If `M` and `Y` have unit currency per month, then `a` is dimensionless and `b` and `c`
have the implicit unit month per currency. Their numerical values must change when the
currency unit changes. Treating `b` and `c` as dimensionless would be dimensionally
incorrect; converting only `M` and `Y` would change the formula's result.

One possible design would declare the implicit units of every coefficient and rescale
each coefficient when the computation currency changes. This would be dimensionally
complete but would add declarations that are not explicit in the statutory source and
would require conversion rules for heterogeneous structured parameters and polynomial
coefficients.

The adopted design instead evaluates every formula in its statutory currency. Parameters
and coefficients retain their statutory numerical values. Only input data and computed
results cross the currency boundary.

### Pass Pint quantities through the DAG

Rejected. `pint.Quantity` is not a JAX pytree and cannot be used in the compiled JAX
calculation. Units are static properties of nodes, so environment and boundary
validation provide the required checks without changing the numerical representation
inside the TT function.

### Remove currency labels for parameters

Rejected. Concrete currency labels in parameter YAMLs seem redundant because we don't
allow for any other currency than the statutory one at a given policy date (i.e. you
can't pass a EUR parameter to a DM policy date). However, the labels are useful for
validation and for human readers. During implementation it proved to be helpful to
receive automatic validation errors when a parameter is declared in the wrong currency.
Adding concrete currency tags does not demand much work from developers and helps to
prevent painful conversion bugs.

## Discussion

- [GETTSIM #1193: GEP 10 — Units and Dimensionality](https://github.com/ttsim-dev/gettsim/pull/1193)
- [TTSIM #138: units and dimensionality infrastructure](https://github.com/ttsim-dev/ttsim/pull/138)

## References and footnotes

- [GETTSIM #1174: discussion of Deutsche-Mark values](https://github.com/ttsim-dev/gettsim/issues/1174)
- [pint](https://pint.readthedocs.io)
- [NEP 18: NumPy array-function protocol](https://numpy.org/neps/nep-0018-array-function-protocol.html)

## Copyright

This document has been placed in the public domain.
