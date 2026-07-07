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
run time, as it is not JAX-compatible. The computation of taxes and transfers itself is
untouched, and its runtime unaffected.

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
             | PERSON_COUNT                    # the [person] count
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
- **Whether a bare spelling carries the implied leaf is fixed by the vocabulary.** The
  person leaf attaches iff the quantity is one a person can *own*: the base is extensive
  — an amount a group can total: the currencies, `PERSON_COUNT`, the areas, `HOURS` —
  and no area denominator is present (an area denominator makes the unit a price or a
  density, which nobody owns: a rent cap is `CURRENCY / meter ** 2 / month`, no leaf).
  The intensive bases — `DIMENSIONLESS`, the durations, the calendar points — are always
  bare: an age is `month`, not `month / [person]`, because ages do not total across
  persons (booleans are the exception — a boolean carries its level,
  {ref}`below <gep-10-booleans>`). The *resolves to* column of the table below is
  authoritative.

A few worked spellings:

| spelling                              | resolves to                      | typical use                |
| ------------------------------------- | -------------------------------- | -------------------------- |
| `CURRENCY_PER_MONTH`                  | `CURRENCY / month / [person]`    | a personal monthly amount  |
| `CURRENCY_PER_MONTH_PER_BG`           | `CURRENCY / month / [bg]`        | a benefit at bg level      |
| `CURRENCY`                            | `CURRENCY / [person]`            | wealth, an asset threshold |
| `DIMENSIONLESS`                       | `dimensionless`                  | a share, a rate            |
| `DIMENSIONLESS_PER_FG`                | `1 / [fg]`                       | an fg-level boolean        |
| `DIMENSIONLESS_PER_YEAR`              | `1 / year`                       | Zugangsfaktor per year     |
| `PERSON_COUNT_PER_BG`                 | `[person] / [bg]`                | a declared head count      |
| `HOURS_PER_WEEK`                      | `working_hour / week / [person]` | working hours              |
| `CURRENCY_PER_SQUARE_METER_PER_MONTH` | `CURRENCY / meter ** 2 / month`  | a rent cap                 |
| `YEARS` / `CALENDAR_YEAR`             | a duration / an affine point     | an age / a birth year      |

In `.py` modules, developers can work with autocomplete and the canonical order enforced
by the staged return types:

```python
Unit.CURRENCY.PER_MONTH.PER_BG  # -> "CURRENCY_PER_MONTH_PER_BG"
Unit.CURRENCY  # a stock, per person
Unit.PERSON_COUNT.PER_BG  # a declared head count
Unit.DIMENSIONLESS  # a share, or a person-level boolean
Unit.DIMENSIONLESS.PER_FG  # an fg-level boolean
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
exactly as a flow carries its period.

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

(gep-10-leveled)=

### Which quantities carry a level

A quantity carries a group level **iff it is a property of the group as a whole**; a
property of a *person* carries none, even when its value is equal across the group. What
decides is whom the value is about — not its type, nor how it is computed. The
household's rent is `CURRENCY/month/[hh]`; a person's share of it is
`CURRENCY/month/[person]`.

The level is therefore **stated, not read off the suffix**: the suffix says the column
is constant within that group ({ref}`GEP 2 <gep-2>`), the level says whether the value
is the group's or an individual's. The suffix constrains the declaration but does not
determine it: a group property spells its level, which must match the suffix; a person
property is declared level-less *even when its name carries a group suffix* —
`regelbedarf_pro_person_m_bg` is `CURRENCY/month/[person]`, no `[bg]`, despite its name.

- **Group properties (a level attached).** Totals and counts (currency, area, hours, the
  `[person]` count); an extreme (`alter_monate_jüngstes_mitglied_fg` → `MONTHS/[fg]`); a
  group indicator (`bewohnt_eigentum_hh` → `1/[hh]`); a graded label (`mietstufe_hh` →
  `DIMENSIONLESS_PER_HH`).
- **Person properties (individual — no level attached).** A person's income, age, or
  birth year; a per-person fraction (`anteil_wohnfläche_pro_person_bg`); an average
  (per-head). No level is attached: the value stays at the individual grain, carrying
  the implied person leaf or staying bare as its base dictates
  ({ref}`above <gep-10-vocabulary>`).

Note that the cost of such a substantive definition is that some things that are
mathematically similar are treated differently. Take, for example,
`alter_monate_jüngstes_mitglied_fg` and `alter_monate` — both are ages, but the former
is a property of the family and carries the `[fg]` level, while the latter is a property
of the individual and carries no level. Against an age threshold parameter
`altersgrenze` (`MONTHS`), the person-level age screens cleanly, but the group extreme
mismatches (`MONTHS/[fg]` against `MONTHS`) — even where the law mandates exactly this
test. The resolution is the expression-level cast `cast_unit`
({ref}`below <gep-10-opt-out>`), which states the intended per-person reading at the
site and keeps the rest of the body checked:

```python
cast_unit(alter_monate_jüngstes_mitglied_fg, Unit.MONTHS) <= altersgrenze
```

Another example is `wohnbedarf_anteil_eltern_bg` (the share parents make up of the
Bedarfsgemeinschaft's Wohnbedarf). Because it is a property of the group, it carries the
`[bg]` level. However, when multiplying the share with another quantity defined on the
Bedarfsgemeinschaft level, the result is a unit with a squared [bg] denominator:

```text
wohnbedarf_anteil_eltern_bg * wohnbedarf_m_bg
  = (1 / [bg]) * (CURRENCY / month / [bg])
  = CURRENCY / month / [bg] ** 2
```

Developers need to judge on a case-by-case basis whether a unit mismatch is a bug or a
legitimate cross-level operation mandated by the policy. If the latter, the cast states
the intended result:

```python
cast_unit(wohnbedarf_anteil_eltern_bg * wohnbedarf_m_bg, Unit.CURRENCY.PER_MONTH.PER_BG)
```

(gep-10-booleans)=

### Leveled booleans

A boolean is a *leveled* quantity: a truth value about an entity at some level. A
person-level indicator is `1 / [person]`, a Familiengemeinschaft-level one `1 / [fg]`.
Like any leveled quantity a person boolean is bare `DIMENSIONLESS` (the leaf implied), a
group boolean spells its level, `DIMENSIONLESS_PER_FG`. A node is recognised as a
boolean by its `-> bool` return type (orthogonal to its declared unit), and that is what
distinguishes a boolean from a plain dimensionless *share*: a share stays level-less, a
boolean carries its level.

This catches a class of wrong-level predicate bugs. The function below carries a `_fg`
name, so it declares a family-level boolean (`1 / [fg]`); but its body compares two
*person*-level quantities, so the unit check infers `1 / [person]`. That contradicts the
`_fg` suffix, and the function throws an error:

```python
@policy_function(unit=Unit.DIMENSIONLESS.PER_FG)  # claims 1 / [fg]
def requirement_fulfilled_fg(einkommen_m: float, schwelle_m: float) -> bool:
    return einkommen_m < schwelle_m  # but these are person-level → infers 1 / [person]
```

**Combine rule.** A logical operator (`&` / `|` / `^`) of two leveled booleans keeps the
level if they are equal and **downcasts to the person leaf** on any mismatch. The
downcast is sound and conservative: grouping levels do not nest, and a cross-level
logical combination is evaluated per person (each person sees its groups' indicators),
so the result is person-level. This is the operation a per-person gate actually needs —

```text
kind_in_anspruchsberechtigter_familie = child & requirement_fulfilled_fg
  = (1 / [person]) & (1 / [fg]) = 1 / [person]   # the per-person conjunction
```

— and it is implemented in the build-time check's logical operators directly, rather
than left to pint's multiplicative algebra (whose product never yields the lower of the
two levels a per-person result needs). An ordering comparison requires equivalent units
on both sides — the literal `0` excepted, which takes the other side's unit
({ref}`below <gep-10-checks>`) — and yields a boolean at the operands' level; `~`
preserves the level.

(gep-10-hours)=

### Working hours are their own dimension

Working hours are a genuine dimension `[hours]`, registered as `working_hour` and
**isolated from pint's `[time]`**. This is deliberate: if working hours were based on
the `[time]` `hour`, then `hours / week` would be `[time] / [time]` and collapse to a
bare number — adding working hours to a share would not be caught, and an hours quantity
could not be told from a dimensionless one. With its own dimension, `HOURS_PER_WEEK` is
`[hours] / [time] / [person]` (the person leaf implied as usual).

`HOURS_PER_WEEK → HOURS_PER_MONTH` re-bases the **period** only (the existing
time-conversion machinery), leaving the `[hours]` numerator untouched.

### Calendar points are distinct from durations

A year *on the calendar* — a birth year, the policy year — is an affine *point*, not a
*duration*. The two do not share arithmetic: subtracting two calendar years gives a
duration, and shifting a year by a duration gives a year, but two years cannot be added
and a year cannot be scaled. The `CALENDAR_YEAR` / `CALENDAR_MONTH` / `CALENDAR_DAY`
bases carry the calendar point; `YEARS` / `MONTHS` / `DAYS` carry the corresponding
duration. The build-time check enforces the algebra (`P` a point, `D` a duration):

| operation                 | result    | example                              |
| ------------------------- | --------- | ------------------------------------ |
| `P − P`                   | duration  | `policy_year − geburtsjahr` → an age |
| `P ± D` (same axis)       | point     | `geburtsjahr + statutory_age`        |
| `P + P`, `P × n`, `P / n` | **error** | two calendar years cannot be added   |
| mixing calendar axes      | **error** | a year point plus a month duration   |

Granularities are separate axes, for durations as well as for points: `CALENDAR_YEAR`
pairs with `YEARS`, `CALENDAR_MONTH` with `MONTHS`, `CALENDAR_DAY` with `DAYS`, and a
duration adds neither to a point nor to a duration of another granularity. The
conversion factor is fixed — a year is twelve months — but applying it silently is
exactly the bug the split exists to catch: a month count folded into a year count
without the division by twelve. Where the conversion is intended, it is made in the open
and the result re-tagged ({ref}`below <gep-10-opt-out>`):

```python
geburtsjahr + cast_unit(alter_monate / 12, Unit.YEARS)  # CALENDAR_YEAR ± YEARS
```

A *cyclic* ordinal — a month-of-year (`geburtsmonat` 1–12), a day-of-week, a quarter —
is **not** a calendar point but `DIMENSIONLESS`: it is a recurring label, not a position
on a running calendar. The difference is the count: a `CALENDAR_MONTH` runs 0, 1, 2, …
from its epoch without bound, so each value pins one absolute month (January 2019 =
December 2018 + 1), whereas a month-of-year only runs 1–12 and wraps, so `3` is March in
*any* year and pins nothing.

## Declaring units on functions and parameters

Every active node carries a unit. The declaration decorators (`@policy_function`,
`@policy_input`, `@param_function`) take `unit=` as a required argument, so omitting it
there is an immediate error; wherever a declaration cannot be forced at definition time
— a parameter YAML, a hand-written aggregation — a missing unit is marked `UNSET_UNIT`
and the mandatory-units check reports it at build time. Most nodes declare the unit
directly; derived nodes get one auto-assigned ({ref}`below <gep-10-auto>`), and
framework-injected date nodes get theirs from the framework (`policy_year` is a
`CALENDAR_YEAR`).

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
types. With grouping levels in the unit, the aggregation is where a level is created or
swapped — and it turns on **what the aggregated value is about**. A sum, a count, an
extreme (`MIN`/`MAX`), or an all/any indicator is a property of the group, so it takes
the **target** level whatever the source's base — an age min'd to the family is
`MONTHS/[fg]`, no longer level-less. A **mean** is the exception: an average per head
belongs to the person, so it stays at the **individual** level — which is just what the
algebra yields, the group sum divided by the head count:
`(CURRENCY/[hh]) / ([person]/[hh]) = CURRENCY/[person]`.

| aggregation                       | physical base   | level                                                                                                        |
| --------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------ |
| `SUM` / `MIN` / `MAX`, any source | preserved       | source level **swapped for the target** (`CURRENCY/[person] → CURRENCY/[hh]`; `MONTHS → MONTHS/[fg]`)        |
| `MEAN`, any source                | preserved       | **individual** — the group sum over the head count (`(CURRENCY/[hh]) / ([person]/[hh]) → CURRENCY/[person]`) |
| `COUNT`                           | `[person]`      | **minted** `[person] / [target]`                                                                             |
| `ANY` / `ALL`                     | `DIMENSIONLESS` | boolean **at the target level** (`1 / [target]`)                                                             |

Sometimes, a policy may require a cross-level comparison, e.g. a group `MAX` against a
person value. The unit check will reject that, since the two levels are not compatible;
where the comparison is policy-mandated, the author states the intended reading at the
site with `cast_unit` ({ref}`below <gep-10-opt-out>`).

A hand-written aggregation also carries an author-declared unit (one is required to pass
the mandatory-units check), and that declaration must **equal the derived unit exactly**
— the same declared-vs-produced contract a `@policy_function` body is held to, but a
*full* match, not merely the physical kind: the dimension, the flow period, **and** the
grouping level must all agree. Only the person leaf is implied; a group level must be
spelled. So a `SUM` of a per-person `CURRENCY_PER_MONTH` to the `bg` level must be
declared `CURRENCY_PER_MONTH_PER_BG`.

(gep-10-literals)=

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

For a genuine dimensioned constant that must stay inline, the cast tags it in place —
`einkommen_m < cast_unit(1000.0, Unit.CURRENCY.PER_MONTH)`
({ref}`below <gep-10-opt-out>`).

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
tree — a sibling of the ordinary input tree in which every leaf is a
`UnitAnnotatedColumn(values=…, unit=…)`, its `unit` built off the same `Unit` vocabulary
as the policy functions. When the mode is used **every** leaf must be tagged,
identifiers and other dimensionless columns included (`unit=Unit.DIMENSIONLESS`). Two
rules mirror the parameter side: a currency column names a **concrete** currency
(`Unit.EUR`, `Unit.DM`) — the agnostic `Unit.CURRENCY` is rejected, exactly as for a
parameter — and the tag's grouping level must equal the level the column's **declared**
unit carries ({ref}`above <gep-10-leveled>`): a group-owned column spells its level
(`Unit.EUR.PER_MONTH.PER_BG`), a person property is tagged without one, even at a group
suffix. The **result tree** is the *same shape*: each output leaf is a
`UnitAnnotatedColumn` too, its `unit` the node's resolved unit in the concrete *run*
currency (`Unit.EUR.PER_MONTH.PER_BG`, never the agnostic `CURRENCY`). Annotated input
and annotated output are independent: either can be used without the other. The check
the input tree enables is {ref}`Layer 2 <gep-10-checks>` below.

```python
from gettsim import InputData, MainTarget, TTTargets, main
from gettsim.tt import Unit, UnitAnnotatedColumn

# `transfer` here is an illustrative stand-in, not a real benefit.
input_tree = {
    "p_id": UnitAnnotatedColumn(values=[0, 1, 2], unit=Unit.DIMENSIONLESS),
    "bg_id": UnitAnnotatedColumn(values=[0, 0, 0], unit=Unit.DIMENSIONLESS),
    "geburtsjahr": UnitAnnotatedColumn(
        values=[1980, 1982, 2015], unit=Unit.CALENDAR_YEAR
    ),
    "einkommen_m": UnitAnnotatedColumn(
        values=[2000.0, 0.0, 0.0], unit=Unit.EUR.PER_MONTH
    ),
    "miete_m_bg": UnitAnnotatedColumn(
        values=[1200.0, 1200.0, 1200.0], unit=Unit.EUR.PER_MONTH.PER_BG
    ),
}

results = main(
    main_target=MainTarget.results.tree_with_unit_annotations,
    policy_date_str="2025-01-01",
    input_data=InputData.tree_with_unit_annotations(input_tree),
    tt_targets=TTTargets(tree={"transfer": {"betrag_m_bg": None}}),
)

# results ==
# {"transfer": {"betrag_m_bg": UnitAnnotatedColumn(
#     values=array([250.0, 0.0, 0.0]), unit=Unit.EUR.PER_MONTH.PER_BG)}}
```

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

|        | **Layer 1 — DAG validity**                                                                                                  | **Layer 2 — boundary**                                                                                                                      |
| ------ | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| when   | `fail_if` on the assembled environment                                                                                      | where GEP-9 normalises user input into canonical arrays                                                                                     |
| input  | none — synthetic `Quantity`s                                                                                                | the user's unit-annotated input tree                                                                                                        |
| checks | inferred body unit vs. declaration; edges checked through the bodies (each argument enters at its producer's resolved unit) | tag currency → run currency; period vs. suffix; level vs. declaration; unknown spelling rejected; every tag equivalent to its resolved unit |

### Layer 1: the dry-run dimensionality check

**Layer 1** runs each function body in NumPy+pint, infers the unit that falls out, and
checks it against the declaration. The DAG's edges need no pass of their own: every
argument enters the consumer's dry-run carrying its *producer's* resolved unit — the
producer's declaration is the edge contract — so a producer↔consumer disagreement
surfaces inside the consumer, at the operation that combines the mismatched quantity or
at the consumer's own return-vs-declaration check. The one edge with neither a body nor
a spelled unit on both ends is the aggregation, which is checked declared-vs-derived
instead ({ref}`above <gep-10-auto>`).

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
function name.

**Every branch is covered, by re-running.** A unit stand-in has no value to compare, so
it intercepts the *truth test* itself (Python's `__bool__`) and hands it to the **path
explorer**, which re-runs the body and steers each open branch both ways until every
reachable branch combination is driven. Each run is checked on its own, so a unit slip
on one arm is caught while the others are clean.

**A failure names the branch.** The error reports the declared and the inferred unit —
compositional spelling and resolved form — and, where the body branches, the branch
combination that produced the mismatch:

```text
Unit check failed for `transfer__betrag_m`:
  declared  CURRENCY_PER_MONTH  =  CURRENCY / month / [person]
  inferred  CURRENCY_PER_YEAR   =  CURRENCY / year / [person]
  on the branch where `befreit` is False:
      return einkommen_y
  All other branches match the declaration.
```

**Vectorized bodies are checked at the same parity.** A body that computes on whole
columns (`vectorization_strategy="not_required"`) — or a scalar body after the
vectorizer's rewrite — calls `xnp` array ops instead of scalar operators. The dry-run
hands such a body an `xnp` stand-in that routes every unit-bearing op through the same
checking primitives the operators use: `xnp.maximum` / `xnp.minimum` screen like an
ordering comparison, `xnp.where` requires equivalent units on its two arms (they become
one column), `xnp.clip` screens each bound, and reductions and shape ops preserve the
unit. The framework primitives are screened at their edges the same way: a
`piecewise_polynomial(...)` call or a lookup table's `.look_up(...)` is checked against
the schedule's declared `input_unit` and produces its `output_unit`; a `join(...)`
gather hands on the target column's unit, grouping level included. A
`cast_unit(value, unit)` call is the identity at run time and re-tags the stand-in with
the stated unit in the dry-run ({ref}`below <gep-10-opt-out>`). An op the dry-run does
not model is never waved through silently: the check fails and demands an explicit
opt-out.

**What the dry-run catches:**

- a body whose inferred unit disagrees with its declaration, on any reachable branch — a
  `_m` flow returned where `_y` is declared, or a `…/[person]` result where the
  declaration spells `…_PER_HH`. The inferred grouping level is checked against the
  **declaration**, not the name suffix ({ref}`above <gep-10-leveled>`), and the match is
  exact: a body whose arithmetic cannot produce the declared group level — a graded
  label computed from level-less shares, say — states it with `cast_unit` at the return;
- an addition or subtraction of two non-equivalent quantities — a monthly flow plus a
  yearly one (`betrag_m + freibetrag_y`), a stock plus a flow, **or two different
  grouping levels** (`einkommen_m_hh − einkommen_m_bg`) — or of a bare non-zero literal
  (`einkommen_m + 100.0`), which silently carries the quantity's unit exactly as in an
  ordering comparison; a bare non-zero literal *returned* under a dimensioned
  declaration is rejected the same way (only `0` passes inline,
  {ref}`Literals <gep-10-literals>`);
- an ordering comparison (`<`, `<=`, `>`, `>=`) of two non-equivalent quantities, or of
  a quantity against a bare non-zero literal that silently carries the quantity's unit
  (so promote the bound to a parameter or tag it with `cast_unit`; only `0` is allowed
  inline). Equality (`==`, `!=`) is deliberately **not** screened: it is the operator
  for sentinel and exact-marker tests (`p_id_empfänger == -1`, `kindersatz_m == 0.0`),
  where the literal is a deliberate marker, not a hidden dimensioned bound;
- a logical operator (`&`, `|`, `^`, `~`) applied to a non-boolean operand
  (`wealth & is_adult`, where `wealth` is a stock); a cross-level boolean combination is
  resolved by the {ref}`combine rule <gep-10-booleans>`, not rejected;
- a missing unit, and malformed declarations: a non-canonical or repeated denominator, a
  flow function without a specified period unit, a currency-agnostic base on a
  parameter, or a spelled group level disagreeing with the name suffix.

(gep-10-opt-out)=

### When to opt out (`cast_unit`, `verify_units=False`)

Two escapes exist, at two grains; the narrow one is preferred wherever it suffices.

**The expression-level cast.** `cast_unit(value, unit)`, exported from the `tt`
namespace, re-tags a single expression with the stated unit — dimension, period, and
grouping level, wholesale. Like `typing.cast`, it does nothing at run time: it returns
`value` unchanged, scalar or column, so the numeric path and JAX tracing are untouched;
only the dry-run gives it meaning, re-tagging the stand-in that flows through it. The
rest of the body stays checked, and every override is visible — and greppable — at the
expression that needs it. Use it where a single operation is dimensionally irregular but
deliberate:

- **Policy-mandated cross-level arithmetic** ({ref}`above <gep-10-leveled>`): the law
  compares a group extreme to a person-level threshold, or multiplies two group-level
  quantities.
- **A granularity conversion on the calendar axes**:
  `cast_unit(alter_monate / 12, Unit.YEARS)`.
- **A genuine dimensioned constant** that cannot be promoted to a parameter
  ({ref}`Literals <gep-10-literals>`).

**The function-level opt-out.** `verify_units=False` skips the body's inference
entirely; the declared unit still stands as the edge contract, so an opted-out
function's consumers are checked as usual. It remains for bodies the dry-run cannot run
at all:

- **Structured values.** A `@param_function` that *builds* a structured object — a
  dataclass of related parameters, a schedule assembled from a `require_converter` blob
  — returns something that is not a quantity, so its body cannot be unit-checked; a body
  that *consumes* such an object through attribute access opts out for the same reason.
- **Converter-built schedules.** A body calling `piecewise_polynomial` on a schedule a
  `@param_function` produced (rather than one declared as a parameter) cannot be
  screened — the converter's output carries no `input_unit`/`output_unit` axes to check
  against. Schedules declared in YAML are covered; only converter-built ones need the
  opt-out.
- **An `xnp` operation the dry-run does not model** — rare, and never waved through
  silently: the check fails and demands the opt-out.

### Layer 2: the boundary check

**Layer 2** compares each tagged leaf of the
{ref}`unit-annotated input tree <gep-10-trees>` to the unit the environment resolves for
that leaf. Tag and resolved unit need not be identical, but only the **currency** is
converted: a tag in any registered currency is converted to the run currency at the
boundary. Every other axis must already agree — a tag period that disagrees with the
name's time suffix, a spelled grouping level that disagrees with the column's declared
level, or any other dimensional mismatch is a build error.

## Backward Compatibility

- **User code shape is unchanged.** Bare arrays and the DataFrame/mapper interface keep
  working; `currency` defaults to `"EUR"` and output stays in Euros.
- **`unit` is repurposed; `reference_period` and `reference_level` are removed.** `unit`
  becomes a compositional spelling. The period a flow used to record in
  `reference_period`, and the level a per-group amount used to record in
  `reference_level`, are now **folded into the unit string** (`EUR_PER_YEAR_PER_FG`), so
  there is a single source of truth and the two fields are gone.
- **No blanket opt-out.** There is no env-var escape hatch that switches the unit check
  off wholesale. Users can opt out for single expressions (`cast_unit`) or specific
  functions (`verify_units=False`, {ref}`see <gep-10-checks>`) or opt out of some checks
  by turning off GETTSIM's fail-if nodes.

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

Delivered as one infrastructure PR, with the framework proven on `METTSIM` — the
stylised Middle-Earth tax-and-transfer system that serves as TTSIM's test bed and
documentation example — before any German annotation:

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
