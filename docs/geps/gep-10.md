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

This GEP gives every quantity in GETTSIM a **unit** — Euros, Euros per square meter,
etc. — declared on parameters, policy functions, and (optionally) input data. The
framework reads those units to do two things:

- **Dimensional safety.** It checks that the arithmetic combining quantities is sound,
  so mixing incompatible kinds — say, a monthly amount and a per-square-meter rent —
  becomes a loud error when the model is defined, not a silent wrong number far
  downstream.
- **Automatic unit conversion.** It converts compatible quantities to a common unit. For
  example, parameters denominated in Deutsche Mark can be converted to Euros at build
  time, so a parameter's history can include values in both currencies and the user can
  run in either one without hand-converting the numbers. Time conversions of flows work
  the same way. The existing `_y`/`_q`/`_m`/`_w`/`_d` suffix convention is preserved.

The engine is [pint](https://pint.readthedocs.io), and it runs **only while the model is
built**: it checks dimensions and converts units, then steps aside. The numeric runtime
is unchanged. As in {ref}`GEP 9 <gep-9>`, the checks fire at definition time, catching a
whole class of unit bugs before they can reach a result.

### Terminology

- **dimension** — the basic kind of a quantity: `[currency]`, `[time]`, `[area]`, or
  dimensionless. Counting quantities (children, adults, household members) are
  dimensionless, following the SI and pint convention.
- **unit** — a particular way of measuring a dimension, such as Euros for `[currency]`
  or years for `[time]`. A unit carries a conversion factor to the dimension's base
  unit, so e.g. `1 month = 1/12 year`.

## Motivation and Scope

Three long-standing problems motivate this GEP.

1. **No dimensional safety.** The DAG carries quantities of many kinds, but a function
   body may add, subtract, or compare them freely. `betrag_m + miete_pro_qm_m` (a
   monthly amount plus a monthly rent *per square meter*) is a bug that runs silently
   today and surfaces, if at all, as an implausible number far downstream.

1. **Hand-converted historical currency.** Every Deutsche-Mark-era parameter is divided
   by `1.95583` by a maintainer before being written to YAML, with the original value
   preserved only in a free-text `note`. There is no machine-checkable provenance and no
   guard against a transcription error. This is both prone to errors and violates
   GETTSIM's law-to-code approach.

1. **Hand-written time arithmetic.** `ttsim/unit_converters.py` implements ~50
   conversion functions (`y_to_m`, `per_y_to_per_m`, …) and their stock/flow duals by
   hand. The resulting arithmetic has itself been a source of bugs.

**Scope.** The GEP covers `ttsim` (the framework) and `gettsim` (the German currencies
and the policy annotations). GEP 1's `_y`/`_q`/`_m`/`_w`/`_d` suffix automation is
preserved; only the *arithmetic* behind the conversions moves onto the unit engine.

## The available units

Every quantity in GETTSIM is declared as one of a small, fixed set of **unit tokens**. A
special, but common, special case is the currency dimension. GETTSIM supports two
currencies: Euros (EUR) and Deutsche Mark (DM). However, policy functions are written to
be currency-agnostic, i.e. they can run in either currency without change. Only
parameters and input data carry a concrete currency declaration.

Policy functions and columns declare their unit as one of the **agnostic tokens**:

- **`CURRENCY`** is a *stock* — an amount of money at a point in time, such as wealth or
  an asset threshold.
- **`CURRENCY_FLOW`** is a *flow* — an amount of money per unit of time, such as a
  monthly Regelsatz or an annual income. The period (per month, per year, …) is read off
  the {ref}`GEP 1 <gep-1>` name suffix (`_m`, `_y`, …), so a `betrag_m` declared
  `CURRENCY_FLOW` resolves to `CURRENCY / month`.

Parameters, which record a legal amount in a specific historical currency, instead use
the *concrete* currency tokens `EUR` / `EUR_FLOW` and `DM` / `DM_FLOW`.

The remaining tokens cover the other dimensions GETTSIM needs:

| token                                               | measures                                                     |
| --------------------------------------------------- | ------------------------------------------------------------ |
| `DIMENSIONLESS`                                     | shares, rates, counts (children, household size)             |
| `DIMENSIONLESS_FLOW`                                | a pure number per period (e.g. change of Zugangsfaktor p.a.) |
| `YEARS` / `MONTHS` / `DAYS`                         | *durations*: an age, a number of years/months/days           |
| `CALENDAR_YEAR` / `CALENDAR_MONTH` / `CALENDAR_DAY` | *calendar points*: a birth year, the policy date             |
| `HOURS_FLOW`                                        | working hours per period                                     |
| `SQUARE_METERS`                                     | dwelling size                                                |
| `CURRENCY_PER_SQUARE_METER_FLOW`                    | rent caps                                                    |

A *calendar point* (a year/month/day **on** the calendar) is distinct from a *duration*
(a number of years/months/days): the difference of two calendar points is a duration
(`policy_year - geburtsjahr` is an age in `YEARS`), but two calendar points cannot be
added. The {ref}`vocabulary <gep-10-vocabulary>` below spells out the algebra.

The same `…_FLOW` rule applies throughout: a token ending in `…_FLOW` needs a period —
from a name suffix for single values, from `reference_period` for tables — while every
other token is complete on its own. The full vocabulary, the rules for where the period
comes from, and the currency model are spelled out in the
{ref}`token vocabulary <gep-10-vocabulary>` below.

## Usage and Impact

Every parameter and policy function carries a `unit=` declaration. The unit declaration
on policy functions is a guard rail: GETTSIM checks that the unit that falls out of the
function body matches the declaration, so a mismatch is a loud error at definition time,
but the declaration itself is not a source of truth for the unit.

```python
@policy_function(unit=Unit.CURRENCY_FLOW)  # name betrag_m -> resolved CURRENCY/month
def betrag_m(regelsatz_m: float, anzahl: int) -> float:
    return regelsatz_m * anzahl


@policy_function(unit=Unit.CURRENCY)  # a stock; a time suffix would be an error
def vermögen(aktien: float, immobilien: float) -> float:
    return aktien + immobilien
```

One optional `currency` argument to `main()` picks the currency the model runs in —
defaulting to the registered base currency (`"EUR"` for GETTSIM) — and every
currency-denominated parameter is converted to it at build time.

Tagging input data with units is **optional**, through a dedicated unit-annotated input
tree; results can likewise be returned as a unit-annotated tree. This provides
additional boundary checks on the user's input data and clarifies the units of the
outputs.

## Backward Compatibility

- **User code shape is unchanged.** Bare arrays and the DataFrame/mapper interface keep
  working; `currency` defaults to `"EUR"` and output stays in Euros.
- **The `unit`/`reference_period` metadata is repurposed.** `unit` becomes one member of
  the token vocabulary and `reference_period` becomes *functional* (it supplies the
  period for structured `…_FLOW` parameters — dicts, schedules, lookup tables — which do
  not auto-convert) rather than purely descriptive.
- **No blanket opt-out.** Unlike the {ref}`GEP 9 <gep-9>` beartype claw, there is no
  env-var escape hatch that switches the unit check off wholesale. Users can opt-out of
  unit checking for specific functions (`verify_units=False`,
  {ref}`see below <gep-10-checks>`) or by turning off GETTSIM's fail-if nodes.

## Detailed Description

(gep-10-vocabulary)=

### The unit vocabulary

A declaration is one member of the **token vocabulary**. Its backbone is a closed core
enumeration — a `Unit` `StrEnum` shipped by `ttsim`, spelled identically in code (e.g.
`unit=Unit.HOURS_FLOW`) and in YAML (e.g. `unit: HOURS_FLOW`):

| token                                               | resolves to                           | typical use                   |
| --------------------------------------------------- | ------------------------------------- | ----------------------------- |
| `CURRENCY_FLOW`                                     | `CURRENCY / period`                   | wages, claims, benefits       |
| `CURRENCY`                                          | `CURRENCY`                            | wealth, asset thresholds      |
| `DIMENSIONLESS`                                     | `dimensionless`                       | shares, rates, counts         |
| `DIMENSIONLESS_FLOW`                                | `1 / period`                          | Zugangsfaktor per year        |
| `YEARS` / `MONTHS` / `DAYS`                         | a duration in `year`/`month`/`day`    | an age, a span                |
| `CALENDAR_YEAR` / `CALENDAR_MONTH` / `CALENDAR_DAY` | a calendar point in years/months/days | a birth year, the policy date |
| `HOURS_FLOW`                                        | `hour / period` (dimensionless)       | working hours                 |
| `SQUARE_METERS`                                     | `meter ** 2`                          | dwelling size                 |
| `CURRENCY_PER_SQUARE_METER_FLOW`                    | `CURRENCY / meter ** 2 / period`      | rent caps                     |

A token ending in `…_FLOW` needs a period; every other token is complete as written and
takes no period. Tokens are not pint syntax: each resolves internally to a pint unit
(flow tokens after the period is filled in), but pint expressions never appear in a
declaration.

`HOURS_FLOW` is the one flow token that resolves to a *dimensionless* quantity: hours
and the period are both `[time]`, so hours per week is a time-over-time ratio. It is
kept as a distinct token so the time-suffix and time-conversion bookkeeping still apply
to working hours, but dimensionally it cannot be told apart from a bare `DIMENSIONLESS`
quantity. Likewise, a *per-period* dimensionless quantity is `DIMENSIONLESS_FLOW`, not
`DIMENSIONLESS`: the pension Zugangsfaktor moves by a fixed factor per year of earlier
or later retirement (`zugangsfaktor_veränderung_y`, § 77 SGB VI) — a pure number, but
*per year* it is `1/year`, and multiplied by the gap in `YEARS` the years cancel to the
dimensionless adjustment.

**Calendar points are distinct from durations.** A year *on the calendar* — a birth
year, the policy year — is an affine *point*, not a *duration*. The two do not share
arithmetic: subtracting two points gives a duration, and shifting a point by a duration
gives a point, but two points cannot be added and a point cannot be scaled. The
`CALENDAR_YEAR` / `CALENDAR_MONTH` / `CALENDAR_DAY` tokens carry the point on each axis;
`YEARS` / `MONTHS` / `DAYS` carry the corresponding duration. The dry-run enforces the
algebra (the duration `D` of a point `P`):

| operation                 | result    | example                              |
| ------------------------- | --------- | ------------------------------------ |
| `P − P`                   | duration  | `policy_year − geburtsjahr` → an age |
| `P ± D` (same axis)       | point     | `geburtsjahr + statutory_age`        |
| `P + P`, `P × n`, `P / n` | **error** | two calendar years cannot be added   |
| mixing calendar axes      | **error** | a year point plus a month duration   |

This is the one case where a quantity's token decides whether an operation is *allowed*,
not just whether two units match: the affine point and its duration have the same
dimension but obey different algebra. A *cyclic* ordinal — a month-of-year
(`geburtsmonat` 1-12), a day-of-week, a quarter — is **not** a calendar point but
`DIMENSIONLESS`: it is a recurring label, not a position on a running calendar.
Migration is a no-op for existing `YEARS` declarations: an age, an age threshold, a
contribution count stay `YEARS` and behave exactly as before (a duration is fully
multiplicative); only quantities that are genuinely points on the calendar move to a
`CALENDAR_*` token.

**Counting quantities, booleans, and identifiers are dimensionless** (`DIMENSIONLESS`),
following SI and pint convention. A per-person parameter declares the same token as any
other amount (`EUR_FLOW` for a monthly Regelsatz); scaling it by a head count is a plain
multiplication that preserves the unit. A boolean is a `{0, 1}` value, and an identifier
(`p_id`, `*_id`, `p_id_*`) carries no dimension — both spell that out rather than being
silently waved through.

```yaml
beitragssatz:
  unit: DIMENSIONLESS   # a rate is dimensionless
  reference_period: null
  type: scalar
  2024-01-01:
    value: 0.013
```

**There are no exemptions** — every active node has a unit. Most nodes declare it
directly. Derived nodes get one auto-assigned ({ref}`see below <gep-10-auto>`); the
framework-injected date nodes get theirs from the framework (`policy_year` is a
`CALENDAR_YEAR`, etc.). So `UNSET_UNIT` has a single meaning — *no declaration was made*
— which the mandatory-units check always reports as an error, with no second
"legitimately blank" reading to disambiguate.

Beyond the core enumeration, the full vocabulary adds one set of **concrete currency
tokens** per registered currency ({ref}`see Currency <gep-10-currency>`); the
currency-dimensioned rows of the table above are the *agnostic* tokens. The core
enumeration lives in `ttsim` and is shared by all downstream packages.

### pint runs at build time only

The foundational constraint is that pint never wraps a live array. A `pint.Quantity` is
not a JAX pytree and does not trace under `jit`; wrapping runtime columns would fight
both JAX and the GEP-9 `FloatColumn` vocabulary. Instead, pint is used in two build-time
roles:

- to compute conversion **factors** (time and currency), which are baked into the
  compiled workers as plain numeric constants; and
- to run the **dry-run** dimensionality check on representative `Quantity`s.

The numeric runtime path stays pure arrays, single currency, and JAX-safe. Time is a
first-class pint dimension here: the conversion factors are sourced from pint
(`Quantity(1, "year").to("month")`), while the suffix auto-generation and naming follow
the {ref}`GEP 1 <gep-1>` conventions.

(gep-10-periods)=

### Flow tokens

Flow units need a reference period source. For many functions and parameters, the period
comes from the name suffix (`_y`, `_m`, …) as laid out in {ref}`GEP 1 <gep-1>`. Only
parameters that cannot auto-convert because they are structured values (dicts,
schedules, lookup tables) need to declare a `reference_period` to supply the period that
a consumer would read off a suffix if it were there..

| what you declare                                         | period from                  | auto-converts |
| -------------------------------------------------------- | ---------------------------- | ------------- |
| single value — column, policy function, scalar parameter | name suffix `_y/_q/_m/_w/_d` | yes           |
| structured value — dict, schedule, lookup table          | `reference_period`           | no            |

Where the suffix supplies the period it is also *mandatory and exclusive*: a time suffix
requires a `…_FLOW` token and a `…_FLOW` token requires a time suffix, so a non-flow
token on a suffixed name — or a flow token on an unsuffixed one — fails at build. This
makes the {ref}`GEP 1 <gep-1>` convention machine-checked: a node named `…_m` whose body
computes a stock cannot be declared.

The two period sources are mutually exclusive: `reference_period` exists only for the
structured values that have no suffix to read, so declaring it on a single value — a
column, a policy function, or a **scalar parameter** — is an error. A scalar parameter's
period therefore comes *only* from its name suffix, and the JSON schema rejects a
`reference_period` on `type: scalar`.

### Dict parameters with heterogeneous leaves

A dict parameter whose leaves carry different units declares `unit:` as a **mapping from
leaf keys to tokens** (or `DIMENSIONLESS` for a dimensionless leaf). A flow leaf with a
string key takes its period from the key's own time suffix; an integer-keyed flow leaf,
which has no suffix to carry, takes it from the dict-level `reference_period`:

```yaml
schedule:
  unit:
    child_amount_y: EUR_FLOW   # string key -> period from its own _y
    max_age: YEARS
  type: dict
  2024-01-01:
    child_amount_y: 3000.0
    max_age: 18
```

```yaml
satz_nach_kindanzahl:
  unit: EUR_FLOW            # uniform: one token for all leaves
  reference_period: Month   # integer keys carry no suffix -> dict-level period
  type: dict
  2024-01-01:
    1: 250.0
    2: 250.0
```

**Leaves that change name across the parameter's history.** The `unit:` mapping is a
**union over all dated entries**: the mandatory-units check looks only at the leaves
present in the value active at the policy date and ignores mapping entries for leaves
that exist only at other dates. So a leaf renamed across a reform is covered by listing
both names. A value leaf with no entry in the mapping is a *missing* declaration and is
flagged, so a mistyped key cannot pass silently.

### Mapping parameters: one token per axis

A schedule or lookup table is not a quantity — it is a *function between quantities*,
with a domain and a codomain. The mapping parameter types (the `piecewise_*` family, the
lookup tables, the phase-in/out types) therefore declare `input_unit:` and
`output_unit:` instead of `unit:`; a `unit:` on them is an error, and the JSON schema
enforces the split per `type:`:

```yaml
tarif:
  input_unit: EUR_FLOW    # taxable income per year in ...
  output_unit: EUR_FLOW   # ... tax per year out
  reference_period: Year
  type: piecewise_quadratic
  ...
```

(gep-10-currency)=

### Currency

Currencies live in the framework as a `[currency]` dimension, with concrete currencies
registered by downstream packages via
`register_currency(name, *, base=False, definition=None)`. GETTSIM registers `EUR`
(base) and `DM = EUR / 1.95583`. Registration does two things: it provides the
**conversion factors**, with pint as the single source of truth for the rate; and it
derives the currency's **declaration tokens** — one concrete variant per
currency-dimensioned core token (`DM`, `DM_FLOW`, `DM_PER_SQUARE_METER_FLOW`, `EUR_*`,
…) — spelled by replacing the agnostic `CURRENCY` prefix with the upper-cased currency
name.

**Agnostic and concrete tokens.** A **currency-agnostic token** (`CURRENCY`,
`CURRENCY_FLOW`, …) is a placeholder for any registered currency: it declares the unit
of a function or column for which it does not matter which currency the model runs in. A
**concrete currency token** (`DM_FLOW`, `EUR`) names one specific currency; what it adds
over its agnostic counterpart is **denomination** — it names the currency a parameter's
stored numbers are written in, which the build-time conversion reads off the
declaration.

**Parameters must be concrete; functions must be agnostic.** A parameter's numbers are
written in *some* currency, so once a concrete currency is registered, an agnostic
`CURRENCY_*` token on a parameter is a build error — the declaration must name the
denomination (`EUR_FLOW`, not `CURRENCY_FLOW`). Columns and functions may *only* declare
agnostic tokens.

**The run currency.** The `currency` argument to `main()` defaults to the registered
base currency; it is the currency the input data is taken to be in and that the outputs
come out in. At environment build, every currency-denominated *parameter* is converted
from its declared denomination to the run currency.

**A changeover within one parameter's history.** A dated entry may restate the unit
field(s), overriding the top-level declaration for that entry's numbers. This is how the
DM→Euro switch is written — entries before the reform denominated in the legacy
currency, entries from the reform date in the new one:

```yaml
arbeitnehmerpauschbetrag_y:
  unit: DM_FLOW
  type: scalar
  1990-01-01:
    value: 2000
  2002-01-01:
    unit: EUR_FLOW   # the changeover: denominated in Euro from here on
    value: 1044
```

`updates_previous` cannot cross a changeover: an entry that restates the unit
declaration must restate the full value, because a merged value would mix numbers
denominated in different currencies.

**Converters (`require_converter`).** A `require_converter` hands an arbitrary nested
structure to a `@param_function` that knows how to read it. The framework cannot, so for
currency conversion the parameter declares one of two *honest* shapes:

- **Homogeneous** — a single `unit:`, when every numeric leaf is the same currency. The
  structure is scaled uniformly, leaf by leaf, before the converter runs.
- **Function-like** — `input_unit:` / `output_unit:` axes, when the converter produces a
  schedule or lookup table (a function between quantities, like a mapping parameter).
  The raw structure is then left untouched and the converter's *typed output* is
  converted per axis, so an order-`j` polynomial coefficient scales by `f_out / f_in**j`
  (the slope invariant, the quadratic by `1 / f_in`) rather than by one uniform factor.

A structure that **mixes** a currency with non-currency numbers — a `satz` bundled with
the age bracket it applies to, an amount next to a dimensionless share — is neither
shape: a single blob offers no surface on which to declare a unit per leaf, and uniform
scaling would corrupt the non-currency numbers. Such a parameter is **split** into
separate homogeneous parameters (the amount as a currency parameter, the ages as a
`YEARS` parameter), each independently declarable and checkable. Accordingly, a
homogeneous (single-`unit:`) converter that is found to produce a function-like value is
rejected at build time — uniform scaling cannot state its coefficients correctly — with
the error pointing the author at the per-axis declaration.

(gep-10-checks)=

### Build-time checks and boundary conversion

The checks run in two layers, both at build time:

|        | **Layer 1 — DAG validity**                                        | **Layer 2 — boundary**                                                                                                                             |
| ------ | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| when   | `fail_if` on the assembled environment                            | GEP-9 canonicalisation boundary                                                                                                                    |
| input  | none — synthetic `Quantity`s                                      | the user's unit-annotated input tree                                                                                                               |
| checks | inferred body unit vs. declaration; producer↔consumer edges agree | tag currency → run currency; period vs. suffix; unknown token rejected; every tag equivalent to its resolved unit (currency and flow period aside) |

#### Layer 1: the **dry-run** dimensionality check.

**Layer 1** runs each scalar body in NumPy+pint, infers the unit that falls out, and
checks it against the declaration; an edge-consistency pass then confirms each
producer's unit equals its consumer's declared expectation.

**How the dry-run checks one body.** The check *runs the function body*, but with
**units in place of numbers**. Each input becomes a stand-in carrying its resolved unit
and a throwaway magnitude of `1`; pint carries the units through the body's arithmetic,
and the unit that falls out of the `return` is compared to the declaration:

```python
@policy_function(unit=Unit.CURRENCY_FLOW)  # -> CURRENCY / month
def betrag_m(
    einkommen_m: float, satz: float, mindestbetrag_m: float, befreit: bool
) -> float:
    if befreit:
        return 0.0
    if einkommen_m > mindestbetrag_m:
        return einkommen_m * satz
    return mindestbetrag_m
```

Here `einkommen_m` and `mindestbetrag_m` enter as `EUR/month`, `satz` as a dimensionless
`1`, and `befreit` as a boolean stand-in. `einkommen_m * satz` is a flow times a
dimensionless number, so it stays `EUR/month` — matching the declaration; the
`mindestbetrag_m` arm matches too.

**Every branch is covered, by re-running.** To evaluate `if befreit:` Python needs a
yes/no, but a unit stand-in has no value to compare. So the stand-in intercepts the
*truth test* itself (Python's `__bool__`) and hands it to a small driver — the **path
explorer** — that decides which way to go, re-running the body and steering the open
branches differently each time (a depth-first walk of the decision tree, in the style of
*concolic* execution) until every syntactically reachable branch combination is driven —
the explorer tracks no path constraints, so it counts branch combinations, not strictly
feasible paths. A body whose branching exceeds an internal cap is rejected (it must opt
out), never passed with some combinations left unchecked. Each run's result is checked
on its own, so a unit slip on a single arm — say, returning a yearly figure where `_m`
was declared — is caught even though the other arms are clean. A `return 0.0` arm yields
a dimensionless result and falls back to the declaration, so the ubiquitous
`if befreit: return 0.0` guard never raises a false alarm.

**What the dry-run catches:**

- a body whose inferred unit disagrees with its declaration, on any reachable branch — a
  stock times a per-year rate labelled as a stock, or a `_m` flow returned where `_y` is
  declared;
- an addition or subtraction of two non-equivalent quantities — a monthly flow plus a
  yearly one (`betrag_m + freibetrag_y`), or a stock plus a flow. At run time the
  assembled DAG computes on bare arrays with no pint, so such a combination is
  unit-blind and silently wrong; the dry-run rejects it rather than letting pint's
  build-time auto-conversion of same-dimension operands paper over it;
- an ordering comparison (`<`, `<=`, `>`, `>=`) of two non-equivalent quantities, or of
  a quantity against a bare non-zero literal — the literal silently carries the
  quantity's unit, so promote the bound to a parameter (only `0` is allowed inline).
  Equality (`==`, `!=`) is deliberately **not** screened: it is the operator for
  sentinel and exact-marker tests — a person-pointer's no-link marker
  (`p_id_empfänger == -1`) or an exact-zero guard (`kindersatz_m == 0.0`) — where the
  literal is a deliberate marker, not a hidden dimensioned bound to be promoted to a
  parameter. The trade-off is that an equality between two genuinely non-equivalent
  quantities is not caught, so `==`/`!=` are reserved for marker tests rather than for
  comparing computed amounts;
- a logical operator (`&`, `|`, `~`) applied to a unit-carrying operand —
  `wealth & is_adult`, where `wealth` is a stock. Logical operators combine truth
  values, so an operand carrying a real unit is a bug the run-time arrays would silently
  swallow;
- a missing unit, and malformed declarations: a flow token without a period, a
  currency-agnostic token on a parameter, disagreeing period sources, or a boolean node
  carrying a concrete unit.

**What it cannot catch:**

- **anything that reduces to dimensionless.** The check is *dimensional*, not
  *semantic*: quantities that collapse to the dimensionless dimension are
  indistinguishable to it. A per-period count is `[time]/[time] = 1`, so `HOURS_FLOW`
  (working hours per period) reads as a plain number — adding working hours to a share
  or a head count is *not* caught. The same blind spot covers a body whose result
  *infers* dimensionless (an early `return 0.0`, or arithmetic that cancels): it falls
  back to the declaration rather than contradicting it. So the engine guarantees
  *dimensional* soundness, not that every quantity is the intended *kind*;

**A body the dry-run cannot evaluate must opt out explicitly.** The dry-run executes a
*scalar* body symbolically, so a body it cannot trace must opt out: vectorized functions
(`vectorization_strategy="not_required"`, no scalar form for pint to walk), piecewise
polynomials and lookup tables (evaluated by table machinery), bodies calling `join` or a
raw `xnp` op, and bodies returning an opaque value (a dataclass, a tuple) the dry-run
cannot unit-check. Rather than silently trusting such a body, the check **rejects** it
unless the author marks it `verify_units=False` on the decorator. The opt-out is of body
*inference only*: the declared output unit still stands, so every *consumer* of this
node is still checked against it. The units flowing *into* the body are sound as well —
each is the declared, separately verified output of its producer. What the opt-out drops
is any check *internal* to the body: for a schedule, the binding of its declared domain
(`input_unit`) to the argument it is evaluated at is not verified, because the body is
never dry-run.

**Known limitation.** An opted-out schedule (e.g. a `piecewise_polynomial`) could in
principle be evaluated at an argument whose unit differs from its declared `input_unit`
without the dry-run catching it. The residual risk is small: schedule evaluation goes
through a single standardized primitive, and the argument it receives is itself a
verified producer output, so a mismatch would have to originate inside that standardized
machinery. It could escape unit-checking end to end only if two opt-out bodies fed one
another directly — which does not occur in the current system.

#### Layer 2: the **boundary check** on the unit-annotated input tree.

**Layer 2** is offered through the unit-annotated input tree (a sibling of the ordinary
input tree in which every leaf is a pint `Quantity`). When the mode is used **every**
leaf must be tagged, including identifiers and other dimensionless columns (tagged
`dimensionless`). The boundary check requires each tagged input to be *equivalent* to
its resolved environment unit once the two axes handled elsewhere — currency (converted
by the strip path) and a flow's reference period (owned by the suffix guard) — are
divided out, so a same-dimension level error such as a `HECTARES` column tagged `m²`, or
a `YEARS` input tagged in months, is rejected rather than silently mis-scaled. It feeds
no node, so it adds no back-edge to the boundary and needs no declared unit threaded
through `processed_data`. Symmetrically, the **unit-annotated result tree** relabels
each output leaf with its precise run-currency unit (`euro/month`, not the agnostic
`CURRENCY_FLOW`) — pure naming, since results are already computed in the run currency.

(gep-10-auto)=

### Auto-generated nodes

Auto-generated nodes receive auto-assigned units: time-conversion variants inherit the
source's base token and read the variant's period off its own suffix; auto-aggregations
derive their token from the source and the aggregation type, paralleling how
{ref}`GEP 4 <gep-4>` resolves their types. `SUM`/`MEAN`/`MIN`/`MAX` preserve the source
token; `COUNT` is a head count and is `DIMENSIONLESS`; `ANY`/`ALL` yield a boolean (a
dimensionless quantity) and so auto-assign `DIMENSIONLESS` (as does a `SUM` over a
boolean column — a head count). A `@group_creation_function` group id is auto-assigned
`DIMENSIONLESS` (it is an identifier, and the decorator exposes no `unit=`). Where the
source's token pins down a concrete currency (a parameter), the derived node inherits
the **agnostic counterpart**.

### Literals

The dry-run executes a body on representative `Quantity`s, so a bare numeric literal
combined *additively* with a unit-carrying value raises (pint refuses to add a
dimensionless number to a currency). A literal that is only a multiplicative factor
(`betrag * 0.5`) is fine — multiplying by a dimensionless number preserves the unit.

Most apparent cases dissolve once the quantities are declared correctly: an ordinal such
as `geburtsmonat` (the month 1–12) is `DIMENSIONLESS`, so `geburtsmonat - 1` is
dimensionless arithmetic and needs no tag. For a genuine constant of a real dimension,
either **promote it to a parameter** (the norm — it then gets the same provenance,
currency conversion, and checking as any other parameter, and the body becomes
dry-runnable), or **opt the body out** with `@policy_function(verify_units=False)` for
genuine code-level constants where a parameter would be artificial (the same body-level
opt-out as above).

## Related Work

- {ref}`GEP 9 <gep-9>`: runtime type checking via beartype; this GEP follows its
  build-boundary philosophy and its "loud at the boundary you wrote" goal.
- {ref}`GEP 1 <gep-1>`: the time/aggregation suffix conventions this GEP preserves.
- [pint](https://pint.readthedocs.io): the unit registry, dimensionality analysis, and
  NumPy (NEP-18) support relied on here.

## Implementation

Delivered as several PRs, with the framework proven on `mettsim` before any German
annotation. The tracking issues are:

- ttsim [#117](https://github.com/ttsim-dev/ttsim/issues/117) — framework core + tracer
  bullet
- ttsim [#118](https://github.com/ttsim-dev/ttsim/issues/118) — full dimension model
- ttsim [#119](https://github.com/ttsim-dev/ttsim/issues/119) — mandatory units +
  edge-consistency
- ttsim [#120](https://github.com/ttsim-dev/ttsim/issues/120) — currency knob + Layer-2
  boundary
- ttsim [#121](https://github.com/ttsim-dev/ttsim/issues/121) — annotate mettsim, switch
  check on, CI test
- gettsim [#1191](https://github.com/ttsim-dev/gettsim/issues/1191) — register EUR/DM
- gettsim [#1192](https://github.com/ttsim-dev/gettsim/issues/1192) — gettsim rollout

Each package's params schema enumerates its own token vocabulary: the core tokens minus
the agnostic currency tokens (the schema governs parameters, which must be concrete)
plus the concrete variants of that package's registered currencies. It also enforces,
per parameter `type:`, both the `unit:` XOR `input_unit:`/`output_unit:` split *and the
shape of the declaration itself*: a `type: scalar` parameter's `unit:` must be a single
token — the leaf-keys-to-tokens mapping form is admitted only for `type: dict` — and
`type: scalar` may not carry a `reference_period` (see
{ref}`Flow tokens <gep-10-periods>` above). It admits the per-entry overrides in dated
entries. The schema shipped with ttsim (listing mettsim's `CASTAR_*`/`SILVER_PENNY_*`
tokens) is the template; the copy at `docs/geps/params-schema.json` (the validation
target for all German parameter YAMLs) is migrated together with the YAML files in
#1192, adding the `DM_*`/`EUR_*` tokens.

## Alternatives

### Runtime pint Quantities flowing through the DAG

Rejected. `Quantity` is not a JAX pytree, breaks tracing, contradicts the GEP-9 column
vocabulary, and adds hot-path cost. Units in a tax-transfer model are static structural
properties of nodes, not of data, so runtime wrapping buys nothing the build-time check
does not already provide.

### Keep hand-written time conversions; use pint only for checks

Possible, but the stock/flow duality is exactly what a unit engine encodes for free.
Sourcing the factors from pint removes a class of hand-maintained arithmetic without
touching the naming.

### A `[count]` dimension for head counts

Considered, prototyped, and rejected. An earlier draft promoted counting quantities to a
custom `[count]` dimension, making per-person parameters `CURRENCY / count` and head
counts `count`. The intended payoff was catching a forgotten per-capita scaling. It was
dropped because:

- the protection is weaker than it looks: a single generic `[count]` cannot distinguish
  per-child from per-adult from per-household, so scaling by the *wrong* count still
  type-checks — only the forgot-entirely case is caught;
- the annotation tax lands on every per-capita parameter in the system (Regelsätze,
  Kindergeld, Freibeträge, …), which would read `CURRENCY / count` where the law and
  every practitioner say "Euros per month";
- SI and pint treat counting quantities as dimensionless; deviating surprises anyone who
  knows either.

The accepted cost is that a missing per-capita scaling is no longer a unit error. If
that bug class accumulates in practice, the closed token vocabulary makes a future
amendment with genuinely distinct dimensions (`[person]`, `[child]`, …) a clean
retrofit.

### Make functions time-agnostic

Rejected. Collapsing `betrag_m` and `betrag_y` into one node would erase the law-to-code
correspondence GEP 1 is built on.

## References and Footnotes

- [gettsim #1174 (the originating DM-values discussion)](https://github.com/ttsim-dev/gettsim/issues/1174)
- [pint](https://pint.readthedocs.io)
- [NEP 18 (NumPy `__array_function__`)](https://numpy.org/neps/nep-0018-array-function-protocol.html)

## Copyright

This document has been placed in the public domain.
