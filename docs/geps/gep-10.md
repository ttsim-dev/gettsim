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
  * 2026-07-24
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/channel/309998-GEPs/topic/GEP.2010/with/612909474)
```

## Abstract

This GEP introduces explicit units for nodes, parameters, inputs, generated operations,
rounding specifications, and results in TTSIM and GETTSIM. A unit records what a value
measures, whether it is a stock or a flow, its reference period, and, for a restricted
class of measurable group quantities, the group to which it belongs. Examples are Euros
per month, square meters per household, and persons per Bedarfsgemeinschaft.

TTSIM uses these declarations as a **bounded dimensional linter**. During policy-
environment assembly, it evaluates supported policy-function expressions with
unit-carrying placeholders and rejects incompatible arithmetic. It can detect, for
example, addition of a monthly monetary amount to a yearly monetary amount, use of a
currency stock as a branch condition, or a function that declares monthly income but
returns wealth multiplied by a bare share.

The checker is not a proof of arbitrary Python, data alignment, legal correctness, or
semantic correctness among dimensionless values. In particular, it does not generally
distinguish shares, identifiers, categories, counts, and rates that have the same Pint
dimensionality. Grouping-level denominators are a deliberately restricted guard for
measurable group quantities, not a complete model of relational data grain. Operations
whose unit-relevant behavior the checker cannot derive must fail closed or be covered by
an explicit, reported exception.

Unit declarations also make historical currency handling explicit. Each policy regime
has exactly one statutory computation currency. GETTSIM evaluates statutory parameters
and rounding rules in that currency, converts monetary input at the boundary, and
converts computed results only after statutory computation and rounding.

## Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and
**OPTIONAL** in this document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in
capital letters.

## Motivation and scope

Four problems motivate this GEP.

1. **Arithmetic is not dimensionally validated.** TTSIM currently manipulates ordinary
   Python, NumPy, and JAX values. A calculation can therefore add total rent to rent per
   square meter or return a stock from a function that declares a monthly flow.
1. **Selected grouping mistakes are not caught.** A household total and a
   Bedarfsgemeinschaft total can be combined without an explicit conversion. A missing
   division by a group head count can likewise remain invisible.
1. **Historical currencies need one explicit convention.** Some historical monetary
   parameters are specified in Deutsche Mark and others in Euro. Statutory numerical
   values must not be silently rewritten merely to make every policy year use the same
   denomination.
1. **Reference-period conversions are maintained separately.** GETTSIM already converts
   between annual, quarterly, monthly, weekly, and daily flows. The ordinary conversion
   ratios should come from the same unit system that checks the policy expressions.

The adopted design is intentionally narrower than a general static value-type system. It
covers:

- compositional Pint units for physical quantities, reference periods, and restricted
  grouping-level markers;
- declarations on policy functions, policy inputs, parameters, schedules, structured
  values, generated nodes, aggregations, rounding rules, and optional input tags;
- bounded body checking for the documented expression subset;
- explicit handling of truth contexts, `xnp.where`, joins, and unsupported reductions;
- validation over every distinct function, parameter, and statutory-currency regime;
- one statutory computation currency per policy regime; and
- separate reporting of declarations, checked bodies, casts, and whole-body opt-outs.

The GEP does **not** attempt to establish:

- that a policy formula implements the statute or an economic model correctly;
- semantic distinctions among all dimensionless values, such as an identifier, share,
  category, probability, count, or unrestricted scalar;
- nominal key domains, uniqueness, join cardinality, row alignment, broadcasting
  provenance, or general storage grain;
- numerical stability, finiteness, overflow safety, or economically admissible ranges;
- correctness of arbitrary Python or third-party functions; or
- statutory day-count, partial-period, or compounding conventions beyond the existing
  generated reference-period conversions.

The naming conventions and generated reference-period conversions in
{ref}`GEP 1 <gep-1>`, grouping declarations in {ref}`GEP 2 <gep-2>`, DAG and aggregation
concepts in {ref}`GEP 4 <gep-4>`, rounding in {ref}`GEP 5 <gep-5>`, and runtime
user/canonical type split in {ref}`GEP 9 <gep-9>` remain in force.

(gep-10-guarantee)=

### What a successful check means

A successful GEP-10 body check means only the following:

> For every explored path through a supported policy-function body, every operation for
> which TTSIM supplies a unit rule is dimensionally compatible, and every explored
> return value is compatible with the function's declared unit.

This statement is conditional on the declared units of inputs and parameters being
correct, on the checker reaching every relevant path within its documented bounds, and
on every called operation being represented by a faithful validator stand-in.

A successful environment check MUST NOT be described simply as a proof that “all
functions are unit-correct.” Documentation and CI output MUST distinguish at least:

- required declarations that were resolved;
- function bodies that were checked;
- generated nodes whose units were derived from a documented rule;
- local uses of `cast_ttsim_unit`;
- function bodies excluded with `verify_units=False`; and
- bodies rejected because they use an unsupported operation.

(gep-10-usage)=

## Usage and impact

### Users of existing policy environments

Most users continue to call `main()` with ordinary arrays, mappings, or a DataFrame.
Users may provide a `data_currency` argument to specify the denomination assumed for
unannotated monetary input and requested for computed monetary results. The default in
GETTSIM remains Euro.

```python
results = main(
    policy_date_str="1999-01-01",
    data_currency="EUR",
    # Other arguments omitted.
)
```

For this run, GETTSIM:

1. identifies Deutsche Mark as the statutory computation currency on 1999-01-01;
1. converts currency-denominated input from Euro to Deutsche Mark;
1. evaluates the policy using statutory Deutsche-Mark parameters and rounding rules;
1. performs statutory rounding before presentation conversion; and
1. converts computed monetary results back to Euro.

Requested raw input columns are returned unchanged. Requested parameters retain their
statutory currency. A policy function never receives simultaneous DM- and
EUR-denominated monetary quantities within one policy regime.

(gep-10-trees)=

(gep-10-boundary)=

### Unit-annotated data

Input unit annotations are optional. They are useful when users want to state the source
currency and reference period of their data. When this input mode is selected, every
leaf is wrapped in `UnitAnnotatedColumn`, including identifiers and dimensionless
columns.

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

The boundary behavior is deliberately limited and MUST be described exactly:

- a tag built from an unknown unit token fails;
- the tag's period MUST match the column's GEP-1 time suffix exactly;
- a concrete source currency may differ from the run's statutory currency and is
  converted; and
- other physical dimensions and grouping levels are not, in this first implementation,
  compared with the corresponding node declaration at the input boundary.

Thus a `_m` column tagged per year fails, but the boundary alone does not establish that
an unsuffixed age column was not incorrectly tagged as currency. The function and node
declarations remain the source of the computation's units. Unit-annotated input is a
currency-and-period guard, not a fully typed data interface.

When `MainTarget.results.tree_with_unit_annotations` is requested, computed result
leaves carry their resolved unit and concrete output currency. Ordinary result targets
continue to return bare values.

### Contributors and users extending policy environments

Contributors adding functions to a policy environment declare units on policy functions,
policy inputs, parameters, rounding specifications, and hand-written aggregations.

#### Policy functions

A policy function declares the unit of its return value. TTSIM checks the supported
parts of the function body against that declaration when the policy environment is
assembled.

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

`CURRENCY` is abstract in code-side declarations. At a policy date, TTSIM replaces it
with the regime's concrete statutory currency. The `_m` suffix must agree with
`PER_MONTH`, and `_bg` must agree with `PER_BG` where GEP 1 requires the suffix.

The following function is rejected because the operands have different physical units:

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

A stock has no reference-period denominator. A flow has one. Multiplication by a bare
share preserves the stock/flow status of the other operand.

```python
@policy_input(unit=TTSIMUnit.CURRENCY)
def wealth() -> float: ...


@policy_function(unit=TTSIMUnit.CURRENCY)
def retained_wealth(wealth: float) -> float:
    return 0.8 * wealth
```

The result is a stock because `0.8` is dimensionless. Declaring `retained_wealth` as
`CURRENCY.PER_MONTH` would be false.

A rate that turns a stock into a flow carries an inverse-period unit:

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

The inference is

```text
CURRENCY * (1 / year) = CURRENCY / year.
```

The unit system does not infer financial compounding conventions. A linear annual rate
may be converted to a monthly flow with the ordinary generated period ratio. An
effective annual return that requires `(1 + r_y) ** (1 / 12) - 1`, a continuously
compounded rate, or a statute-specific proration MUST use an explicit conversion
function. Units can establish that a rate is per year; they cannot determine the
intended rate convention.

#### Parameters

Parameter files record the concrete currency and period in which a statute specifies a
value.

```yaml
einkommensgrenze_m:
  unit: EUR_PER_MONTH
  type: scalar
  2024-01-01:
    value: 1000.0
```

Currency-denominated parameters MUST use a concrete currency. Validation requires that
currency to equal the statutory computation currency for every policy regime in which
the parameter entry is active.

## Backward compatibility

- Bare arrays and the DataFrame or mapping input interfaces remain supported.
- `data_currency` defaults to `EUR`, so current-policy Euro input and output retain
  their existing denomination.
- The former `reference_period` and `reference_level` fields are replaced by the
  compositional unit, for example `EUR_PER_YEAR_PER_FG`.
- Existing policy functions, policy inputs, parameter files, hand-written aggregations,
  and monetary rounding specifications require unit declarations.
- `DIMENSIONLESS` remains the common unit for shares, rates without a period, IDs,
  categories, and other physically dimensionless values. This GEP deliberately does not
  introduce a public semantic-kind hierarchy.
- `verify_units=False` remains available for one body, but every use is reported as an
  unchecked body. It MUST NOT be counted as body verification.
- `cast_ttsim_unit` remains available as a local assertion. Every use is reported
  separately from inferred operations.
- Unit validation cannot be disabled globally. `include_fail_nodes=False` may skip
  selected fail nodes during environment assembly and annotated-input processing, but
  malformed declarations remain errors.

## Detailed description

(gep-10-principles)=

### Design principles

1. **Pint handles physical and reference-period algebra.** TTSIM does not replace Pint
   with a general value-type system.
1. **Grouping markers have a narrow purpose.** They catch selected group-total,
   head-count, and group-indicator mistakes. They do not model arbitrary row grain.
1. **Claims follow implementation.** A bounded placeholder evaluation is called a
   linter, not a proof of arbitrary Python.
1. **Supported operations inspect every unit-relevant operand.** A stand-in MUST NOT
   discard a condition, fallback, key, period, or other operand and still count the body
   as checked.
1. **Unsupported grain-changing operations fail closed.** In-body reductions are not
   assigned an unchanged unit when the checker lacks axis metadata.
1. **Every distinct policy regime is checked.** Function boundaries alone are not an
   exhaustive date partition; parameter and statutory-currency changes matter too.
1. **Exceptions remain visible.** A declaration, cast, generated rule, checked body, and
   whole-body opt-out are different facts and are reported separately.
1. **One policy regime uses one statutory currency.** Mixed statutory currencies never
   enter the same policy-function body.

(gep-10-terminology)=

### Terminology

| Term               | Meaning                                                                                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| quantity           | A value with a declared unit, such as income, age, a share, or a head count.                                                                           |
| base               | The numerator of a compositional unit, such as `CURRENCY`, `DIMENSIONLESS`, or `YEARS`.                                                                |
| period             | A denominator that distinguishes a flow or rate from a stock or bare quantity, such as `MONTH` or `YEAR`.                                              |
| grouping level     | A restricted denominator identifying the group to which a measurable group quantity, count, or indicator belongs. It is not a complete row-grain type. |
| bare               | A quantity without a grouping-level denominator. Personal quantities and physically dimensionless shares or rates are normally bare.                   |
| stock              | A quantity without a period denominator, such as wealth.                                                                                               |
| flow               | A quantity with a period denominator, such as income per month.                                                                                        |
| rate               | A multiplicative quantity. A rate that turns a stock into a flow carries an inverse-period denominator.                                                |
| calendar point     | A coordinate such as a calendar year.                                                                                                                  |
| calendar ordinal   | A bounded coordinate within a wider context, such as month of year or day of month.                                                                    |
| calendar duration  | A length such as years, months, or days.                                                                                                               |
| statutory currency | The one concrete currency in which a policy regime's monetary parameters and rounding rules are written.                                               |
| data currency      | The currency assumed for unannotated input and requested for computed output.                                                                          |
| body check         | Bounded evaluation of a supported function body with unit-carrying placeholders.                                                                       |
| cast               | A local assertion that replaces the inferred unit of one expression during body checking.                                                              |
| opt-out            | `verify_units=False` on one body; its declaration remains a consumer contract, but the body is not checked.                                            |

(gep-10-valuespec)=

(gep-10-vocabulary)=

### Compositional unit vocabulary

A unit consists of one base followed by at most one denominator from each supported
category. Components have a fixed order.

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
level       := HH | BG | FG | SN | EG | EHE | WTHH | ...

unit        := base
             | base _PER_ physical
             | base _PER_ period
             | base _PER_ level
             | base _PER_ physical _PER_ period
             | base _PER_ physical _PER_ level
             | base _PER_ period _PER_ level
             | base _PER_ physical _PER_ period _PER_ level
```

Each denominator category may appear at most once and must follow the order shown above.
For example, `EUR_PER_MONTH_PER_YEAR` is invalid, as is `EUR_PER_BG_PER_MONTH`; use
`EUR_PER_MONTH_PER_BG`.

In Python, declarations are constructed by chaining attributes:

```python
TTSIMUnit.CURRENCY.PER_MONTH.PER_BG
TTSIMUnit.CURRENCY
TTSIMUnit.DIMENSIONLESS
TTSIMUnit.DIMENSIONLESS.PER_YEAR
TTSIMUnit.HOURS.PER_WEEK
```

The YAML spelling joins the same components with `_PER_`.

#### Common declarations

| Declaration                           | Resolved dimensionality       | Example                                             |
| ------------------------------------- | ----------------------------- | --------------------------------------------------- |
| `CURRENCY_PER_MONTH`                  | `CURRENCY / month`            | personal monthly income                             |
| `CURRENCY_PER_MONTH_PER_BG`           | `CURRENCY / month / [bg]`     | monthly amount assigned to a Bedarfsgemeinschaft    |
| `CURRENCY`                            | `CURRENCY`                    | wealth stock                                        |
| `DIMENSIONLESS`                       | dimensionless                 | share, ID, category, or bare rate                   |
| `DIMENSIONLESS_PER_YEAR`              | `1 / year`                    | linear annual rate applied to a stock               |
| `DIMENSIONLESS_PER_BG`                | `1 / [bg]`                    | persons in, or indicator for, a Bedarfsgemeinschaft |
| `HOURS_PER_WEEK`                      | `[hours] / week`              | weekly working hours                                |
| `CURRENCY_PER_HOURS`                  | `CURRENCY / [hours]`          | hourly wage                                         |
| `CURRENCY_PER_SQUARE_METER_PER_MONTH` | `CURRENCY / meter**2 / month` | monthly rent ceiling per square meter               |
| `YEARS`                               | year duration                 | age or another duration in years                    |
| `CALENDAR_YEAR`                       | calendar-year point           | birth year                                          |
| `CALENDAR_MONTH`                      | month-of-year ordinal         | February represented as `2`                         |

`CURRENCY` is an abstract code-side placeholder. TTSIM resolves it to the statutory
currency for the policy date. Parameters, rounding specifications, and annotated input
use concrete currencies where their denomination is fixed.

(gep-10-kinds)=

#### Dimensionless semantic distinctions

`DIMENSIONLESS` is deliberately not a semantic top type with a complete operation
algebra. It is the physical unit shared by several meanings, including shares,
identifiers, categories, indicators, counts, and bare rates. GEP 10 validates only the
additional cases stated explicitly, such as truth compatibility and restricted
group-level count or indicator declarations.

A successful dimensional check therefore does not prove that an identifier was not
multiplied by a share or that two dimensionless IDs belong to the same nominal domain.
Adding those distinctions requires a separate semantic or relational type proposal.

(gep-10-subject-index)=

(gep-10-levels)=

### Grouping levels

GETTSIM has a person level, identified by `p_id`, and grouping levels identified by
`*_id` columns. Examples include households (`hh`), Familiengemeinschaften (`fg`),
Bedarfsgemeinschaften (`bg`), tax units (`sn`), Einsatzgemeinschaften (`eg`),
Ehegemeinschaften (`ehe`), and wohngeldrechtliche Teilhaushalte (`wthh`). See
{ref}`GEP 2 <gep-2>`.

A policy package registers its grouping levels with its unit system. Each level gains a
`PER_<LEVEL>` builder step and a separate Pint base dimension. There is no person
dimension: a person quantity is bare.

#### What a group marker means

A grouping-level denominator is permitted for a quantity that is both:

1. a property calculated or assigned at the target group; and
1. a measurable amount, count, or boolean indicator for which the supported group
   arithmetic below is meaningful.

Examples include monthly household rent, square meters per household, persons per
household, and a household eligibility indicator.

The grouping marker is **not** attached merely because a value happens to be stored once
per group. In particular, physically dimensionless shares and ordinary multiplicative
rates remain bare:

```text
housing-cost share of a household     -> DIMENSIONLESS
annual interest rate for a household  -> DIMENSIONLESS_PER_YEAR
household identifier                  -> DIMENSIONLESS
```

This GEP does not validate the row ownership or alignment of those bare values. That is
a deliberate limitation rather than a claim that shares or rates lack a group-specific
interpretation.

Declaration validation MUST enforce this restriction. A direct
`DIMENSIONLESS.PER_<LEVEL>` declaration is accepted only when the producer is known to
be boolean or count-like from its Python return annotation or from a generated `COUNT`,
boolean `SUM`, `ANY`, or `ALL` rule. A share, probability, or ordinary rate with a
grouping marker is rejected regardless of storage dtype. When the available metadata
cannot distinguish a count or indicator from another dimensionless value, validation
fails conservatively rather than treating every dimensionless group value as admissible.

#### Restricted group algebra

The checked group algebra is deliberately small.

1. A bare dimensionless scalar may multiply or divide a group quantity without changing
   its group marker.
1. Dividing a group total by a matching group head count cancels the group marker and
   yields a bare per-person quantity.
1. Multiplying a bare per-person quantity by a matching group head count acquires the
   group marker and yields a group total.
1. Logical operations may combine truth-compatible indicators under the rules in
   {ref}`Booleans and truth contexts <gep-10-booleans>`. A known boolean indicator may
   select or mask a same-level quantity through a conditional or `xnp.where`; the
   condition does not multiply its grouping dimension into the selected value. Direct
   multiplication may receive the same mask rule only when the producer is known to be
   boolean.
1. Generic multiplication or division of two other non-count quantities carrying
   grouping markers is rejected. This prevents accidental squared grouping dimensions or
   silent cancellation of two unrelated group properties.
1. Generic multiplication or division of quantities carrying different grouping levels
   is rejected.

The implementation MAY track “count-like” provenance internally for generated `COUNT`,
boolean `SUM`, and explicitly declared head-count producers. This does not create a new
public unit category.

A head-count conversion is valid:

```text
wohnen__bruttokaltmiete_m_hh / anzahl_personen_hh
  = (CURRENCY / month / [hh]) / (1 / [hh])
  = CURRENCY / month
```

and so is the reverse:

```text
familie__anzahl_personen_sn * sparerfreibetrag_y
  = (1 / [sn]) * (CURRENCY / year)
  = CURRENCY / year / [sn]
```

A policy interpretation that transfers an amount from one group concept to another must
use a local cast or an explicitly declared aggregation. The unit system does not infer
membership relations between `[hh]`, `[bg]`, `[eg]`, and other levels.

(gep-10-booleans)=

### Booleans and truth contexts

The public unit vocabulary does not distinguish every semantic kind of dimensionless
value. The unit checker therefore establishes **truth compatibility**, not full Boolean
semantics.

A unit-carrying value is truth-compatible only if it has no physical or period dimension
and carries at most one permitted grouping-level marker. Python annotations and runtime
type validation remain responsible for distinguishing actual booleans from IDs, counts,
shares, and other dimensionless values.

The following contexts MUST apply the same truth-compatibility check:

- Python `if` and conditional expressions;
- `bool(value)` as invoked by branch exploration;
- `not`, `&`, `|`, `^`, and `~` where supported; and
- the `condition` argument of `xnp.where`.

A currency stock, age, annual rate, or monthly amount cannot control a branch:

```python
@policy_function(unit=TTSIMUnit.CURRENCY)
def invalid(wealth: float) -> float:
    return wealth if wealth else 0.0
```

`xnp.where` MUST check its condition before unifying the two result arms. Refactoring a
scalar conditional into a vectorized conditional must not remove a unit check.

Logical operators preserve a common grouping level when both operands have that level.
When one operand is bare and one carries a grouping level, or when the levels differ,
the result is bare because the operation is evaluated row-wise. This rule is a pragmatic
unit rule and is not a general proof of row alignment.

Ordering comparisons require unit-compatible operands and produce a truth-compatible
result. Equality remains unit-blind; see
{ref}`Trade-offs and limitations <gep-10-limitations>`.

(gep-10-hours)=

### Physical and calendar dimensions

#### Working hours

Working hours use a dedicated `[hours]` dimension rather than Pint's calendar-time
dimension. Otherwise, hours per week would reduce to a dimensionless ratio and could not
be distinguished from a share.

`HOURS_PER_WEEK` therefore resolves to `[hours] / [time]`.

(gep-10-calendar)=

#### Calendar points, durations, and ordinals

`CALENDAR_YEAR` is an affine point on the calendar-year axis. `YEARS` is a duration.
Their supported algebra is:

| Operation                      | Result                 | Example                       |
| ------------------------------ | ---------------------- | ----------------------------- |
| point minus point              | duration               | `policy_year - geburtsjahr`   |
| point plus or minus duration   | point                  | `geburtsjahr + statutory_age` |
| ordering of two points         | truth-compatible value | `geburtsjahr <= policy_year`  |
| point plus point               | error                  | adding two birth years        |
| point times scalar             | error                  | scaling a birth year          |
| point ordered against duration | error                  | comparing birth year with age |

Quarter of year, month of year, and day of month are **ordinals**, not context-free
affine points. `2 CALENDAR_MONTH` means February and `15 CALENDAR_DAY` means the
fifteenth day within a wider date context. These declaration tokens are nominal ordinal
markers whose allowed operations are supplied by TTSIM's validator rules; they are not
ordinary Pint affine-point units. They support equality and ordering within the same
ordinal axis, but they do not support generic point-plus-duration or point-minus-point
algebra.

In particular, the unit system does not define:

```text
December + 2 months
31st day + 1 day
February 29 without a year and calendar
```

Framework-provided `policy_quarter`, `policy_month`, and `policy_day` values MAY remain
represented as dimensionless ordinals. This GEP does not claim to validate their
complete calendar semantics. A future calendar proposal may add explicit range and
context rules without changing the physical-unit model adopted here.

Reference-period conversion for flows is separate from calendar arithmetic. Converting
`CURRENCY_PER_YEAR` to `CURRENCY_PER_MONTH` is not calendar-point addition.

(gep-10-parameters)=

### Parameter declarations

Units are declared at parameter definition. Declaration shape follows parameter shape.

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

The unit mapping is the union of leaves that can occur over the parameter's date range.
At one policy date, validation requires declarations only for leaves present in the
resolved value.

A dated entry may replace or introduce a unit declaration. The most recent declaration
at or before the policy date applies. A dated per-leaf mapping replaces the previous
mapping completely and declares every leaf present at that date.

(gep-10-schedules)=

#### Mapping parameters

A schedule or lookup table declares input and output axes rather than one scalar unit.

```yaml
freibetrag_bei_behinderung_gestaffelt_y:
  input_unit: DIMENSIONLESS
  output_unit: EUR_PER_YEAR
  type: piecewise_constant
  # Intervals omitted.
```

The parameter schema rejects `unit:` on a mapping type that requires `input_unit:` and
`output_unit:`. A time suffix in the parameter name describes the output axis and must
agree with `output_unit`.

#### Parameter functions

A `@param_function` converts a raw YAML parameter declared with
`type: require_converter` into the object used by policy functions. Its unit declaration
describes the converted result.

Schedule-producing parameter functions declare input and output units:

```python
@param_function(
    unit=InputOutputUnits(
        input_unit=TTSIMUnit.CURRENCY.PER_YEAR,
        output_unit=TTSIMUnit.CURRENCY.PER_YEAR,
    ),
)
def tarif() -> PiecewisePolynomialParamValue: ...
```

Every supported `look_up` or `piecewise_polynomial` call screens its domain argument
against the declared input axis and yields the declared output unit.

Structured parameters may declare `unit=UNSET_UNIT` only when their result has no single
unit and every unit-carrying field has its own annotation.

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

When a policy function accesses an annotated scalar field, body checking uses the
field's unit. If a YAML leaf path matches an annotated field path, validation compares
the two declarations. Renamed or derived fields have no automatic source-path
comparison.

(gep-10-generated)=

(gep-10-auto)=

### Generated nodes and aggregations

#### Reference-period conversions

A generated reference-period conversion changes only the period component of a unit. For
example, converting a household amount from monthly to yearly changes
`CURRENCY_PER_MONTH_PER_HH` to `CURRENCY_PER_YEAR_PER_HH`; currency, physical
components, and grouping level remain unchanged.

Pint supplies the ordinary ratios used by the existing generated converters. These are
conventions for linear flows. They do not establish that every statute uses the same
day-count or partial-period rule, and they do not convert effective returns by
compounding.

The treatment of daily and other legally sensitive period conventions is deferred to
[GETTSIM #1205](https://github.com/ttsim-dev/gettsim/issues/1205). Until that work is
completed:

- generated conversions retain the factors currently used on `main`;
- the checker establishes dimensional compatibility, not statutory day-count
  correctness; and
- a formula requiring a different convention uses an explicit policy function rather
  than an automatic suffix conversion.

(gep-10-extensity)=

(gep-10-aggregations)=

#### Aggregations

Generated aggregations derive their result unit from the source unit, aggregation type,
and target level.

| Aggregation            | Base                             | Result level                               |
| ---------------------- | -------------------------------- | ------------------------------------------ |
| `SUM` of a non-boolean | preserved                        | target group; bare at an individual target |
| `MIN`, `MAX`, `MEAN`   | preserved                        | target group; bare at an individual target |
| `COUNT`                | `DIMENSIONLESS`                  | target group; bare at an individual target |
| `SUM` of a boolean     | `DIMENSIONLESS` count            | target group; bare at an individual target |
| `ANY`, `ALL`           | truth-compatible `DIMENSIONLESS` | target group; bare at an individual target |

A mean is a statistic of the target group. It does **not** become a person-level value
merely because a symbolic group total divided by a head count would cancel the grouping
denominator. Thus the mean wealth of a household has a household result level. To create
a person-level allocation or per-person amount, use an explicit group-total/head-count
calculation or an aggregation whose declared target is the individual person.

`MIN` and `MAX` likewise remain properties of the target group. The current unit system
does not distinguish totals, means, and extrema beyond the aggregation rule that
produced them; it only checks their base, period, and target level.

A hand-written aggregation declares its unit. That declaration MUST exactly match the
unit derived from its source, aggregation type, and target level. An intentional policy
reinterpretation uses a local cast or `verify_units=False`, both of which are reported.

`@agg_by_p_id_function` assigns each result to an individual person and therefore has no
grouping-level denominator. A group identifier remains `DIMENSIONLESS` because nominal
identifier domains are outside this GEP.

(gep-10-relations)=

#### Joins

The body checker provides only a dimensional join guard. For a supported `join` call:

- modeled foreign and primary keys MUST carry no physical or period dimension;
- the missing-key fallback MUST be unit-compatible with the target, except for the
  documented dimensionless sentinel case; and
- the result inherits the target unit.

This check does **not** establish that the two keys have the same nominal domain, that
the primary key is unique, that cardinality is correct, or that source and destination
rows are aligned. Those properties remain the responsibility of the existing relation
and runtime validation layers.

A join stand-in that ignores a key or fallback is nonconforming. If a future join option
has unit-relevant behavior and no unit rule, the call must be rejected rather than
silently returning the target unit.

#### In-body reductions

Raw array reductions such as `xnp.sum`, `xnp.amin`, and `xnp.amax` can change which rows
or axes a result represents. The current unit checker has no static array-axis metadata
from which to derive that change. It therefore MUST reject these operations during body
checking instead of passing through the operand's unit.

A function requiring such a reduction must either:

- express it as a generated or hand-written aggregation with a declared target level; or
- use `verify_units=False`, which is then reported as an unchecked body.

This conservative refusal closes a false-certification path; it is not a claim that all
reductions are dimensionally invalid.

(gep-10-declarations)=

### Declaration rules

#### Declaration matrix

| Object                               | Declaration                           | Currency base                      | Validation                                               |
| ------------------------------------ | ------------------------------------- | ---------------------------------- | -------------------------------------------------------- |
| `@policy_function`                   | required `unit=`                      | `CURRENCY` for monetary values     | declaration, suffixes, and supported body paths          |
| `@policy_input`                      | required `unit=`                      | `CURRENCY` for monetary values     | declaration and suffixes                                 |
| scalar or dictionary parameter       | `unit:`                               | concrete currency where monetary   | schema, suffix, and statutory currency                   |
| mapping parameter                    | `input_unit:` and `output_unit:`      | concrete currency where applicable | schema and axes                                          |
| structured `@param_function`         | `unit=UNSET_UNIT`                     | units on fields                    | field use and matching parameter leaves                  |
| schedule-producing `@param_function` | `InputOutputUnits(...)`               | abstract `CURRENCY` in code        | schedule call sites                                      |
| generated time conversion            | automatic                             | inherited                          | target period from suffix                                |
| generated aggregation                | automatic                             | inherited                          | aggregation rule and target level                        |
| hand-written aggregation             | required `unit=`                      | abstract `CURRENCY` in code        | exact derived unit unless opted out                      |
| group-creation function              | required or generated `DIMENSIONLESS` | not applicable                     | declaration only                                         |
| rounding specification               | required for monetary magnitudes      | concrete currency                  | function unit and statutory currency                     |
| unit-annotated input                 | required on every leaf in that mode   | concrete source currency           | token vocabulary, suffix period, and currency conversion |

Use `UNSET_UNIT` only for a structured producer with no single unit. For ordinary
parameters, functions, and aggregations, a missing declaration is an error.

(gep-10-literals)=

### Numerical literals

Multiplication and division by a bare numerical literal are valid and preserve or
compose the other operand's unit.

```python
betrag_m * 0.5  # CURRENCY_PER_MONTH
wealth * 0.8  # CURRENCY, not CURRENCY_PER_MONTH
```

A non-zero bare literal cannot be added to, subtracted from, or ordered against a
dimensioned quantity.

```python
einkommen_m < 1000.0  # Invalid: different units.
```

A dimensioned threshold should normally be a parameter. If it must remain in the body, a
local cast gives the literal its intended unit.

```python
einkommen_m < cast_ttsim_unit(
    value=1000.0,
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
```

Zero is the sole polymorphic numerical-literal exception. It may act as an additive
identity, return arm, or `min`/`max`/`clip` bound and adopts the compatible other unit.

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_m(einkommen_m: float, befreit: bool) -> float:
    return 0.0 if befreit else einkommen_m
```

A bare literal cannot acquire an identifier, category, or calendar-point meaning through
this rule. Those distinctions are outside the unit system and remain subject to ordinary
runtime typing and policy review.

(gep-10-nullability)=

### Missing values and nullability

Missingness is not a physical unit. This GEP does not replace GEP 9's runtime treatment
of nullable values, sentinels, or backend-specific missing representations. During body
linting, a missing-key fallback is checked only for dimensional compatibility with the
join target. The unit checker does not prove that a numeric sentinel is valid for a
particular identifier domain.

A `NaN`, `-1`, or other sentinel does not acquire semantic missing-value meaning from
`DIMENSIONLESS`. Policy packages remain responsible for their ordinary runtime and data
validation contracts.

(gep-10-currency-type)=

(gep-10-currency)=

### Currency

#### Registration and statutory currency

A policy package constructs one `UnitSystem` containing its supported currencies and
statutory history. GETTSIM uses Euro as the base currency and defines Deutsche Mark by
the official conversion factor.

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

Exactly one currency is statutory at every supported policy date. That currency is the
**only** denomination permitted inside the active policy computation.

Environment assembly MUST verify that, for every checked regime:

- every active concrete monetary parameter uses the statutory currency;
- every active monetary rounding specification uses the statutory currency;
- every code-side `CURRENCY` declaration resolves to the statutory currency; and
- no active producer introduces a second concrete currency into a policy-function body.

The single-currency invariant deliberately excludes simultaneous DM and EUR values from
one policy regime. Retroactive or carried amounts that must retain a different legal
denomination require a future extension and are not silently admitted by this GEP.

#### Parameters and data currencies

Parameters are not converted. Validation instead requires their concrete currency to
match the statutory currency of every regime in which they are active. This preserves
statutory numerical values, including legally rounded values introduced at a currency
changeover.

Input data may use a different concrete currency. Monetary inputs are converted to the
statutory currency before policy evaluation. Computed monetary outputs are converted to
`data_currency` only after statutory calculation and rounding.

An annotated input may therefore contain DM values for a Euro policy run or Euro values
for a DM policy run. The boundary performs the conversion before the values enter the
DAG. Mixed source currencies across separately annotated input leaves are acceptable
only because each leaf is converted to the one statutory currency before policy
computation.

#### Currency changes in parameter histories

A dated parameter entry inherits the most recent earlier unit declaration. A new unit
declaration applies from its date onward.

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

Resolution uses only declarations at or before the policy date. A statutory-currency
transition opens a new validation regime even when no function starts or ends on that
date.

#### Coefficients whose numerical meaning depends on currency

Some statutory formulas contain coefficients whose mathematical units include inverse
currency, even when the statute prints them as bare numbers. The present compositional
vocabulary does not attempt to encode arbitrary inverse-currency powers for all
structured coefficients.

The adopted first-stage rule is therefore:

- evaluate the complete formula in the one statutory currency of the regime;
- retain the statutory coefficient values exactly as written; and
- do not claim that the unit checker has proved the dimensional semantics of
  coefficients represented as bare values.

Such formulas may require a local cast or body opt-out and appear as such in the
validation report. Statutory-currency evaluation preserves their numerical convention;
it is not a substitute for full coefficient-unit verification.

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

The rounding unit must equal the function unit after resolving `CURRENCY` to the
statutory currency. A function active across a statutory-currency change must be split
or receive date-appropriate rounding specifications. Presentation-currency conversion
occurs after rounding.

(gep-10-validation)=

(gep-10-checks)=

### Validation and limitations

#### Validation stages

| Stage                         | When                            | Input                                  | Validates                                                                            |
| ----------------------------- | ------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------ |
| declaration validation        | decoration or parameter loading | declarations                           | required fields, grammar, suffixes, and allowed currency bases                       |
| environment validation        | policy-environment assembly     | graph declarations and generated rules | required units, aggregation derivations, statutory currency, and regime completeness |
| function-body linting         | policy-environment assembly     | unit-carrying placeholders             | supported operations and explored returns                                            |
| annotated-input boundary      | input canonicalisation          | user tags and column names             | known tokens, exact suffix period, and source-currency conversion                    |
| numerical boundary conversion | before and after computation    | values and conversion factor           | input to statutory currency; computed results to data currency                       |

Pint quantities are used while declarations and policy environments are checked, while
annotated input is processed, and while numerical conversion factors are derived. Pint
quantities do not enter the compiled tax-and-transfer function or a JAX trace.

(gep-10-body-checker)=

#### Function-body linting

TTSIM evaluates a policy-function body with placeholders carrying the declared units of
its arguments. Conditional branches are explored by re-evaluating the body with
different branch decisions. Each explored return path is checked separately.

The body checker is a linter over a documented operation set. It is conforming only when
every supported stand-in inspects every operand that can affect the result's unit.
Scalar and vectorized spellings of the same operation MUST use equivalent rules.

Body linting rejects, among other things:

- addition, subtraction, or ordering of unit-incompatible quantities;
- a non-zero bare literal used as a dimensioned value;
- a return unit that differs from the declaration in physical dimension, period, or
  grouping level;
- a value with physical or period content used in a truth context;
- an `xnp.where` condition with physical or period content;
- unsupported in-body reductions;
- a supported join with a physically dimensioned key or incompatible fallback;
- an untyped numerical value accessed from a structured parameter;
- inconsistent schedule input and output axes; and
- any operation for which no faithful unit stand-in exists, unless the function
  explicitly opts out.

The checker MUST NOT silently preserve the input unit when an operation changes a
unit-relevant axis or grouping interpretation. A stand-in that discards `axis`,
`condition`, `foreign_key`, `primary_key`, `fallback`, or another unit-relevant argument
is nonconforming.

Branch exploration is bounded. Environment assembly fails when a body exceeds the
implementation's documented path or decision limit; the author must simplify it or use a
reported opt-out.

(gep-10-date-partition)=

(gep-10-policy-dates)=

#### Exhaustive policy-date regimes

A policy package is not validated exhaustively by testing function start dates alone.
TTSIM constructs a half-open date partition from every boundary that can change the
resolved unit environment.

The partition MUST include:

- every function start date;
- the day after every inclusive function end date;
- every dated parameter entry, including entries that change only a value, unit, leaf
  set, or currency;
- every statutory-currency transition; and
- every separately dated rounding-rule boundary not already represented by a function
  boundary.

Boundaries are clipped to the policy package's supported date domain. At least one
representative date, normally the left endpoint, is assembled and checked for every
resulting interval.

`ttsim.testing_utils.get_policy_date_partition` provides the reusable implementation for
TTSIM policy packages. A parameter-only or currency-only change must open a regime even
if the active function set is unchanged.

(gep-10-evidence)=

(gep-10-coverage)=

#### Validation reporting

Every environment check MUST expose a summary that distinguishes declaration coverage
from body coverage. The exact class and field names are implementation details, but the
report contains at least:

```text
resolved declarations
checked function bodies
generated nodes checked by rule
local casts used
function bodies opted out with verify_units=False
bodies rejected as unsupported
policy-date regimes checked
```

Counts alone are insufficient for exceptions. The report also lists the function or node
names using `cast_ttsim_unit` or `verify_units=False`.

A project may say that all required declarations are present while still containing
unchecked bodies. It may say that all non-exempt supported bodies passed the unit
linter. It MUST NOT describe an opted-out body as verified, and it MUST NOT use “100%
annotated” as a synonym for “100% body checked.”

A suitable CI summary is, for example:

```text
Declarations resolved: 412 / 412
Bodies checked:         371
Generated rules:         28
Casts:                     9
Body opt-outs:             4
Unsupported bodies:        0
Date regimes:             37
```

(gep-10-failures)=

#### Failure diagnostics

A dimensional failure SHOULD identify the policy node, policy date or regime, source
expression, expected unit, inferred unit, and the operation that failed. A branch or
`xnp.where` failure SHOULD identify the condition or incompatible arm. A join failure
SHOULD identify whether a key or fallback caused it. An unsupported reduction SHOULD
name the reduction and explain that row or axis metadata is unavailable.

Diagnostics must not recommend a generic cast as the default repair. They may state that
a local cast or body opt-out is available, while making clear that either is an
assertion or loss of body coverage.

(gep-10-limitations)=

#### Trade-offs and limitations

**Dimensionless semantics are mostly unchecked.** `DIMENSIONLESS` covers shares, IDs,
categories, bare rates, and ordinary scalars. The unit system cannot generally reject
arithmetic between them. Truth compatibility excludes dimensioned values but does not by
itself prove that a dimensionless selector is a Boolean.

**Equality is unchecked.** Equality operators do not compare units. This permits
sentinel comparisons such as `p_id_empfänger == -1`, but also means equality between
monthly and yearly income is not detected.

**Grouping markers are not relational grain.** They do not prove row alignment,
uniqueness, cardinality, broadcast provenance, or the nominal domain of an ID. A bare
household-specific share remains bare because this GEP does not model where it is
stored.

**The group algebra is intentionally partial.** Only documented head-count conversions,
scalar modification, logical rules, and generated aggregations are checked. Other
products or ratios involving group-marked quantities require an explicit assertion or
opt-out.

**Body exploration is bounded.** Code outside the explored paths or beyond the path
limit is not silently certified.

**Some operations are unsupported.** In-body array reductions are rejected. Joins
receive only the dimensional checks documented above. Nominal domains and cardinality
are not proved.

**Annotated-input validation is partial.** It checks known tokens, exact suffix periods,
and currency conversion. It does not compare every tag's physical dimension or grouping
level with the target node declaration.

**Automatic period ratios are conventions.** Their dimensional validity does not prove a
statute-specific day-count, partial-period, or compounding rule. See
[GETTSIM #1205](https://github.com/ttsim-dev/gettsim/issues/1205).

**Currency provenance is regime-level.** The model assumes one statutory currency per
policy regime and does not support simultaneous monetary values that retain distinct
historical legal denominations inside one body.

**A cast is an assertion.** An incorrect cast can hide an error. Casts are reported and
must remain local.

(gep-10-exceptions)=

(gep-10-opt-out)=

#### Explicit exceptions

`cast_ttsim_unit(value, unit=unit)` replaces the inferred unit of one expression during
body linting. At numerical execution, it returns `value` unchanged.

It is appropriate for:

- a policy-defined transfer between grouping concepts that the generic group algebra
  cannot derive;
- a dimensioned implementation constant that is not a statutory parameter; or
- a narrow formula seam involving a known coefficient or operation outside the current
  vocabulary.

It should apply to the smallest expression requiring the assertion. Every cast is listed
in the validation report.

`verify_units=False` disables body linting for one decorated function or hand-written
aggregation. Its declared output unit remains the contract used by consumers. It is
appropriate only when the body:

- uses an unsupported operation;
- exceeds the branch-exploration limit; or
- implements a policy interpretation that cannot be represented by the documented unit
  rules.

Every opt-out is listed separately and does not increase checked-body coverage. A policy
package with opt-outs may be declaration-complete and may pass environment assembly; it
must not claim that every body was unit checked.

(gep-10-conformance)=

## Conformance and acceptance requirements

An implementation conforms to this GEP only if it satisfies all of the following:

1. every required object has a valid declaration under the compositional vocabulary;
1. group-level dimensionless declarations are restricted to known counts and indicators;
1. the restricted group algebra rejects unsupported products, ratios, and cross-level
   operations;
1. `MEAN`, `MIN`, and `MAX` derive the target group level;
1. scalar truth contexts and `xnp.where` reject values with physical or period content;
1. supported joins inspect keys and fallbacks, while unsupported join semantics are
   documented rather than implied;
1. raw in-body reductions fail when their result level cannot be derived;
1. the policy-date partition includes function, parameter, rounding, and statutory-
   currency boundaries as applicable;
1. one statutory currency is enforced throughout each policy regime; and
1. validation output distinguishes declarations, checked bodies, generated rules, casts,
   and whole-body opt-outs.

Green project tests without these cases are not sufficient evidence of conformance. The
implementation test suite SHOULD include adversarial mutations for each rule, including
stock-versus-flow returns, dimensioned truth conditions, vectorized conditions, wrong
join fallbacks, group-level shares, group means, parameter-only dates, and currency-only
dates.

## Related work

- {ref}`GEP 1 <gep-1>` defines the time and grouping suffixes validated here.
- {ref}`GEP 2 <gep-2>` defines `*_id` columns and group creation.
- {ref}`GEP 4 <gep-4>` defines the DAG, aggregations, and generated reference-period
  conversions.
- {ref}`GEP 5 <gep-5>` defines rounding specifications.
- {ref}`GEP 9 <gep-9>` defines runtime type validation and the user/canonical data
  split.
- [Pint](https://pint.readthedocs.io) supplies the physical-unit registry and algebra.
- [GETTSIM #1205](https://github.com/ttsim-dev/gettsim/issues/1205) tracks legally
  sensitive reference-period conventions.
- [GETTSIM #1219](https://github.com/ttsim-dev/gettsim/issues/1219) records the review
  that led to the narrowed guarantee and additional guards in this revision.

## Implementation

The implementation is divided between TTSIM infrastructure and policy-system
annotations.

- TTSIM [#138](https://github.com/ttsim-dev/ttsim/pull/138) contains the unit registry,
  compositional vocabulary, declarations, generated aggregation rules, body linter, and
  input-boundary machinery.
- TTSIM [#141](https://github.com/ttsim-dev/ttsim/pull/141) annotates the bundled
  fictional METTSIM policy system.
- TTSIM [#150](https://github.com/ttsim-dev/ttsim/pull/150) tightens truth contexts,
  `xnp.where`, join operands, unsupported reductions, the stock/flow reproducer, and the
  policy-date partition.
- GETTSIM [#1193](https://github.com/ttsim-dev/gettsim/pull/1193) contains GEP 10.
- GETTSIM [#1212](https://github.com/ttsim-dev/gettsim/pull/1212) contains the GETTSIM
  rollout.

Before this GEP is described as implemented, the code and test suite must additionally
cover the normative changes introduced by this revision:

- prohibit group-level dimensionless shares and rates while retaining documented group
  counts and indicators;
- restrict generic products and ratios of group-marked quantities;
- derive `MEAN` at the target group rather than automatically making it bare;
- report casts and whole-body opt-outs separately from checked bodies; and
- align public calendar wording with the ordinal semantics specified here.

(gep-10-alternatives)=

## Alternatives

### A general multi-axis value-type system

Deferred. A broader design could represent physical unit, semantic kind, row index,
nominal key domain, extensity, tensor axes, calendar semantics, currency provenance, and
nullability as independent type axes. Such a system could validate joins, row alignment,
group-specific shares, inverse-unit coefficients, and more of the Python expression
language.

That design is substantially larger than the dimensional guards needed for the current
GETTSIM and METTSIM rollout. This GEP instead states the limits of the Pint-centered
model and fails closed where a supported operation would otherwise be falsely certified.
A later GEP may add relational or semantic typing without changing the physical-unit
rules here.

### A dedicated public `SHARE` or identifier unit

Deferred. Pint would still treat a share as physically dimensionless, so meaningful
semantic restrictions would require a separate rule system. The present GEP prefers
fewer public unit kinds and explicitly documents the dimensionless blind spot. It adds
only the truth and group-declaration guards needed for the claims made here.

### A complete relational grain model

Deferred. Grouping levels in this GEP are restricted arithmetic markers, not row-domain
types. Nominal ID domains, uniqueness, join cardinality, broadcast provenance, and
alignment remain outside scope. Unsupported reductions fail rather than pretending that
their row grain is unchanged.

### A person level, implied or spelled

Rejected for this proposal. Earlier variants represented every person amount as
`... / [person]` and head counts as `[person] / [group]`. This distinguished a bare rate
or share from a per-person amount, but introduced an implied level on almost every value
and two spellings for the same practical person quantity.

The adopted model keeps person quantities bare and uses group head counts as
`1 / [group]`. The consequence is explicit: after total/head-count division, the unit
checker knows that the result is bare but does not maintain a separate person-grain
type.

### Convert every parameter to a selected run currency

Rejected. Some statutory formulas contain coefficients whose numerical values depend on
the currency convention. Converting only the obvious monetary quantities could change
the formula. The adopted design evaluates each regime entirely in its statutory
currency, retains parameter and coefficient values as written, and converts only input
and computed output at the boundary.

### Pass Pint quantities through the DAG

Rejected. `pint.Quantity` is not part of the intended NumPy/JAX numerical
representation. Units are static properties checked during environment assembly and at
interface boundaries. The compiled tax-and-transfer function continues to receive
ordinary numeric values.

### Remove concrete currency labels from parameters

Rejected. The one-currency-per-regime invariant would make these labels theoretically
redundant, but they are useful validation checks and documentation. A parameter declared
in Euro during a Deutsche-Mark regime should fail loudly.

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
