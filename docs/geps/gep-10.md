(gep-10)=

# GEP 10 — Units and Dimensionality

```{list-table}
- * Author
  * [Marvin Immesberger](https://github.com/MImmesberger)
- * Status
  * Accepted
- * Type
  * Standards Track
- * Created
  * 2026-07-24
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/channel/309998-GEPs/topic/GEP.2010/with/612909474)
```

## Abstract

This GEP adds explicit units to TTSIM and GETTSIM. Units are attached to policy
functions, parameters, input columns, automatically generated calculations, rounding
rules, and results. A unit records what a number measures and how it is expressed. For
example, it can distinguish:

- Euro per month from Euro per year;
- wealth from monthly income;
- total rent from rent per square meter; and
- a household total from a total for a Bedarfsgemeinschaft.

TTSIM uses these declarations to check the unit calculations in a policy environment,
meaning the functions and parameters that apply on a particular policy date. When TTSIM
assembles this environment, it runs supported policy formulas with test values that
carry units. It rejects operations that are not dimensionally valid, such as adding a
monthly amount to an annual amount or using an amount of money as the condition in an
`if` statement.

The check is limited in scope. It does not establish that a formula implements the law
correctly, that observations are matched to the right people, or that every physically
dimensionless number has the right economic meaning. A share, an identifier, a category
code, and a count are all dimensionless in the physical sense. The checker can
distinguish them only in the special cases described in this GEP. Likewise, a household
marker helps with selected calculations involving household totals and head counts, but
it does not fully describe the variable's level and does not replace checks of data
layout, merge keys, or group membership. If TTSIM does not know how an operation affects
units, it must reject the operation or record an explicit exception.

The unit declarations also set one rule for historical currencies. Each policy regime is
calculated in the currency used by the law in that regime. GETTSIM converts monetary
input into that statutory currency before the calculation and converts results into the
user's requested currency only after the statutory calculation and rounding are
complete.

## Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and
**OPTIONAL** in this document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in
capital letters.

## Motivation and scope

This GEP addresses four recurring sources of mistakes.

1. **The same storage type can represent different quantities.** In a DataFrame, a
   `float` column may contain wealth, monthly earnings, annual earnings, a share, or
   square meters. Python, NumPy, and JAX allow arithmetic between these columns without
   error, even when the economic quantities are not compatible.
1. **Group calculations can use the wrong level.** A variable's level is the person or
   group for which it is defined or varies: a person, a household, or a
   Bedarfsgemeinschaft. A household total can accidentally be combined with a
   Bedarfsgemeinschaft total. A formula can also forget to divide a group total by the
   number of people in the group. These mistakes are similar to using a variable
   produced by `egen total(), by(hh_id)` as if it were a person-level value.
1. **Historical policy parameters use different currencies.** German statutes contain
   both Deutsche-Mark and Euro amounts. Rewriting all historical values into one
   currency would obscure the values stated in the law and can change formulas that
   contain currency-dependent coefficients.
1. **Period conversions should use one common rule.** GETTSIM already converts flows
   between years, quarters, months, weeks, and days. The same unit system should supply
   these standard ratios and check that the conversions are dimensionally possible.

The scope is deliberately narrow. It uses [Pint](https://pint.readthedocs.io), a Python
library for calculations with units, and covers:

- physical units, reference periods, and a limited set of group markers built with Pint;
- unit declarations for policy functions, inputs, parameters, schedules, structured
  values, automatically generated calculations, aggregations, rounding rules, and
  optionally unit-annotated input data;
- narrow count/indicator evidence attached to the exact scalar, mapping leaf, raw or
  converted schedule axis, schedule output, or structured-field occurrence that it
  authorizes;
- checking the supported expressions inside policy functions;
- explicit rules for conditions, `xnp.where` (an array-valued if-then-else), joins
  (merges), and reductions such as sums over arrays;
- checking every relevant combination of functions, parameters, and statutory currency;
- one statutory computation currency in each policy regime; and
- separate reporting of inferred units, generated rules, local unit assertions, and
  unchecked function bodies.

The GEP does **not** check:

- whether a formula is a correct interpretation of a statute or economic model;
- every difference between dimensionless values such as identifiers, shares,
  probabilities, categories, counts, and rates;
- whether merge keys refer to the same kind of identifier, are unique, or produce the
  intended number of matches;
- whether columns contain the intended observations, are sorted and aligned correctly,
  or are automatically repeated across rows or array dimensions;
- numerical stability, finite values, overflow, or economically sensible ranges;
- arbitrary Python or third-party functions for which TTSIM has no unit rule; or
- legal conventions for day counts, partial periods, and compounding beyond the existing
  automatic period conversions.

The naming rules and automatic period conversions in {ref}`GEP 1 <gep-1>`, group
identifiers in {ref}`GEP 2 <gep-2>`, the directed acyclic graph of calculations and the
aggregation concepts in {ref}`GEP 4 <gep-4>`, rounding in {ref}`GEP 5 <gep-5>`, and the
checks applied to values when the model runs in {ref}`GEP 9 <gep-9>` continue to apply.

(gep-10-guarantee)=

### What a successful check means

When TTSIM successfully checks the calculations inside a policy function—called a body
check in this GEP—it means:

> For every case of the policy formula that TTSIM examined, each supported operation
> used compatible units, and the result had the unit declared by the function.

This conclusion depends on three conditions:

1. the units declared for inputs and parameters are correct;
1. the checker reaches all relevant cases within its documented limits; and
1. TTSIM's checking version of each operation represents the real operation faithfully.

A successful check MUST NOT be summarized as “all functions are unit-correct.”
Documentation and continuous-integration output MUST report at least:

- declarations that were found and resolved;
- policy-function bodies that were checked;
- automatically generated calculations whose units follow a documented rule;
- local uses of `cast_ttsim_unit`;
- bodies excluded with `verify_units=False`;
- bodies rejected because they use an unsupported operation; and
- any other function bodies that were not checked, together with the reason.

(gep-10-usage)=

## Usage and impact

### Users of existing policy environments

Most users continue to call `main()` with unannotated arrays, mappings, or a DataFrame.
The optional `data_currency` argument states the currency of untagged monetary input and
the currency requested for monetary results. In GETTSIM it defaults to Euro.

```python
results = main(
    policy_date_str="1999-01-01",
    data_currency="EUR",
    # Other arguments omitted.
)
```

For this example, GETTSIM:

1. recognizes Deutsche Mark as the currency of the law on 1999-01-01;
1. converts monetary input from Euro to Deutsche Mark;
1. calculates the policy with the Deutsche-Mark parameters and rounding rules stated in
   the law;
1. performs statutory rounding in Deutsche Mark; and
1. converts the calculated monetary results back to Euro.

If users request an input column as part of the output, GETTSIM returns that input
column unchanged. Requested parameters remain in their statutory currency. Within one
policy regime, a policy function does not receive a mixture of DM and EUR amounts.

(gep-10-trees)=

(gep-10-boundary)=

### Unit-annotated data

Users may optionally attach a unit to every input column. This mode suits datasets that
arrive with a known currency and reference period. In this input mode, every final entry
in the nested input (called a leaf in the code) is a `UnitAnnotatedColumn`, including
identifiers and other dimensionless columns.

```python
from gettsim import InputData, MainTarget, TTTargets, main
from gettsim.tt import TTSIMUnit, UnitAnnotatedColumn

input_tree = {
    "p_id": UnitAnnotatedColumn(
        values=[0, 1],
        unit=TTSIMUnit.DIMENSIONLESS,
    ),
    "bg_id": UnitAnnotatedColumn(
        values=[0, 0],
        unit=TTSIMUnit.DIMENSIONLESS,
    ),
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

The data-boundary checks MUST be described exactly. They verify that:

- an unknown unit name is an error;
- the period in the unit agrees exactly with the GEP-1 suffix of the column name;
- the tag and the policy declaration agree on whether the value is monetary, on its
  remaining physical measure and scale, and on its group marker; and
- a stated source currency may differ from the statutory currency and is converted
  before the policy calculation.

For example, TTSIM rejects a column ending in `_m` that is tagged as an annual flow, an
age column tagged as currency, and a household amount tagged as a person-level amount.
The policy declaration remains authoritative; the input tag must agree with it except
for an allowed currency conversion. These checks establish consistency of the stated
units. They do not establish that a dimensionless value has the intended economic
meaning or that observations are matched to the right people and groups.

When users request `MainTarget.results.tree_with_unit_annotations`, calculated results
include their resolved unit and output currency. The unannotated result targets continue
to return plain numerical values.

### Contributors and users extending policy environments

Anyone who adds or changes a policy environment declares units for policy functions,
policy inputs, parameters, rounding specifications, and hand-written aggregations.

#### Policy functions

A policy function declares the unit of the value it returns. When TTSIM assembles the
policy environment, it checks the supported calculations in the function against this
declaration.

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_BG)
def regelsatz_m_bg() -> float: ...


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_BG)
def mehrbedarf_m_bg() -> float: ...


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_BG)
def betrag_m_bg(
    regelsatz_m_bg: float,
    mehrbedarf_m_bg: float,
) -> float:
    return regelsatz_m_bg + mehrbedarf_m_bg
```

In Python declarations, `CURRENCY` means “the currency used by the law at this policy
date.” TTSIM replaces it with the concrete statutory currency. The `_m` suffix must
agree with `PER_MONTH`, and `_bg` must agree with `PER_BG` whenever GEP 1 requires these
suffixes.

The next function is rejected because one argument is a total monthly amount and the
other is a monthly amount per square meter:

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def amount_m() -> float: ...


@policy_input(unit=TTSIMUnit.CURRENCY.PER_SQUARE_METER.PER_MONTH)
def rent_per_square_meter_m() -> float: ...


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def incorrect_amount_m(
    amount_m: float,
    rent_per_square_meter_m: float,
) -> float:
    return amount_m + rent_per_square_meter_m
```

(gep-10-periods)=

#### Stocks, flows, shares, and rates

A stock is measured at a point in time and has no period in its unit. A flow is measured
per year, month, week, or day. Multiplying either by a dimensionless share does not
change whether it is a stock or a flow.

```python
@policy_input(unit=TTSIMUnit.CURRENCY)
def wealth() -> float: ...


@policy_function(unit=TTSIMUnit.CURRENCY)
def retained_wealth(wealth: float) -> float:
    return 0.8 * wealth
```

The result is still wealth because `0.8` is a dimensionless share. Declaring the result
as `CURRENCY.PER_MONTH` would be incorrect.

A rate that converts a stock into a flow includes a period denominator:

```python
@policy_input(unit=TTSIMUnit.DIMENSIONLESS.PER_YEAR)
def interest_rate_y() -> float: ...


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def interest_income_y(
    wealth: float,
    interest_rate_y: float,
) -> float:
    return wealth * interest_rate_y
```

The unit calculation is:

```text
CURRENCY * (1 / year) = CURRENCY / year.
```

Units do not determine how a financial rate compounds. A linear annual rate can use the
automatically generated conversion to a monthly flow. An effective annual rate that
requires `(1 + r_y) ** (1 / 12) - 1`, a continuously compounded rate, or a legal
proration rule MUST use an explicit conversion function. The unit tells us that the rate
is annual; it does not tell us which financial convention applies.

#### Parameters

Parameter files state the concrete currency and period in which the law gives a value.

```yaml
einkommensgrenze_m:
  unit: EUR_PER_MONTH
  type: scalar
  2024-01-01:
    value: 1000.0
```

A monetary parameter MUST name a concrete currency. For every date on which the
parameter entry is used, that currency must be the statutory currency of the policy
regime.

## Backward compatibility

- Unannotated arrays, mappings, and DataFrame inputs remain supported.
- `data_currency` defaults to `EUR`, so present-day Euro input and output keep their
  current denomination.
- One combined unit name such as `EUR_PER_YEAR_PER_FG` replaces the separate
  `reference_period` and `reference_level` fields.
- Existing policy functions, policy inputs, parameter files, hand-written aggregations,
  and monetary rounding rules need unit declarations.
- `DIMENSIONLESS` continues to cover shares, rates without a period, identifiers,
  categories, and other physically dimensionless numbers. This GEP does not add a
  separate public unit category for every economic meaning.
- `QuantityKind` is narrow supporting information, not another unit. It is used only to
  distinguish a known count or yes/no indicator from another dimensionless value where a
  group marker is declared. For a multi-axis schedule, any non-generic kind is stated
  separately for each axis.
- `verify_units=False` may exclude one function body from checking, but the report lists
  it as unchecked. It MUST NOT count as a checked body.
- `cast_ttsim_unit` remains available for a local unit assertion. The report lists each
  use separately from units inferred by TTSIM.
- Unit checks are included by default when a policy environment is assembled. When
  explicit output targets are supplied, `include_fail_nodes=False` can omit unit-related
  failure checks from that call. Results from such a call MUST NOT be described as
  unit-validated, even though some invalid declarations may still be rejected earlier.

## Detailed description

(gep-10-principles)=

### Design principles

1. **Use Pint for dimensional arithmetic.** Pint handles physical units and reference
   periods. TTSIM adds only the policy-specific rules described here.
1. **Use group markers for selected group calculations.** They help find mistakes in
   totals, head counts, and indicators at different levels. They do not fully describe a
   variable's level or the layout of the data.
1. **Describe the check accurately.** TTSIM checks a defined set of expressions. It does
   not prove arbitrary Python code correct.
1. **Check every relevant argument.** If a condition, fallback value, key, period, or
   other argument can affect the unit of a supported operation, the checker MUST inspect
   it.
1. **Reject unsupported changes of level.** If an operation may change the level at
   which a result is defined and TTSIM lacks the necessary array or grouping
   information, the checker must not retain the source unit.
1. **Check every distinct policy regime.** A regime may change because a function,
   parameter, rounding rule, or statutory currency changes.
1. **Keep exceptions visible.** A declaration, a generated rule, a checked body, a local
   cast, and a whole-body opt-out provide different levels of assurance and are reported
   separately.
1. **Use one statutory currency per regime.** Monetary values in different statutory
   currencies never enter the same policy-function calculation.

(gep-10-terminology)=

### Terminology

| Term               | Meaning                                                                                                                                                                                                                          |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| quantity           | A value with a unit, such as income, age, a share, or a head count.                                                                                                                                                              |
| base               | What is measured in the numerator, such as `CURRENCY`, `DIMENSIONLESS`, or `YEARS`.                                                                                                                                              |
| period             | A denominator such as `MONTH` or `YEAR` that identifies a flow or rate.                                                                                                                                                          |
| level              | The person or group for which a variable is defined or varies, such as person, household, or Bedarfsgemeinschaft.                                                                                                                |
| group              | A level other than person, such as `HH` or `BG`, which may appear as a denominator.                                                                                                                                              |
| group marker       | A denominator such as `HH` or `BG` that checks selected amounts, counts, or indicators at that level. It is not a complete representation of the level.                                                                          |
| quantity kind      | Narrow supporting information—`GENERIC`, `COUNT`, or `INDICATOR`—used only when deciding whether a dimensionless value may carry a group marker. It belongs to one exact declared value or schedule axis and is not a Pint unit. |
| stock              | A quantity without a period denominator, such as wealth.                                                                                                                                                                         |
| flow               | A quantity with a period denominator, such as monthly income.                                                                                                                                                                    |
| rate               | A multiplier. A rate that converts a stock to a flow has a period denominator.                                                                                                                                                   |
| calendar point     | A location on a calendar, such as the year 2025.                                                                                                                                                                                 |
| calendar ordinal   | A position within a larger calendar unit, such as month 2 or day 15.                                                                                                                                                             |
| calendar duration  | A length of time, such as 18 years or 3 months.                                                                                                                                                                                  |
| statutory currency | The currency in which the law states the active parameters and rounding rules.                                                                                                                                                   |
| data currency      | The currency assumed for untagged input and requested for calculated output.                                                                                                                                                     |
| policy environment | The functions, inputs, parameters, and automatically generated calculations that apply on one policy date.                                                                                                                       |
| leaf               | A final value in a nested input or parameter structure, rather than a dictionary containing further entries.                                                                                                                     |
| body check         | Running supported policy formulas with unit-carrying test values and comparing the result with the declared unit.                                                                                                                |
| cast               | A local assertion that tells the checker to use a stated unit for one expression.                                                                                                                                                |
| opt-out            | `verify_units=False` on one function. Its output declaration still applies, but its calculations are not checked.                                                                                                                |

(gep-10-valuespec)=

(gep-10-vocabulary)=

### How unit names are built

A declaration begins with one base unit. It may then add no more than one physical
denominator, one period denominator, and one group denominator, in that order.

```text
base        := CURRENCY
             | EUR | DM
             | DIMENSIONLESS
             | HOURS
             | SQUARE_METER | HECTARE
             | YEARS | QUARTERS | MONTHS | DAYS
             | CALENDAR_YEAR
             | CALENDAR_QUARTER | CALENDAR_MONTH | CALENDAR_DAY

physical    := SQUARE_METER | HOURS
period      := MONTH | YEAR | QUARTER | WEEK | DAY
group       := HH | BG | FG | SN | EG | EHE | WTHH | ...

unit        := base
             | base _PER_ physical
             | base _PER_ period
             | base _PER_ group
             | base _PER_ physical _PER_ period
             | base _PER_ physical _PER_ group
             | base _PER_ period _PER_ group
             | base _PER_ physical _PER_ period _PER_ group
```

The fixed order gives each unit exactly one spelling. For example,
`EUR_PER_MONTH_PER_YEAR` is invalid because it contains two period denominators.
`EUR_PER_BG_PER_MONTH` is also invalid; the correct order is `EUR_PER_MONTH_PER_BG`.

In Python, units are built by chaining attributes:

```python
TTSIMUnit.CURRENCY.PER_MONTH.PER_BG
TTSIMUnit.CURRENCY
TTSIMUnit.DIMENSIONLESS
TTSIMUnit.DIMENSIONLESS.PER_YEAR
TTSIMUnit.HOURS.PER_WEEK
```

YAML uses the same components joined by `_PER_`.

#### Common declarations

| Declaration                           | Meaning                                      | Example                                                        |
| ------------------------------------- | -------------------------------------------- | -------------------------------------------------------------- |
| `CURRENCY_PER_MONTH`                  | currency per month                           | personal monthly income                                        |
| `CURRENCY_PER_MONTH_PER_BG`           | currency per month for a Bedarfsgemeinschaft | monthly amount assigned to a Bedarfsgemeinschaft               |
| `CURRENCY`                            | a currency stock                             | wealth                                                         |
| `DIMENSIONLESS`                       | no physical unit                             | share, identifier, category, or rate without a period          |
| `DIMENSIONLESS_PER_YEAR`              | one per year                                 | linear annual rate applied to a stock                          |
| `DIMENSIONLESS_PER_BG`                | count or indicator for a Bedarfsgemeinschaft | number of people in the group or a group eligibility indicator |
| `HOURS_PER_WEEK`                      | working hours per week                       | weekly working hours                                           |
| `CURRENCY_PER_HOURS`                  | currency per working hour                    | hourly wage                                                    |
| `CURRENCY_PER_SQUARE_METER_PER_MONTH` | currency per square meter per month          | monthly rent ceiling per square meter                          |
| `YEARS`                               | a duration measured in years                 | age                                                            |
| `CALENDAR_YEAR`                       | a particular calendar year                   | birth year                                                     |
| `CALENDAR_MONTH`                      | a month-of-year number                       | February represented as `2`                                    |

`CURRENCY` is used in Python when the concrete currency depends on the policy date.
TTSIM resolves it to the statutory currency. Parameters, rounding rules, and tagged
input use a concrete currency whenever their denomination is already known.

(gep-10-kinds)=

#### Dimensionless values with different economic meanings

Several economically different values have no physical unit. Examples are a marginal tax
rate, a probability, a person identifier, a category code, and a number of people. All
use `DIMENSIONLESS` unless this GEP gives a more specific rule, such as a period on a
rate or a group marker on a known count or indicator.

For the restricted group-marker rules, TTSIM may record one narrow `QuantityKind`:
`GENERIC`, `COUNT`, or `INDICATOR`. This information is not another public unit and does
not distinguish economic meanings. It answers only whether one particular dimensionless
declaration is independently known to be a count or yes/no indicator. Like any
declaration supplied by an author, explicit `QuantityKind` metadata can be wrong; it
does not prove the economic meaning of the underlying data.

The evidence is local. A scalar function or input, one leaf of a mapping, each input
axis of a raw parameter table or converted schedule, the schedule output, and each
occurrence of a field in a nested structured value are separate declarations. Evidence
for one of them MUST NOT authorize another. In particular, a count description on a
parent object or sibling leaf does not authorize a category leaf; a count axis does not
authorize another schedule axis; and evidence at one occurrence of a reused nested type
does not authorize a different occurrence.

A successful unit check therefore does not show that an identifier was never multiplied
by a share or that two identifiers refer to the same kind of entity. Such checks would
require a separate system for economic meaning and data relations.

(gep-10-subject-index)=

(gep-10-levels)=

### Levels and group markers

In this GEP, a variable's **level** is the person or group for which it is defined or
varies. Examples are person, household, family unit, Bedarfsgemeinschaft, and tax unit.
A level is distinct from a physical unit. GEP 10 nevertheless uses group markers as a
limited check for selected calculations across levels.

GETTSIM stores one row per person and identifies that person with `p_id`. Columns such
as `hh_id`, `fg_id`, `bg_id`, `sn_id`, `eg_id`, `ehe_id`, and `wthh_id` identify groups.
See {ref}`GEP 2 <gep-2>`.

A policy package registers its group levels in the unit system. This creates a
`PER_<GROUP>` component for each group. TTSIM treats the registered groups as different
units, so a household (`HH`) cannot be substituted for a Bedarfsgemeinschaft (`BG`).
There is no `PER_PERSON` component: person is a level, not a group, so a person-level
amount has no group denominator.

#### What a group marker means

A group marker is a limited check on the level; it is not the level itself. A group
marker may be used when a value is:

1. calculated or assigned for a particular target group; and
1. an amount, count, or yes/no indicator to which the group calculations below apply.

Examples are total monthly rent per household, square meters per household, persons per
household, and a household eligibility indicator.

A group marker is not added merely because a value is stored once per group or repeated
on every person in the group. In particular, shares, rates without a period, and
identifiers remain dimensionless without a group denominator:

```text
housing-cost share of a household     -> DIMENSIONLESS
annual interest rate for a household  -> DIMENSIONLESS_PER_YEAR
household identifier                  -> DIMENSIONLESS
```

This is similar to the distinction between a variable's economic meaning and the way it
happens to be stored after a Stata `merge` or `bysort`: repeating a household share on
all household members does not turn the share into a household total. GEP 10 does not
check whether such repeated values are aligned with the correct rows.

Declaration validation MUST enforce the following restriction. A direct
`DIMENSIONLESS.PER_<GROUP>` declaration is allowed only for a count or yes/no indicator
whose meaning is established independently of its unit **for that exact declaration**.
Generated `COUNT`, the sum of a yes/no indicator, `ANY`, and `ALL` qualify
automatically. A Boolean return type establishes an indicator. A directly declared
integer value may qualify as a count when its own name, documentation, or explicit
`QuantityKind.COUNT` metadata states that interpretation unambiguously, although an
integer return type alone does not distinguish a count from an identifier or category
code.

Evidence MUST NOT be borrowed from an enclosing object, sibling mapping leaf, another
schedule axis, the schedule output, or another occurrence of the same nested structured
type. General descriptions such as “number of children and rent class” do not establish
that both components are counts. A floating-point share, probability, identifier,
category, or rate without a period carrying a group marker is rejected. If TTSIM cannot
establish one of the permitted cases for the exact declaration carrying the marker, it
MUST reject the declaration rather than guess.

#### Restricted group calculations

TTSIM checks the following group calculations:

1. Multiplying or dividing a group quantity by a quantity that has no group marker
   follows dimensional arithmetic and keeps the group marker. For example, multiplying
   group wealth by an annual interest rate produces an annual group flow.
1. Dividing a group total by the matching group head count removes the group marker and
   gives a person-level amount.
1. Multiplying a person-level amount by the matching group head count adds the group
   marker and gives a group total.
1. Logical operations follow the rules in {ref}`Conditions <gep-10-booleans>`. A yes/no
   indicator whose meaning is known from the operation that produced it may select or
   mask a value at the same group level in a conditional expression or `xnp.where`; its
   group marker is not multiplied into the selected value. Direct multiplication
   receives this special mask rule only when the value is independently known to be a
   yes/no indicator.
1. Other multiplication or division between two non-count group quantities is rejected.
   This avoids results such as “household squared” and accidental cancellation between
   unrelated group properties.
1. Multiplication or division between quantities carrying different group markers is
   rejected.

TTSIM MAY record internally that a value comes from `COUNT`, Boolean `SUM`, or another
explicit head-count calculation. This internal information does not create another
public unit.

For example, dividing a household rent total by the household head count produces a
person-level amount:

```text
wohnen__bruttokaltmiete_m_hh / anzahl_personen_hh
  = (CURRENCY / month / [hh]) / (1 / [hh])
  = CURRENCY / month
```

The reverse calculation produces a tax-unit total:

```text
familie__anzahl_personen_sn * sparerfreibetrag_y
  = (1 / [sn]) * (CURRENCY / year)
  = CURRENCY / year / [sn]
```

If a policy deliberately transfers an amount from one group concept to another, the
function must use a local cast or an explicitly declared aggregation. TTSIM does not
infer how households, Bedarfsgemeinschaften, tax units, and other groups overlap.

(gep-10-booleans)=

### Conditions

Policy formulas use conditions to choose between alternatives. GEP 10 does not assign a
separate unit to yes/no values and does not attempt to distinguish the different
meanings of dimensionless values.

For conditions, TTSIM therefore requires only that the value be **dimensionless**. It
rejects a value if it has a physical unit or a period. A value that meets this
requirement may be a yes/no value, an identifier, a count, a share, a category code, or
another dimensionless scalar. Meeting it means only that units do not rule out its use
as a condition. It does not establish which of these meanings the value has.

When a comparison or logical operation produces a yes/no result, TTSIM may use that fact
when checking later operations. This information comes from the operation that produced
the result, not from its `DIMENSIONLESS` unit.

The same dimensionless requirement MUST apply to:

- Python `if` statements and conditional expressions;
- `bool(value)` calls made while branches are checked;
- supported uses of Python `and`, `or`, and `not`, and of `&`, `|`, `^`, and `~` in
  formulas written for array-valued calculation; and
- the `condition` argument of `xnp.where`.

The following function is invalid because `wealth` is an amount of money:

```python
@policy_function(unit=TTSIMUnit.CURRENCY)
def invalid(wealth: float) -> float:
    return wealth if wealth else 0.0
```

`xnp.where` MUST check its condition as well as the two possible results. Rewriting a
scalar conditional as an array-valued `xnp.where` must not remove this check.

When two yes/no results carry the same group marker, the result keeps that marker. If
one is person-level and one is group-level, or if their group markers differ, the result
is treated as person-level because the logical operation is evaluated row by row. This
is a convention about the resulting unit; it does not establish that the underlying rows
are aligned.

Ordering comparisons such as `<` and `>=` require compatible units and produce a
dimensionless yes/no result. Equality comparisons do not compare units, for the reasons
given in {ref}`Trade-offs and limitations <gep-10-limitations>`.

(gep-10-hours)=

### Physical and calendar dimensions

#### Working hours

Working hours use their own `[hours]` dimension. They are not represented as calendar
time. Otherwise, “hours per week” would simplify to a dimensionless fraction and could
not be distinguished from a share.

`HOURS_PER_WEEK` therefore means `[hours] / [time]`.

(gep-10-calendar)=

#### Calendar years, durations, and month/day numbers

A calendar year and a duration in years are different economic variables. The year 2025
is a point on a calendar; an age of 45 is a distance between two calendar points. The
supported calculations are:

| Calculation                            | Result                    | Example                         |
| -------------------------------------- | ------------------------- | ------------------------------- |
| calendar year minus calendar year      | duration                  | `policy_year - geburtsjahr`     |
| calendar year plus or minus duration   | calendar year             | `geburtsjahr + statutory_age`   |
| ordering two calendar years            | condition (true or false) | `geburtsjahr <= policy_year`    |
| calendar year plus calendar year       | error                     | adding two birth years          |
| calendar year times a scalar           | error                     | multiplying a birth year by two |
| calendar year compared with a duration | error                     | comparing birth year with age   |

Quarter of year, month of year, and day of month are positions within a larger calendar
unit. For example, `2 CALENDAR_MONTH` means February and `15 CALENDAR_DAY` means the
fifteenth day of a month. This GEP treats these values as **ordinals**: they may be
compared with values on the same calendar scale, but they do not support general
addition and subtraction with durations.

In particular, the unit system does not assign a meaning to:

```text
December + 2 months
31st day + 1 day
February 29 without a year and calendar
```

The current implementation still represents framework values such as `policy_quarter`,
`policy_month`, and `policy_day` as dimensionless numbers. This is a temporary
implementation limitation, not a different calendar model: a successful unit check does
not certify their ranges or their complete calendar meaning, and it does not permit the
arithmetic ruled out above. Before full conformance, TTSIM must apply the ordinal rules
stated here consistently. A later calendar proposal may add ranges and calendar context
without changing the physical unit system defined here.

Converting an annual flow into a monthly flow is separate from calendar arithmetic.
`CURRENCY_PER_YEAR` to `CURRENCY_PER_MONTH` uses a reference-period ratio; it does not
add or subtract calendar points.

(gep-10-parameters)=

### Parameter declarations

A parameter declares its unit where the parameter is defined. The shape of the unit
declaration follows the shape of the parameter value.

#### Scalars and dictionaries

A scalar parameter and a dictionary whose leaves all have the same unit use one unit
declaration.

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

A dictionary containing different kinds of quantities declares the unit of each leaf.

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

The unit mapping contains every leaf that can appear during the parameter's history. At
a particular date, only the leaves present in the resolved value need declarations.

A dated entry may replace or add a unit declaration. The latest declaration on or before
the policy date applies. If a dated entry supplies a new mapping of leaf units, that
mapping replaces the earlier mapping completely and must declare every leaf present on
that date.

(gep-10-schedules)=

#### Schedules and lookup tables

A schedule or lookup table has one or more input axes and one output. Declaring their
units is the same idea as stating the unit of every running variable and of the result
of a tax schedule.

```yaml
freibetrag_bei_behinderung_gestaffelt_y:
  input_unit: DIMENSIONLESS
  output_unit: EUR_PER_YEAR
  type: piecewise_constant
  # Intervals omitted.
```

For a parameter type that requires `input_unit:` and `output_unit:`, the file-format
rules reject a single `unit:` declaration. A time suffix in the parameter name describes
the output and must agree with `output_unit`.

For a raw parameter table or converted schedule with several input axes, the units are
ordered exactly like the arguments of the lookup call. Each axis is checked separately.
If a dimensionless group-marked axis needs count or indicator evidence, that evidence
belongs to the same position and to no other axis. The output has its own, separate
evidence.

#### Parameter functions

A `@param_function` converts a raw YAML parameter of type `require_converter` into the
object used by policy functions. Its declaration describes the converted object.

A parameter function that produces a schedule declares the unit of every input axis and
of the output:

```python
@param_function(
    unit=InputOutputUnits(
        input_unit=TTSIMUnit.CURRENCY.PER_YEAR,
        output_unit=TTSIMUnit.CURRENCY.PER_YEAR,
    ),
    verify_units=False,
)
def tarif() -> PiecewisePolynomialParamValue: ...
```

A lookup table may have several input axes. Suppose the first axis is a household head
count and the second is a rent class. Only the first may carry the household group
marker and count evidence:

```python
from gettsim.tt import InputOutputUnits, QuantityKind, TTSIMUnit


@param_function(
    unit=InputOutputUnits(
        input_unit=(
            TTSIMUnit.DIMENSIONLESS.PER_HH,
            TTSIMUnit.DIMENSIONLESS,
        ),
        output_unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH,
        input_kind=(
            QuantityKind.COUNT,
            QuantityKind.GENERIC,
        ),
    ),
    verify_units=False,
)
def maximum_rent_m_hh() -> ConsecutiveIntLookupTableParamValue: ...
```

If `input_unit` is a tuple, a non-generic `input_kind` MUST be a tuple of the same
length and is interpreted position by position. A scalar `QuantityKind.COUNT` or
`QuantityKind.INDICATOR` MUST NOT be repeated automatically across several input axes.
The default `QuantityKind.GENERIC` MAY stand for all-generic axes. `output_kind` applies
only to the output and MUST NOT authorize an input axis. An arity mismatch is a
declaration error.

The explicit opt-out applies to the code that constructs the schedule object, which is
not a numerical policy formula. It does not remove the schedule's unit contract: for
every supported `look_up` or `piecewise_polynomial` call, TTSIM checks each input
variable against the corresponding input axis and assigns the declared output unit to
the result. The construction body is nevertheless listed as unchecked in the validation
report.

A structured parameter may use `unit=UNSET_UNIT` only when the object as a whole has no
single unit and every field that carries a quantity has its own annotation.

```python
@dataclass(frozen=True)
class SatzMitAltersgrenzen:
    satz: Annotated[float, TTSIMUnit.CURRENCY.PER_MONTH]
    altersgrenzen: Altersgrenzen
    nach_anzahl_kinder: Annotated[
        ConsecutiveIntLookupTableParamValue,
        InputOutputUnits(
            input_unit=TTSIMUnit.DIMENSIONLESS,
            output_unit=TTSIMUnit.CURRENCY.PER_MONTH,
        ),
    ]


@param_function(unit=UNSET_UNIT)
def satz_mit_altersgrenzen() -> SatzMitAltersgrenzen: ...
```

When a policy function reads an annotated scalar field, the body checker uses the unit
stated on that field. The unit on the corresponding YAML value serves a different
purpose: it describes the raw input to the parameter conversion and controls any
currency conversion before that conversion takes place. TTSIM does not automatically
prove that the parameter-conversion function maps each raw YAML value into an output
field with the intended unit, even when the names coincide, because such a function may
deliberately rename or transform values. That mapping therefore remains a matter for
focused tests and policy review.

Every path through a structured value is validated separately. If the same nested
dataclass type appears under two different fields, TTSIM MUST visit both occurrences and
must not stop after validating the type once. Evidence from an outer field name or
description belongs only to that occurrence. Evidence written directly in the nested
field's type annotation applies to every occurrence of that field because it is part of
the type itself. Reusing a generic nested type for economically different values does
not permit one occurrence—for example, a number of children—to authorize another—for
example, a rent class or identifier. Every annotated field is checked even if no policy
formula reads it.

(gep-10-generated)=

(gep-10-auto)=

### Automatically generated calculations and aggregations

#### Reference-period conversions

An automatic period conversion changes only the period in a unit. For example, changing
a monthly household amount into an annual household amount converts
`CURRENCY_PER_MONTH_PER_HH` to `CURRENCY_PER_YEAR_PER_HH`. The currency, physical unit,
and group marker remain the same.

Pint supplies the standard ratios already used by GETTSIM. These ratios apply to linear
flows. They do not establish the correct legal day count, treatment of partial periods,
or compounding rule for every policy.

The treatment of legally sensitive daily and other period conventions is deferred to
[GETTSIM #1205](https://github.com/ttsim-dev/gettsim/issues/1205). Until that issue is
resolved:

- automatic conversions keep the factors used on `main`;
- the checker confirms that the units are compatible, not that the statute uses the same
  day-count convention; and
- formulas requiring another convention use an explicit policy function rather than an
  automatic suffix conversion.

(gep-10-extensity)=

(gep-10-aggregations)=

#### Aggregations

An aggregation changes the level represented by a value, much like `egen` with a `by()`
option in Stata. TTSIM derives the result unit from the source unit, aggregation type,
and target level.

| Aggregation                 | Quantity being measured       | Level of the result                                 |
| --------------------------- | ----------------------------- | --------------------------------------------------- |
| `SUM` of a non-Boolean      | same as the source            | target group; person-level for an individual target |
| `MIN`, `MAX`, `MEAN`        | same as the source            | target group; person-level for an individual target |
| `COUNT`                     | `DIMENSIONLESS`               | target group; person-level for an individual target |
| `SUM` of a yes/no indicator | `DIMENSIONLESS` count         | target group; person-level for an individual target |
| `ANY`, `ALL`                | `DIMENSIONLESS` yes/no result | target group; person-level for an individual target |

A group mean remains a statistic of that group. For example, a generated `MEAN` of
person-level wealth calculated separately for each household is a household-level
result. Its numerical value may equal household total wealth divided by the household
head count, but the two operations express different interpretations in this GEP: `MEAN`
produces a household statistic, whereas an explicit total-over-head-count calculation
produces a per-person amount. Use the latter, or aggregate to an individual target, only
when the policy intends a per-person allocation.

The same applies to `MIN` and `MAX`: the minimum or maximum is a property of the target
group. The current unit system records the quantity, period, and group level. It does
not otherwise distinguish a total, mean, minimum, and maximum once produced.

A hand-written aggregation declares its result unit. The declaration MUST equal the unit
derived from the source, aggregation type, and target level. If the standard rule does
not express the intended interpretation, the aggregation must use `verify_units=False`.
A later policy function may use a local cast for the smallest affected expression. The
report records either exception.

`@agg_by_p_id_function` assigns results to individual people and therefore has no group
denominator. Group identifiers themselves remain `DIMENSIONLESS`; checking whether two
identifiers belong to the same domain is outside this GEP.

(gep-10-relations)=

#### Joins

A supported `join` receives limited checks, analogous to those available for a Stata
`merge`:

- the foreign and primary keys MUST have no physical unit or period;
- the fallback used for a missing key MUST have a unit compatible with the target,
  except for the documented dimensionless sentinel case; and
- the joined result has the unit of the target variable.

These checks do not show that the two keys identify the same kind of entity, that the
primary key is unique, that the merge has the intended number of matches, or that the
source and destination rows are correct. Existing data and relation checks remain
responsible for these properties.

TTSIM's checking implementation of a join must inspect the keys and the fallback. If a
new join option can affect units and TTSIM has no rule for it, the checker must reject
the call rather than assume the target unit is unchanged.

#### Reductions inside policy functions

Array operations such as `xnp.sum`, `xnp.amin`, and `xnp.amax` may change what one row
of the result represents. Unlike a declared aggregation, a raw reduction does not tell
the checker which observations or array dimensions were combined. This is similar to
seeing a Stata total without knowing the `by()` variables.

The checker therefore MUST reject these reductions inside a checked policy body instead
rather than copying the unit of its input. A function that needs such a reduction must:

- express it as a generated or hand-written aggregation with a declared target level; or
- use `verify_units=False`, which the report then lists as an unchecked body.

The rejection does not mean that reductions are inherently wrong. It means that TTSIM
lacks enough information to certify their result level.

(gep-10-declarations)=

### Declaration rules

#### Declaration matrix

| Object                               | Required declaration                             | Currency                         | What TTSIM checks                                                                                |
| ------------------------------------ | ------------------------------------------------ | -------------------------------- | ------------------------------------------------------------------------------------------------ |
| `@policy_function`                   | `unit=`                                          | abstract `CURRENCY` for money    | declaration, suffixes, and supported cases in the body                                           |
| `@policy_input`                      | `unit=`                                          | abstract `CURRENCY` for money    | declaration and suffixes                                                                         |
| scalar or dictionary parameter       | `unit:`                                          | concrete currency for money      | file format, suffix, and statutory currency                                                      |
| schedule or lookup parameter         | `input_unit:` and `output_unit:`                 | concrete currency where relevant | file format, axis order, and every input/output unit                                             |
| structured `@param_function`         | `unit=UNSET_UNIT`                                | units on fields                  | every complete field path and matching YAML leaves                                               |
| schedule-producing `@param_function` | `InputOutputUnits(...)` and `verify_units=False` | abstract `CURRENCY` in code      | each input axis and the output separately, including exact count/indicator evidence where needed |
| generated period conversion          | automatic                                        | inherited                        | target period from the suffix                                                                    |
| generated aggregation                | automatic                                        | inherited                        | aggregation rule and target level                                                                |
| hand-written aggregation             | `unit=`                                          | abstract `CURRENCY` in code      | exact derived unit unless opted out                                                              |
| group-creation function              | required or generated `DIMENSIONLESS`            | not applicable                   | declaration only                                                                                 |
| rounding specification               | unit required for monetary magnitudes            | concrete currency                | function unit and statutory currency                                                             |
| unit-annotated input                 | unit on every leaf in this mode                  | concrete source currency         | known unit, suffix period, physical measure and scale, group marker, and currency conversion     |

`UNSET_UNIT` is only for a structured result that has no single unit. For all other
parameters, functions, and aggregations, a missing unit declaration is an error.

(gep-10-literals)=

### Numerical constants

Multiplication and division by a dimensionless numerical constant are valid. The
constant keeps or combines with the other value's unit.

```python
betrag_m * 0.5  # CURRENCY_PER_MONTH
wealth * 0.8  # CURRENCY, not CURRENCY_PER_MONTH
```

A non-zero constant with no declared unit cannot be added to, subtracted from, or
ordered against a quantity that has a unit.

```python
einkommen_m < 1000.0  # Invalid: different units.
```

A threshold with a unit belongs in a policy parameter. If it must be written directly in
the function, a local cast states its unit.

```python
einkommen_m < cast_ttsim_unit(
    value=1000.0,
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
```

Zero is the only numerical constant that may adapt to another unit. It may serve as the
neutral value in addition, as one result of a conditional, or as a bound in
`min`/`max`/`clip`.

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_m(einkommen_m: float, befreit: bool) -> float:
    return 0.0 if befreit else einkommen_m
```

This zero rule does not give a constant the meaning of an identifier, category, or
calendar point. Runtime typing and policy review remain responsible for those meanings.

(gep-10-nullability)=

### Missing values and nullability

Missingness is not a physical unit. This GEP does not replace the GEP-9 rules for
nullable values, sentinel values, or the different missing-value representations used by
NumPy and JAX. For a join, the checker tests whether a missing-key fallback has a unit
compatible with the joined value. It does not establish that a particular number is a
valid missing code for an identifier.

For example, `NaN` or `-1` does not gain a missing-value meaning merely because it is
`DIMENSIONLESS`. Policy packages continue to define and validate their missing-value
conventions.

(gep-10-currency-type)=

(gep-10-currency)=

### Currency

#### Supported currencies and statutory currency

A policy package creates one `UnitSystem` with its supported currencies and the dates on
which each currency is statutory. GETTSIM uses Euro as the base currency and defines
Deutsche Mark with the official conversion factor.

```python
UNIT_SYSTEM = UnitSystem(
    currencies={
        "EUR": Currency(statutory_from="2002-01-01"),
        "DM": Currency(
            value="EUR / 1.95583",
            statutory_from="1948-06-20",
        ),
    },
)
```

Exactly one currency is statutory on every supported policy date. All monetary
calculations inside that policy regime use this currency.

For every checked regime, environment assembly MUST verify that:

- each active monetary parameter uses the statutory currency;
- each active monetary rounding rule uses the statutory currency;
- each Python declaration using `CURRENCY` resolves to the statutory currency; and
- no input, parameter, or function introduces another currency into a policy
  calculation.

This rule excludes, by design, any calculation combining DM and EUR amounts inside one
policy regime. A retroactive or carried amount that legally retains another currency
needs a future extension; GEP 10 does not admit it silently.

#### Parameter currency and data currency

GETTSIM does not convert policy parameters. Instead, it verifies that each parameter is
written in the statutory currency for every regime in which it applies. This preserves
the numerical values in the law, including values that were legally rounded when the
currency changed.

Input data may use another currency. Before calculating the policy, GETTSIM converts
monetary inputs into the statutory currency. It converts calculated monetary outputs to
`data_currency` only after applying the policy formula and statutory rounding.

Tagged input columns may therefore contain DM for a Euro policy date or Euro for a DM
policy date. Different tagged input columns may even state different source currencies,
because each is converted separately into the one statutory currency before entering the
policy calculation.

#### Currency changes in parameter histories

A dated parameter entry inherits the latest earlier unit declaration. A new declaration
applies from its own date onward.

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

Only declarations on or before the policy date are used. A change in statutory currency
starts a new validation regime even when the set of active policy functions does not
change.

#### Currency-dependent coefficients

Some legal formulas contain coefficients whose numerical values depend on the currency
used in the formula. Although the law may print these coefficients as plain numbers,
their mathematical units can include inverse powers of currency. The unit vocabulary in
this GEP does not represent every such coefficient.

The rule adopted here is therefore:

- evaluate the entire formula in the statutory currency of the regime;
- keep the statutory coefficient values exactly as written; and
- do not claim that the unit checker verified the full unit meaning of coefficients
  stored as plain values.

These formulas may need a local cast or a body opt-out, which is visible in the report.
Using the statutory currency preserves the formula's numerical convention, but it does
not amount to a unit proof of every coefficient.

(gep-10-rounding)=

#### Rounding specifications

A monetary rounding rule declares the concrete currency and full unit of its numerical
amounts.

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

After `CURRENCY` is replaced by the statutory currency, the rounding unit must equal the
function unit. A function that spans a currency change must be split or use rounding
rules appropriate to each date. Conversion into the user's output currency happens after
rounding.

(gep-10-validation)=

(gep-10-checks)=

### Validation and limitations

#### When checks take place

| Operation                     | When                                                  | What is checked                                                                                                   |
| ----------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| declaration validation        | when a function is decorated or parameters are loaded | required declarations, valid unit names, suffixes, and permitted currencies                                       |
| environment validation        | when a policy environment is assembled for one date   | all required units, units of automatically generated aggregations, and the statutory currency for that date       |
| policy-body checking          | when a policy environment is assembled for one date   | supported calculations and every examined return case                                                             |
| policy-history validation     | in the policy package's automated tests               | one representative date from every interval in which functions, parameters, or statutory currency may differ      |
| tagged-input boundary         | when user input is prepared                           | known unit names, exact period suffixes, physical measure and scale, group marker, and source-currency conversion |
| numerical currency conversion | immediately before and after policy calculation       | input into statutory currency and calculated output into data currency                                            |

TTSIM uses Pint only while it checks declarations and policy environments, processes
unit-annotated input, and obtains currency conversion factors. The tax-and-transfer
calculation continues to use plain NumPy or JAX arrays, so units do not change the
numerical representation used in a simulation.

(gep-10-body-checker)=

#### Checking policy-function calculations

TTSIM calls a policy function with test values that carry the declared units of its
arguments. It repeats the call, taking each side of the `if` statements and conditional
expressions in turn. Each examined return value is compared with the function's
declaration.

TTSIM knows unit rules for a defined set of operations. For each supported operation,
its checking version MUST inspect every argument that can affect the resulting unit.
Scalar and array-valued versions of the same calculation MUST follow equivalent rules.

The checker rejects at least:

- addition, subtraction, or ordering between incompatible units;
- a non-zero constant used as if it had a physical unit;
- a return value with the wrong physical unit, period, or group level;
- an amount, duration, or rate with a period used as a yes/no condition;
- an invalid condition in `xnp.where`;
- an array reduction whose target level cannot be determined;
- a join with a key carrying a physical unit or a fallback with the wrong unit;
- a numerical field from a structured parameter that lacks a unit;
- a group-marked dimensionless leaf, field occurrence, or schedule axis whose own
  count/indicator meaning is not established;
- a schedule called with the wrong input unit, wrong input-axis order or arity, or wrong
  output unit; and
- an operation for which TTSIM has no faithful unit rule, unless the function explicitly
  opts out.

The checker MUST NOT assume that the old unit survives an operation that may change a
physical dimension, period, or group interpretation. In particular, it may not ignore an
array dimension, condition, merge key, fallback, or another argument relevant to units.

The number of branches that TTSIM can examine is limited. If a function exceeds the
documented limit on cases or branch conditions, TTSIM cannot complete the check. The
author must simplify the function or use a reported opt-out.

(gep-10-date-partition)=

(gep-10-policy-dates)=

#### Checking all relevant policy dates

Checking only the start dates of policy functions is not enough. A parameter or the
statutory currency may change while the active functions remain the same. Full-history
validation therefore divides the supported date range into intervals within which the
unit environment is constant.

A new interval MUST begin at:

- every function start date;
- the day after every inclusive function end date;
- every dated parameter entry, including a change only to its value, unit, set of
  leaves, or currency; and
- every change of statutory currency.

Rounding specifications belong to dated function versions in the present design, so a
rounding change is already captured by a function boundary. If a future design allows a
rounding rule to change independently, its date MUST also start a new interval.

`ttsim.testing_utils.get_policy_date_partition` limits these boundaries to the dates
supported by the policy package and returns one representative date per interval, by
default the first. The policy package's automated tests MUST assemble and check the
environment at every returned date. A parameter-only or currency-only change must start
a new interval even when no policy function changes.

(gep-10-evidence)=

(gep-10-coverage)=

#### Validation report

The validation report for a policy package MUST separate the coverage of declarations
from the coverage of function bodies. Field names may differ across implementations, but
the report contains at least:

```text
resolved declarations
checked function bodies
automatically generated calculations checked by rule
local casts used
function bodies opted out with verify_units=False
bodies rejected as unsupported
other function bodies not checked, with reasons
policy-date regimes checked
```

A count is not enough for an exception. The report also names every function or
calculation that uses `cast_ttsim_unit` or `verify_units=False`, and every other
function whose body was not checked.

A project may correctly report that every required declaration is present even when some
bodies are unchecked. It may report that every supported, non-exempt body passed the
unit checker. It MUST NOT call an opted-out body verified, and “100% annotated” MUST NOT
be used as another name for “100% of bodies checked.”

For example, an automated test run might report:

```text
Declarations resolved: 412 / 412
Bodies checked:         371
Generated rules:         28
Casts:                     9
Body opt-outs:             4
Unsupported bodies:        0
Other unchecked bodies:     2
Date regimes:             37
```

(gep-10-failures)=

#### Error messages

A unit error SHOULD identify the policy calculation, date or date interval, source
expression, expected unit, inferred unit, and failing operation. An error in a
conditional or `xnp.where` SHOULD identify the condition or the two incompatible
results. A join error SHOULD say whether a key or fallback caused it. An unsupported
reduction SHOULD name the operation and explain that the checker lacks information about
the observations or array dimensions being combined.

An error message should not present a cast as the standard repair. It may mention a
local cast or body opt-out, but it must explain that the former is an assertion and the
latter removes body coverage.

(gep-10-limitations)=

#### Trade-offs and limitations

**Different dimensionless meanings are checked only where a group marker is declared.**
Shares, identifiers, category codes, counts, yes/no values, rates without a period, and
other unitless scalars all use `DIMENSIONLESS`. Outside the group-marker cases above,
TTSIM cannot reject calculations that confuse these meanings. `QuantityKind` provides
only the narrow, local evidence needed for a dimensionless group marker; it is not a
general semantic type and does not make other arithmetic between dimensionless values
safe. For conditions, TTSIM only requires that the value be dimensionless; meeting that
requirement does not establish the meaning of the remaining dimensionless value.

**Equality does not compare units.** This permits sentinel comparisons such as
`p_id_empfänger == -1`. It also means that the checker does not catch an equality
comparison between monthly and annual income.

**Group markers do not fully describe the level or validate the data layout.** They do
not prove that rows are aligned, keys are unique, a merge has the right number of
matches, or an identifier belongs to a particular domain. For example, a household's
housing-cost share uses `DIMENSIONLESS`, not `DIMENSIONLESS_PER_HH`: the share has no
physical household denominator, even though it varies across households. The group
marker records selected group totals, counts, and indicators, not the level at which a
variable is observed.

**Only selected group calculations are supported.** TTSIM checks the head-count
conversions, scalar changes, logical rules, and generated aggregations stated above.
Other products or ratios involving group-marked values need a local assertion or an
opt-out.

**Branch checking has a limit.** A body that exceeds the limit on cases or branch
conditions is not silently accepted.

**Some operations remain unsupported.** Raw array reductions are rejected. Joins receive
only the unit checks described above; they do not show that the keys identify the same
kind of entity or that the merge produces the intended number of matches.

**Unit-annotated input checks units, not economic meaning or data arrangement.** The
boundary compares monetary status, period, physical measure and scale, and group marker
with the policy declaration, and it converts an allowed source currency. It still cannot
tell whether a dimensionless code is the intended identifier, share, category, or count,
or whether observations are aligned with the correct people and groups.

**Automatic period ratios are conventions.** A valid conversion of units does not prove
that the ratio follows a policy's legal day-count, partial-period, or compounding rule.
See [GETTSIM #1205](https://github.com/ttsim-dev/gettsim/issues/1205).

**Currency is recorded at the regime level.** Each regime has one statutory currency.
The model does not yet support values in different historical legal currencies inside
one policy-function body.

**A cast is an assertion.** If the author states the wrong unit in a cast, the cast can
hide an error. Casts must remain local and appear in the validation report.

(gep-10-exceptions)=

(gep-10-opt-out)=

#### Explicit exceptions

`cast_ttsim_unit(value, unit=unit)` tells the body checker to treat one expression as
having the stated unit. During the numerical calculation, it returns `value` unchanged.

A cast is appropriate for:

- a policy-defined transfer between group concepts that the standard group rules cannot
  derive;
- a constant with a unit that is part of the implementation rather than a statutory
  parameter; or
- a small part of a formula involving a known coefficient or operation outside the
  current vocabulary.

The cast should cover the smallest possible expression. Every cast is named in the
validation report.

`verify_units=False` disables body checking for one decorated function or hand-written
aggregation. The declared output unit still tells downstream functions what the result
represents. An opt-out is appropriate only when the body:

- constructs a schedule or another structured object whose input and output units are
  checked separately;
- uses an unsupported operation;
- exceeds the branch-checking limit; or
- implements a policy interpretation that the documented unit rules cannot express.

Every opt-out is listed separately and does not count toward checked-body coverage. A
policy package with opt-outs may have complete declarations and may assemble
successfully, but it must not claim that every body was checked.

(gep-10-conformance)=

## Conformance and acceptance requirements

An implementation conforms to this GEP only if all of the following hold:

1. every object that requires a unit has a valid declaration;
1. a group marker on a dimensionless value is limited to a known count or indicator;
1. the count/indicator evidence belongs to the exact scalar, mapping leaf, raw or
   converted schedule input axis, schedule output, or structured-field occurrence
   carrying the group marker; it is not borrowed from a sibling, parent description,
   another axis, or another occurrence of a reused nested type;
1. tuple-valued schedule inputs use positionally matched kind evidence of the same
   arity, and a non-generic scalar kind is not broadcast across several axes;
1. unsupported products, ratios, and calculations across group levels are rejected;
1. `MEAN`, `MIN`, and `MAX` produce a result at the target group level;
1. scalar conditions and `xnp.where` reject values with physical units or periods;
1. supported joins inspect both keys and fallbacks, and do not imply that unchecked
   merge properties were validated;
1. a raw reduction fails when TTSIM cannot determine the level of its result;
1. unit-annotated input is checked against the policy declaration for monetary status,
   period, physical measure and scale, and group marker, with source-currency conversion
   handled explicitly;
1. quarter-of-year, month-of-year, and day-of-month values follow the ordinal rules in
   this GEP rather than general calendar-point arithmetic;
1. the checked date intervals include every relevant function boundary, including a
   rounding change attached to a new function version, parameter entry, and
   statutory-currency change;
1. every policy regime uses exactly one statutory currency; and
1. validation output reports declarations, checked bodies, generated rules, casts,
   whole-body opt-outs, and every other unchecked body separately.

Passing the project's existing tests is not enough to demonstrate these requirements.
The implementation tests SHOULD deliberately introduce a mistake for every rule.
Examples include returning a stock where a flow is declared, using money as a condition,
passing an invalid condition to `xnp.where`, using a fallback with the wrong unit in a
join, marking a share as a group total, letting a count axis authorize a rent-class
axis, letting one nested occurrence authorize another occurrence of the same dataclass
type, treating a group mean as person-level, and omitting a date on which only a
parameter or currency changes.

## Related work

- {ref}`GEP 1 <gep-1>` defines the period and group suffixes checked here.
- {ref}`GEP 2 <gep-2>` defines `*_id` columns and group creation.
- {ref}`GEP 4 <gep-4>` defines the calculation graph, aggregations, and generated period
  conversions.
- {ref}`GEP 5 <gep-5>` defines rounding specifications.
- {ref}`GEP 9 <gep-9>` defines checks of values supplied when the model runs and their
  conversion to the standard internal data format.
- [Pint](https://pint.readthedocs.io) supplies the physical-unit definitions and
  dimensional arithmetic.
- [GETTSIM #1205](https://github.com/ttsim-dev/gettsim/issues/1205) tracks legally
  sensitive reference-period conventions.
- [GETTSIM #1219](https://github.com/ttsim-dev/gettsim/issues/1219) records the review
  that led to the narrower guarantee and additional safeguards in this revision.

## Implementation

The implementation is split between TTSIM infrastructure and the unit declarations in
each policy system.

- TTSIM [#138](https://github.com/ttsim-dev/ttsim/pull/138) contains the unit
  definitions, vocabulary, declarations, generated aggregation rules, body checker, and
  input boundary.
- TTSIM [#141](https://github.com/ttsim-dev/ttsim/pull/141) adds units to the fictional
  METTSIM policy system.
- TTSIM [#150](https://github.com/ttsim-dev/ttsim/pull/150) strengthens the checks for
  conditions, `xnp.where`, joins, and reductions; corrects the METTSIM stock/flow
  declaration; and expands the policy-date intervals that are checked.
- GETTSIM [#1193](https://github.com/ttsim-dev/gettsim/pull/1193) contains GEP 10.
- GETTSIM [#1212](https://github.com/ttsim-dev/gettsim/pull/1212) adds the declarations
  to GETTSIM.

Before this GEP is described as implemented, the code and tests must also cover the
requirements added by this revision:

- reject group-level shares and rates while retaining the documented group counts and
  indicators;
- attach count/indicator evidence to the exact declaration it authorizes, including each
  schedule axis and each occurrence of a nested structured field, without broadcasting a
  non-generic kind or reusing evidence from siblings and repeated types;
- restrict general products and ratios between group-marked quantities;
- keep `MEAN` at the target group level rather than treating it as person-level;
- report casts, whole-body opt-outs, and every other body that could not be checked
  separately from checked bodies; and
- implement the calendar-year and ordinal meanings stated here consistently in the
  declarations, checks, and public documentation.

(gep-10-alternatives)=

## Alternatives

### A broader system for units, data levels, and economic meaning

Deferred. A broader design could separately record the physical unit, economic meaning,
level, kind of identifier, whether a value is a total or intensive measure, array
dimensions, calendar meaning, currency history, and missing-value rules. It could then
check more merge operations, row alignment, group-specific shares, and coefficients with
inverse units.

Such a system would require every record listed above, well beyond the unit checks
needed to adopt units in GETTSIM and METTSIM. This GEP therefore focuses on physical
units, periods, and selected group calculations. It rejects an operation when accepting
it would give a misleading impression of coverage. A later GEP may add checks of data
relations or economic meaning without changing the physical-unit rules here.

### A separate public unit for shares or identifiers

Deferred. Pint correctly treats shares and identifiers as having no physical unit.
Distinguishing them would therefore require additional rules beyond Pint. This GEP keeps
the public unit vocabulary small, documents what remains unchecked, and adds only the
condition and group-declaration rules needed for its stated guarantees.

### A complete model of data levels

Deferred. The group markers in this GEP support selected arithmetic; they are not a
complete model of data levels and are not types for rows or merge keys. The kind and
uniqueness of identifiers, the number of merge matches, automatic repetition across rows
or array dimensions, and row alignment remain outside scope. A reduction that would
require such information is rejected instead of being assigned an unchanged unit.

### An explicit person-level unit

Rejected for this proposal. Earlier designs wrote every person amount as
`... / [person]` and every group head count as `[person] / [group]`. This made the
person level explicit but added a component to almost every declaration and allowed two
ways to write the same person-level quantity.

The adopted design leaves person quantities without a group denominator and writes a
group head count as `1 / [group]`. After dividing a group total by its head count, TTSIM
knows that the result no longer carries the group marker. It does not separately record
that the result is stored at the person level.

### Convert every parameter into the selected data currency

Rejected. In some legal formulas, coefficient values depend on the currency in which the
formula is evaluated. Converting only the obvious monetary inputs could change the
formula. The adopted design calculates each regime entirely in its statutory currency,
keeps parameter and coefficient values as written, and converts only input and
calculated output at the boundary.

### Pass Pint quantities through the calculation graph

Rejected. `pint.Quantity` is not part of the intended NumPy/JAX numerical data. Units
are checked while a policy environment is assembled and at its input and output
boundaries. The tax-and-transfer calculation continues to receive plain numbers and
NumPy or JAX arrays.

### Remove concrete currencies from parameter declarations

Rejected. Because each regime uses one statutory currency, concrete labels may appear
redundant. They nevertheless document the denomination in the file and catch a mismatch
with the regime. A Euro parameter used in a Deutsche-Mark regime should produce an
immediate error.

## Discussion

- [GETTSIM #1193: GEP 10 — Units and Dimensionality](https://github.com/ttsim-dev/gettsim/pull/1193)
- [GETTSIM #1219: review of GEP 10 and its prototype implementation](https://github.com/ttsim-dev/gettsim/issues/1219)
- [TTSIM #138: units and dimensionality infrastructure](https://github.com/ttsim-dev/ttsim/pull/138)
- [TTSIM #141: METTSIM annotations](https://github.com/ttsim-dev/ttsim/pull/141)
- [TTSIM #150: targeted GEP-10 guards and date regimes](https://github.com/ttsim-dev/ttsim/pull/150)

## References and footnotes

- [GETTSIM #1174: discussion of Deutsche-Mark values](https://github.com/ttsim-dev/gettsim/issues/1174)
- [GETTSIM #1205: reference-period conversion conventions](https://github.com/ttsim-dev/gettsim/issues/1205)
- [Pint](https://pint.readthedocs.io)
- [NEP 18: NumPy array-function protocol](https://numpy.org/neps/nep-0018-array-function-protocol.html)

## Copyright

This document has been placed in the public domain.
