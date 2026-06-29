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

This GEP gives every quantity in GETTSIM a **unit** — Euros per month, Euros per square
meter, persons per Bedarfsgemeinschaft, etc. — declared on parameters, policy functions,
and (optionally) input data. The framework reads those units to do two things:

- **Dimensional safety.** It checks that the arithmetic combining quantities is sound,
  so mixing incompatible kinds — a monthly amount and a per-square-meter rent, or a
  headcount per Bedarfsgemeinschaft with a monthly amount per household — becomes a loud
  error when the policy environment is built, not a silent wrong number far downstream.
- **Automatic unit conversion.** It converts compatible quantities to a common unit, for
  example Euros to Deutsche Mark. The existing `_y`/`_q`/`_m`/`_w`/`_d` and
  aggregation-level (`_hh`, `_bg`, …) suffix conventions are preserved.

The engine is [pint](https://pint.readthedocs.io), and it runs **only while the policy
environment is built**: it checks dimensions and converts units, and plays no part at
run time, as it is not JAX-compatible. Thus, runtime of the plain tax and transfer
function is not affected by this GEP.

## Motivation and Scope

Four long-standing problems motivate this GEP.

1. **No dimensional safety.** The DAG carries quantities of many kinds, but a function
   body may add, subtract, or compare them freely. `betrag_m + miete_pro_qm_m` (a
   monthly amount plus a monthly rent *per square meter*) is a bug that runs silently
   today and surfaces, if noticed at all, as an implausible number far downstream.

1. **No grouping-level safety.** Quantities live at many grouping levels (`_hh`, `_bg`,
   `_sn`, …) and the framework broadcasts a coarser level down to the individuals it
   contains. Nothing stops a body from combining a household total with a
   Bedarfsgemeinschaft total, or forgetting the per-capita division that converts one
   level to another. Both are silent wrong numbers today.

1. **Hand-converted historical currency.** Every Deutsche-Mark-era parameter is divided
   by `1.95583` by the contributor before being written to YAML, with the original value
   preserved only in a free-text `note`. There is no machine-checkable provenance and no
   guard against a transcription error. This is both prone to errors and violates
   GETTSIM's law-to-code approach.

1. **Hand-written time arithmetic.** `ttsim/unit_converters.py` implements ~50
   conversion functions (`y_to_m`, `per_y_to_per_m`, …) and their stock/flow duals by
   hand. The resulting arithmetic has itself been a source of bugs.

**Scope.** The GEP covers `TTSIM` (the framework) and `GETTSIM` (the German currencies
and the policy annotations).

## Units as guards

A quantity's unit already says which operations are meaningful: two monthly amounts may
be added and an amount may be divided by a head count, but a monthly amount may not be
added to a rent per square metre, nor a household total to a Bedarfsgemeinschaft total.
Recording the unit on every parameter and function turns that into a check the framework
runs when the policy environment is built — a meaningful operation passes, a meaningless
one is a build error. The same units also drive automatic conversion, between time units
and between currencies (Euro ↔ Deutsche Mark).

(gep-10-vocabulary)=

## The unit vocabulary

Developers need to attach a unit to every policy function and parameter explicitly.
GETTSIM will check the unit's validity using the function's name, return type and its
arguments' units.

A unit is **compositional**: a base optionally divided by denominators, in a fixed
canonical order, joined by `_PER_`: <base> _PER_ <denominator> _PER_ <denominator> …,
with at most one denominator of each kind.

```text
base        := CURRENCY                       # agnostic, .py / functions only
             | EUR | DM | …                   # concrete currency, param-YAML only
             | DIMENSIONLESS
             | PERSON                          # the [person] count
             | HOURS                           # the isolated [hours] dimension
             | SQUARE_METER | HECTARE          # areas
             | YEARS | MONTHS | DAYS           # durations (stocks)
             | CALENDAR_YEAR | CALENDAR_MONTH | CALENDAR_DAY   # affine points
denominator := SQUARE_METER                          # area   (physical)
             | MONTH | YEAR | QUARTER | WEEK | DAY    # period (⇒ flow)
             | HH | BG | FG | SN | …                  # grouping level
canonical order := base _PER_ <area> _PER_ <period> _PER_ <level>
```

Rules:

- **Each denominator is classified** — by a closed vocabulary for area and period, and
  as a grouping level otherwise — into one of {area, period, level}. Having a *period*
  denominator is exactly what makes a unit a **flow**; a quantity with no period is a
  *stock*.
- **Canonical order, one per kind.** Denominators appear in the order
  `area · period · level`, at most one of each; a non-canonical spelling
  (`..._PER_BG_PER_MONTH`) or a repeat is rejected, so there is **exactly one spelling
  per unit**.
- **The person leaf is implied, never spelled.** The individual level is the default for
  every leveled quantity, so it is never written: a per-person monthly amount is
  `CURRENCY_PER_MONTH`. Only *group* levels are spelled (`CURRENCY_PER_MONTH_PER_HH`).

A few worked spellings:

| spelling                              | resolves to                     | typical use                |
| ------------------------------------- | ------------------------------- | -------------------------- |
| `CURRENCY_PER_MONTH`                  | `CURRENCY / month / [person]`   | a personal monthly amount  |
| `CURRENCY_PER_MONTH_PER_BG`           | `CURRENCY / month / [bg]`       | a benefit at bg level      |
| `CURRENCY`                            | `CURRENCY / [person]`           | wealth, an asset threshold |
| `DIMENSIONLESS`                       | `dimensionless`                 | a share, a rate            |
| `DIMENSIONLESS_PER_FAM`               | `1 / [fam]`                     | a fam-level boolean        |
| `DIMENSIONLESS_PER_YEAR`              | `1 / year`                      | Zugangsfaktor per year     |
| `PERSON_PER_BG`                       | `[person] / [bg]`               | a declared head count      |
| `HOURS_PER_WEEK`                      | `working_hour / week`           | working hours              |
| `CURRENCY_PER_SQUARE_METER_PER_MONTH` | `CURRENCY / meter ** 2 / month` | a rent cap                 |
| `YEARS` / `CALENDAR_YEAR`             | a duration / an affine point    | an age / a birth year      |

In `.py` modules, developers can work with autocomplete and the canonical order enforced
by the staged return types:

```python
Unit.CURRENCY.PER_MONTH.PER_BG  # -> "CURRENCY_PER_MONTH_PER_BG"
Unit.CURRENCY  # a stock, per person
Unit.PERSON.PER_BG  # a declared head count
Unit.DIMENSIONLESS  # a share, or a person-level boolean
Unit.DIMENSIONLESS.PER_FAM  # a fam-level boolean
Unit.HOURS.PER_WEEK
```

A special, but common, case is the currency dimension. GETTSIM supports two currencies:
Euros (EUR) and Deutsche Mark (DM). Policy functions are written to be currency-agnostic
— they run in either currency without change — so only parameters and input data carry a
concrete currency base ({ref}`Currency <gep-10-currency>`).

(gep-10-levels)=

### Grouping levels

GETTSIM data lives at grouping levels: the individual (the leaf, identified by `p_id`),
and one group per `*_id` column ({ref}`GEP 2 <gep-2>`) — in gettsim the household
(`hh`), the Familiengemeinschaft (`fg`), the Bedarfsgemeinschaft (`bg`), the tax unit
(`sn`), the Einsatzgemeinschaft (`eg`), the Ehegemeinschaft (`ehe`), and the
wohngeldrechtlicher Teilhaushalt (`wthh`). The framework discovers the levels from the
`*_id` columns of the policy environment and registers each as a base dimension; `TTSIM`
ships no fixed list. The unit builder learns a `PER_<level>` step for each.

**Each level is a base dimension.** There is no fixed conversion between a person and a
household — a household holds a *variable* number of persons — so the levels are not
units of one shared dimension (the way `month` and `year` are units of `[time]`) but
distinct, non-interconvertible base dimensions: `[person]`, `[hh]`, `[bg]`, and so on.
The individual level `[person]` doubles as the **count dimension**: counting persons and
denominating something per person are the same `[person]`, which is what lets head
counts and per-person amounts cancel cleanly (below).

**A level is a denominator.** A leveled quantity carries its level as a denominator,
exactly as a flow carries its period. For a column the level comes from the aggregation
suffix (an unsuffixed name is at `[person]`, a `_hh` name at `[hh]`); for a parameter it
is spelled in the unit string.

**Head counts.** A head count is the count dimension over the group it counts within. A
`COUNT` aggregation to the household yields `anzahl_personen_hh` with unit
`[person] / [hh]` — persons per household. Because the count's numerator `[person]` is
the *same* dimension as a person-level quantity's `[person]` denominator, the two
cancel:

```text
wohnen__bruttokaltmiete_m_hh / anzahl_personen_hh
  = (CURRENCY / month / [hh]) / ([person] / [hh])
  = CURRENCY / month / [person]      # a per-person rent share
```

```text
einnahmen__kapitalerträge_y_sn − familie__anzahl_personen_sn * sparerfreibetrag_y
  = CURRENCY / year / [sn] − ([person] / [sn]) · (CURRENCY / year / [person])
  = CURRENCY / year / [sn] − CURRENCY / year / [sn]      # the count bridges person → sn
```

The head count is the conversion factor between levels, and these cross-level bodies —
the per-capita divisions and the multiply-by-count splittings GETTSIM already performs —
type-check on their own once counts carry `[person]`.

(gep-10-booleans)=

### Leveled booleans

A boolean is a *leveled* quantity: a truth value about an entity at some level. A
person-level indicator is `1 / [person]`, a family-level one `1 / [fam]`. Like any
leveled quantity a person boolean is bare `DIMENSIONLESS` (the leaf implied), a group
boolean spells its level, `DIMENSIONLESS_PER_FAM`. A node is recognised as a boolean by
its `-> bool` return type (orthogonal to its declared unit), and that is what
distinguishes a boolean from a plain dimensionless *share*: a share stays level-less, a
boolean carries its level.

This catches a class of wrong-level predicate bugs. The function below carries a `_fam`
name, so it declares a family-level boolean (`1 / [fam]`); but its body compares two
*person*-level quantities, so the unit check infers `1 / [person]`. That contradicts the
`_fam` suffix, and the function throws an error:

```python
@policy_function(unit=Unit.DIMENSIONLESS.PER_FAM)  # claims 1 / [fam]
def requirement_fulfilled_fam(einkommen_m: float, schwelle_m: float) -> bool:
    return einkommen_m < schwelle_m  # but these are person-level → infers 1 / [person]
```

**Combine rule.** A logical operator (`&` / `|` / `^`) of two leveled booleans keeps the
level if they are equal and **downcasts to the person leaf** on any mismatch. The
downcast is sound and conservative: grouping levels do not nest, and a cross-level
logical combination is evaluated per person (each person sees its groups' indicators),
so the result is person-level. This is the operation a per-person gate actually needs —

```text
kind_in_anspruchsberechtigter_familie = child & requirement_fulfilled_fam
  = (1 / [person]) & (1 / [fam]) = 1 / [person]   # the per-person conjunction
```

— and it is implemented in the build-time check's logical operators directly, rather
than left to pint's multiplicative algebra (whose product never yields the lower of the
two levels a per-person result needs). A comparison of a leveled quantity against a
scalar yields a boolean at that level; `~` preserves the level.

(gep-10-hours)=

### Working hours are their own dimension

Working hours are a genuine dimension `[hours]`, registered as `working_hour` and
**isolated from pint's `[time]`**. This is deliberate: if working hours were based on
the `[time]` `hour`, then `hours / week` would be `[time] / [time]` and collapse to a
bare number — adding working hours to a share would not be caught, and an hours quantity
could not be told from a dimensionless one. With its own dimension, `HOURS_PER_WEEK` is
`[hours] / [time]`.

`HOURS_PER_WEEK → HOURS_PER_MONTH` re-bases the **period** only (the existing
time-conversion machinery), leaving the `[hours]` numerator untouched.

### Calendar points are distinct from durations

A year *on the calendar* — a birth year, the policy year — is an affine *point*, not a
*duration*. The two do not share arithmetic: subtracting two calendar years gives a
duration, and shifting a year by a duration gives a year, but two year cannot be added
and a year cannot be scaled. The `CALENDAR_YEAR` / `CALENDAR_MONTH` / `CALENDAR_DAY`
bases carry the calendar point; `YEARS` / `MONTHS` / `DAYS` carry the corresponding
duration. The build-time check enforces the algebra (the duration `D` of a point `P`):

| operation                 | result    | example                              |
| ------------------------- | --------- | ------------------------------------ |
| `P − P`                   | duration  | `policy_year − geburtsjahr` → an age |
| `P ± D` (same axis)       | point     | `geburtsjahr + statutory_age`        |
| `P + P`, `P × n`, `P / n` | **error** | two calendar years cannot be added   |
| mixing calendar axes      | **error** | a year point plus a month duration   |

A *cyclic* ordinal — a month-of-year (`geburtsmonat` 1–12), a day-of-week, a quarter —
is **not** a calendar point but `DIMENSIONLESS`: it is a recurring label, not a position
on a running calendar.

(gep-10-leveled)=

### Which quantities carry a level

A quantity carries a level in one of two cases:

- **additive amounts** — currency, area, the `[person]` count — where summing an
  entity's members is meaningful (a household income is the sum of its members'
  incomes).
- **booleans** — a truth value *about* an entity, whose level is tracked so the
  {ref}`combine rule <gep-10-booleans>` and the suffix check apply.

Everything else is **level-less**: `YEARS` / `MONTHS` / `DAYS`, `CALENDAR_*`, `HOURS`,
and plain `DIMENSIONLESS` shares and rates.

## Declaring units on functions and parameters

Every active node carries a unit. If no unit was specified, the unit is marked
`UNSET_UNIT` which throws an error at build time. Most nodes declare it directly;
derived nodes get one auto-assigned ({ref}`below <gep-10-auto>`), and framework-injected
date nodes get theirs from the framework (`policy_year` is a `CALENDAR_YEAR`).

### Policy functions

The declaration on a policy function is a guard rail: GETTSIM checks that the unit that
falls out of the function body — its physical dimension, its flow period, *and* its
grouping level — matches the declaration and the name suffixes, so a mismatch is a loud
error at definition time.

```python
@policy_function(unit=Unit.CURRENCY.PER_MONTH.PER_BG)  # -> CURRENCY / month / [bg]
def betrag_m_bg(regelsatz_m_bg: float, mehrbedarf_m_bg: float) -> float:
    return regelsatz_m_bg + mehrbedarf_m_bg


@policy_function(
    unit=Unit.CURRENCY
)  # a stock, per person; a time suffix would be an error
def vermögen(aktien: float, immobilien: float) -> float:
    return aktien + immobilien
```

### Parameters

The shape of the `unit:` declaration follows the parameter `type:`. Units can be defined
once for all policy dates (as described here), or for specific dates individually
(helpful for currency changeovers, see {ref}`Currency <gep-10-currency>`).

**Scalar.** One token; the parameter's *name* may carry a time suffix, which must agree
with the spelled period (`lump_sum_deduction_y` declaring `EUR_PER_YEAR`).

**Dict with homogeneous leaves.** One token for the whole structure:

```yaml
satz_nach_kindanzahl:
  unit: EUR_PER_MONTH       # one token; per person (leaf implied)
  type: dict
  2024-01-01:
    1: 250.0
    2: 250.0
```

**Dict with heterogeneous leaves.** `unit:` is a **mapping from leaf keys to tokens**:

```yaml
schedule:
  unit:
    child_amount_y: EUR_PER_YEAR    # string key; _y agrees with the spelled period
    max_age: YEARS
  type: dict
  2024-01-01:
    child_amount_y: 3000.0
    max_age: 18
```

The `unit:` mapping is a **union over all dated entries**: the mandatory-units check
looks only at the leaves present at the policy date and ignores entries for leaves that
exist only at other dates, so a leaf renamed across a reform is covered by listing both
names. A value leaf with no entry is a *missing* declaration and is flagged.

**Mapping parameters (schedules, lookup tables).** A schedule is not a quantity but a
*function between quantities*, with a domain and a codomain. The `piecewise_*` family,
the lookup tables, and the phase-in/out types declare `input_unit:` and `output_unit:`
instead of `unit:`; a `unit:` on them is an error, enforced per `type:` by the JSON
schema:

```yaml
tarif:
  input_unit: EUR_PER_YEAR    # taxable income per year in ...
  output_unit: EUR_PER_YEAR   # ... tax per year out
  type: piecewise_quadratic
  ...
```

A time suffix on the parameter's *name* describes what it yields, so it must coincide
with a flow `output_unit`.

(gep-10-auto)=

### Auto-generated nodes

Auto-generated nodes receive auto-assigned units. Time-conversion variants inherit the
source's base and re-base the period off the variant's own suffix
(`CURRENCY_PER_MONTH → CURRENCY_PER_YEAR`). Auto-aggregations derive their unit from the
source and the aggregation type, paralleling how {ref}`GEP 4 <gep-4>` resolves their
types — and, with grouping levels in the unit, the aggregation is where a level is
created, swapped, or acquired:

| aggregation                    | physical base   | level                                            |
| ------------------------------ | --------------- | ------------------------------------------------ |
| `SUM` / `MEAN` / `MIN` / `MAX` | preserved       | **target** level                                 |
| `COUNT`, `SUM` over a boolean  | `[person]`      | **created** `[person] / [target]`                |
| `ANY` / `ALL`                  | `DIMENSIONLESS` | boolean **at the target level** (`1 / [target]`) |

Sometimes, a policy may require a cross-level comparison, e.g. a group `MAX` against a
person value. The unit check will reject that, since the two levels are not compatible.
The author can opt out locally with `verify_units=False` on the function.

A hand-written aggregation also carries an author-declared unit (one is required to pass
the mandatory-units check), and that declaration is **checked against the derived
unit**, the same declared-vs-produced contract a `@policy_function` body is held to: its
physical *kind* — currency, the `[person]` count, area, a duration — must match what the
aggregation produces, so a `SUM` over a boolean declared `DIMENSIONLESS` rather than
`PERSON_PER_BG` is rejected.

### Literals

Adding dimensionless numbers to a non-dimensionless quantity is forbidden. A literal
that is only a multiplicative factor (`betrag * 0.5`) is fine — multiplying by a
dimensionless number preserves the unit.

Most apparent cases dissolve once the quantities are declared correctly: an ordinal such
as `geburtsmonat` (the month 1–12) is `DIMENSIONLESS`, so `geburtsmonat - 1` is
dimensionless arithmetic and needs no tag. For a genuine constant of a real dimension,
either **promote it to a parameter**:

```python
@policy_function(unit=Unit.DIMENSIONLESS)
def anspruchsberechtigt(einkommen_m: float) -> bool:
    return einkommen_m < 1000.0  # 1000.0 silently carries EUR/month → rejected
```

Promoting the bound to a parameter makes the body dimensionally sound:

```yaml
einkommensgrenze_m:
  unit: EUR_PER_MONTH
  type: scalar
  2024-01-01:
    value: 1000.0
```

```python
@policy_function(unit=Unit.DIMENSIONLESS)
def anspruchsberechtigt(einkommen_m: float, einkommensgrenze_m: float) -> bool:
    return einkommen_m < einkommensgrenze_m
```

If that doesn't work for some reason, the author can turn off unit checks for that
function with `@policy_function(verify_units=False)`.

The only exception is `0.0` which is a common literal for eligibility checks. The
following is dimensionally sound and does not raise an error:

```python
@policy_function(unit=Unit.CURRENCY.PER_MONTH)
def betrag_m(einkommen_m: float, befreit: bool) -> float:
    if befreit:
        return 0.0  # 0.0 is dimensionless, but takes the unit of the return type
    else:
        return einkommen_m
```

(gep-10-currency)=

## Currency

Currencies are units defined in the `[currency]` dimension, with concrete currencies
registered by downstream packages via
`register_currency(name, *, base=False, definition=None)`. GETTSIM registers `EUR`
(base) and `DM = EUR / 1.95583`. Registration does two things: it provides the
**conversion factors**, with pint as the single source of truth for the rate; and it
makes the upper-cased currency name a valid compositional **base** (`DM`,
`DM_PER_MONTH`, `DM_PER_SQUARE_METER_PER_MONTH`, `EUR_*`, …), so parameters can pin down
the concrete currency their numbers are written in.

**Agnostic and concrete bases.** The **currency-agnostic** base `CURRENCY` is a
placeholder for any registered currency: it declares the unit of a function or column
for which it does not matter which currency GETTSIM runs in. A **concrete currency**
base (`DM`, `EUR`) names one specific currency.

**Parameters must be concrete; functions must be agnostic.** A parameter's numbers are
written in a concrete currency — the declaration must name the denomination
(`EUR_PER_YEAR`, not `CURRENCY_PER_YEAR`). Columns and functions may *only* declare the
agnostic `CURRENCY` as base unit. A derived node — a time-conversion variant or an
aggregation of a concrete-currency parameter — inherits the **agnostic** counterpart, as
it computes on values already converted to the run currency.

**The run currency.** The `currency` argument to `main()` defaults to the registered
base currency; it is the currency the input data is taken to be in and that the outputs
come out in. At environment build, every currency-denominated *parameter* is converted
from its declared denomination to the run currency.

**A changeover within one parameter's history.** Many parameters were written in
Deutsche Mark before 2002 and in Euro afterward. Rather than repeating the currency on
every dated entry of the parameter YAMLs, the unit is **forward-filled**: each dated
entry inherits the most recent *earlier* `unit:` declaration. The first declaration is
the seed — either a top-level `unit:` shared by every date, or, as here, spelled on the
first dated entry. A dated entry that restates the unit becomes the new seed from its
date onward, so the unit is spelled once at the start and again only at each changeover;
the entries in between omit it:

```yaml
arbeitnehmerpauschbetrag_y:
  type: scalar
  1990-01-01:
    unit: DM_PER_YEAR      # the first declaration: Deutsche Mark until restated
    value: 2000
  2002-01-01:
    unit: EUR_PER_YEAR     # the changeover: Euro from here on
    value: 1044
  2011-01-01:
    value: 1000            # no unit: — inherits EUR_PER_YEAR
```

Resolution only ever looks **backward**. A dated entry with no `unit:`, no earlier
declaration, and no top-level seed stays unset, and the mandatory-units check reports it
as a missing declaration.

A restatement **replaces** the previous declaration wholesale; for a per-leaf `unit:`
mapping it must therefore spell *every* leaf, so a changeover cannot silently leave some
leaves in the old currency. This is independent of `updates_previous` (which merges a
dated entry's *value* into the previous one).

(gep-10-trees)=

## The unit-annotated input and output trees

Tagging input data with units is **optional**, through a dedicated unit-annotated input
tree — a sibling of the ordinary input tree in which every leaf is a pint `Quantity`.
When the mode is used **every** leaf must be tagged, including identifiers and other
dimensionless columns (tagged `dimensionless`). Symmetrically, the **unit-annotated
result tree** relabels each output leaf with its precise run-currency unit
(`euro/month`, not the agnostic `CURRENCY`). The check the input tree enables is
{ref}`Layer 2 <gep-10-checks>` below.

(gep-10-checks)=

## Consistency checks and their limits

### pint runs at build time only

The foundational constraint is that pint never wraps a live array. A `pint.Quantity` is
not a JAX pytree and does not trace under `jit`; wrapping runtime columns would fight
both JAX and the GEP-9 `FloatColumn` vocabulary. Instead, pint is used in two build-time
roles:

- to compute conversion **factors** (time and currency), which are baked into the
  compiled workers as plain numeric constants; and
- to run the **dry-run** dimensionality check on representative `Quantity`s.

The numeric runtime path stays pure arrays, single currency, and JAX-safe.

The checks run in two layers, both at build time:

|        | **Layer 1 — DAG validity**                                        | **Layer 2 — boundary**                                                                                                                 |
| ------ | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| when   | `fail_if` on the assembled environment                            | where GEP-9 normalises user input into canonical arrays                                                                                |
| input  | none — synthetic `Quantity`s                                      | the user's unit-annotated input tree                                                                                                   |
| checks | inferred body unit vs. declaration; producer↔consumer edges agree | tag currency → run currency; period vs. suffix; level vs. suffix; unknown spelling rejected; every tag equivalent to its resolved unit |

### Layer 1: the dry-run dimensionality check

**Layer 1** runs each scalar body in NumPy+pint, infers the unit that falls out, and
checks it against the declaration; an edge-consistency pass then confirms each
producer's unit equals its consumer's declared expectation.

**How the dry-run checks one body.** The check *runs the function body*, but with
**units in place of numbers**. Each input becomes a stand-in carrying its resolved unit
— physical dimension, flow period, *and* grouping level — and a throwaway magnitude of
`1`; pint carries the units through the body's arithmetic, and the unit that falls out
of the `return` is compared to the declaration:

```python
@policy_function(unit=Unit.CURRENCY.PER_MONTH)  # -> CURRENCY / month / [person]
def bruttokaltmiete_m(
    wohnen__bruttokaltmiete_m_hh: float, anzahl_personen_hh: int
) -> float:
    return wohnen__bruttokaltmiete_m_hh / anzahl_personen_hh
```

Here `wohnen__bruttokaltmiete_m_hh` enters as `EUR / month / [hh]` and
`anzahl_personen_hh` as `[person] / [hh]`; the division cancels `[hh]` and yields
`EUR / month / [person]` — matching the unit declaration *and* being consistent with the
function name name.

**Every branch is covered, by re-running.** A unit stand-in has no value to compare, so
it intercepts the *truth test* itself (Python's `__bool__`) and hands it to the **path
explorer**, which re-runs the body and steers each open branch both ways until every
reachable branch combination is driven. Each run is checked on its own, so a unit slip
on one arm is caught while the others are clean.

**What the dry-run catches:**

- a body whose inferred unit disagrees with its declaration, on any reachable branch — a
  `_m` flow returned where `_y` is declared, or a `…/[person]` result on a `_hh` name (a
  level-less result at a group suffix is exempt — its index-correctness is the
  structural system's concern, not the unit check's);
- an addition or subtraction of two non-equivalent quantities — a monthly flow plus a
  yearly one (`betrag_m + freibetrag_y`), a stock plus a flow, **or two different
  grouping levels** (`einkommen_m_hh − einkommen_m_bg`);
- an ordering comparison (`<`, `<=`, `>`, `>=`) of two non-equivalent quantities, or of
  a quantity against a bare non-zero literal that silently carries the quantity's unit
  (so promote the bound to a parameter; only `0` is allowed inline). Equality (`==`,
  `!=`) is deliberately **not** screened: it is the operator for sentinel and
  exact-marker tests (`p_id_empfänger == -1`, `kindersatz_m == 0.0`), where the literal
  is a deliberate marker, not a hidden dimensioned bound;
- a logical operator (`&`, `|`, `^`, `~`) applied to a non-boolean operand
  (`wealth & is_adult`, where `wealth` is a stock); a cross-level boolean combination is
  resolved by the {ref}`combine rule <gep-10-booleans>`, not rejected;
- a missing unit, and malformed declarations: a non-canonical or repeated denominator, a
  flow function without a specified period unit, a currency-agnostic base on a
  parameter, a group column or boolean that fails to spell its level, or a spelled level
  disagreeing with the name suffix.

### Layer 2: the boundary check

**Layer 2** compares each tagged leaf of the
{ref}`unit-annotated input tree <gep-10-trees>` to the unit the environment resolves for
that leaf. The check throws an error if dimensions are incompatible. Note that units
don't need to be identical. Automatic time and group conversions (see GEP 1), and
currency conversions (this GEP) are performed at the boundary.

## Backward Compatibility

- **User code shape is unchanged.** Bare arrays and the DataFrame/mapper interface keep
  working; `currency` defaults to `"EUR"` and output stays in Euros.
- **`unit` is repurposed; `reference_period` and `reference_level` are removed.** `unit`
  becomes a compositional spelling. The period a flow used to record in
  `reference_period`, and the level a per-group amount used to record in
  `reference_level`, are now **folded into the unit string** (`EUR_PER_YEAR_PER_FAM`),
  so there is a single source of truth and the two fields are gone.
- **No blanket opt-out.** There is no env-var escape hatch that switches the unit check
  off wholesale. Users can opt out for specific functions (`verify_units=False`,
  {ref}`see <gep-10-checks>`) or opt out of some checks by turning off GETTSIM's fail-if
  nodes.

## Related Work

- {ref}`GEP 9 <gep-9>`: runtime type checking via beartype; this GEP follows its
  build-boundary philosophy and its "loud at the boundary you wrote" goal.
- {ref}`GEP 1 <gep-1>`: the time and aggregation-level suffix conventions this GEP
  preserves and makes machine-checked.
- {ref}`GEP 2 <gep-2>`: the `*_id` group identifiers from which the grouping levels are
  derived.
- [pint](https://pint.readthedocs.io): the unit registry, dimensionality analysis, and
  NumPy (NEP-18) support relied on here.

## Implementation

Delivered as one infrastructure PR, with the framework proven on `METTSIM` before any
German annotation:

- TTSIM [#138](https://github.com/ttsim-dev/ttsim/pull/138) — the full GEP-10
  infrastructure in one final-form diff: the pint registry and dimension model (time,
  currency, the `[hours]` dimension, **grouping levels and the `[person]` count**), the
  compositional vocabulary, mandatory units, edge- and target-level aggregation
  consistency, the dry-run, the currency knob, and the Layer-2 boundary conversion.
  (This collapses an earlier three-way infra split, now closed: #139, #140.)
- TTSIM [#141](https://github.com/ttsim-dev/ttsim/pull/141) — annotate `METTSIM`
  end-to-end (the worked example), switch the check on, CI test over all dates

Each package's params schema validates the compositional spelling (a coarse
`^[A-Z][A-Z0-9_]*$` pattern, with `parse_compositional_unit` enforcing the grammar at
load time) and enforces, per parameter `type:`, the `unit:` XOR
`input_unit:`/`output_unit:` split, the shape of the declaration (a `type: scalar`
`unit:` is a single token; the leaf-keys mapping form is admitted only for
`type: dict`), and the concrete-currency rule for parameters. The schema shipped with
TTSIM (listing METTSIM's `SILVER_PENNY`/`CASTAR` currencies and Middle-Earth levels) is
the template; the copy at `docs/geps/params-schema.json` is migrated together with the
YAML files in #1192.

## Alternatives

### Why grouping levels are pint dimensions

Three weaker level models were rejected in favour of making each grouping level a
non-interconvertible pint dimension and the `[person]` count its own dimension:

- **Counts as plain `DIMENSIONLESS`** (an earlier draft, and the SI/pint convention). A
  count then cannot be told from a share, the per-capita divisions infer a bare currency
  instead of a per-person amount, and a household total cannot be told from a
  Bedarfsgemeinschaft total. The `[person]` count and the level dimensions are exactly
  what turn the cross-level bodies GETTSIM already writes into self-checking arithmetic.
- **A single generic `[count]`**, with per-person parameters as `CURRENCY / count`. It
  cannot say *which* group a count is over, so `anzahl_personen_hh` and
  `anzahl_personen_bg` stay interchangeable and a cross-level mix still type-checks; and
  `CURRENCY / count` reads where the law says "Euros per month". The adopted
  `[person]/[group]` fixes both, and a per-person amount stays plain `EUR_PER_MONTH`.
- **A separate, non-unit level tag** beside the pint unit (as the column's index level
  already is, {ref}`GEP 2 <gep-2>`). The payoff — per-capita divisions that type-check,
  cross-level additions that fail — comes precisely from the level living in pint's
  algebra; a separate tag would re-implement it and could not make
  `(CURRENCY/[hh]) / ([person]/[hh])` cancel to `CURRENCY/[person]` for free.

### Spelling the person leaf

Rejected. The person leaf could be spelled (`CURRENCY_PER_MONTH_PER_PERSON`) for full
symmetry with group levels. But then two spellings would denote the same unit (the bare
and the `_PER_PERSON` form), violating the one-spelling-per-unit invariant, and the
common case — a per-person amount — would carry the noisiest spelling. Implying the leaf
and rejecting `_PER_PERSON` keeps one canonical spelling and the short form for the
common case; only group levels, which genuinely vary, are spelled.

### Runtime pint Quantities flowing through the DAG

Rejected. `Quantity` is not a JAX pytree and breaks tracing. Units in a tax-transfer
model are static structural properties of nodes, not of data, so runtime wrapping buys
nothing the build-time check does not already provide.

### Make functions time-agnostic

Rejected. Collapsing `betrag_m` and `betrag_y` into one node would erase the law-to-code
correspondence GEP 1 is built on.

## References and Footnotes

- [gettsim #1174 (the originating DM-values discussion)](https://github.com/ttsim-dev/gettsim/issues/1174)
- [pint](https://pint.readthedocs.io)
- [NEP 18 (NumPy `__array_function__`)](https://numpy.org/neps/nep-0018-array-function-protocol.html)

## Copyright

This document has been placed in the public domain.
