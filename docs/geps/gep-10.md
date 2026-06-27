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
meter, persons per Bedarfsgemeinschaft — declared on parameters, policy functions, and
(optionally) input data. The framework reads those units to do three things:

- **Dimensional safety.** It checks that the arithmetic combining quantities is sound,
  so mixing incompatible kinds — a monthly amount and a per-square-meter rent — becomes
  a loud error when the model is defined, not a silent wrong number far downstream.
- **Grouping-level safety.** A unit also records the **grouping level** a quantity
  belongs to — the individual, the household, the Bedarfsgemeinschaft, the tax unit.
  Levels are genuine dimensions with no fixed conversion between them, so combining a
  household-level amount with a Bedarfsgemeinschaft-level amount is caught the same way,
  while the per-capita conversions GETTSIM already performs (dividing a household total
  by a head count) type-check on their own.
- **Automatic unit conversion.** It converts compatible quantities to a common unit:
  parameters denominated in Deutsche Mark are converted to Euros at build time, and time
  conversions of flows work the same way. The existing `_y`/`_q`/`_m`/`_w`/`_d` and
  aggregation-level (`_hh`, `_bg`, …) suffix conventions are preserved.

A unit is written **compositionally** — a base optionally divided by an area, a period,
and a grouping level, spelled `CURRENCY_PER_MONTH_PER_BG` — so the vocabulary is read
off the spelling rather than memorised from a table of opaque tokens. The engine is
[pint](https://pint.readthedocs.io), and it runs **only while the model is built**: it
checks dimensions and converts units, then steps aside. The numeric runtime is
unchanged. As in {ref}`GEP 9 <gep-9>`, the checks fire at definition time, catching a
whole class of unit bugs before they can reach a result.

### Terminology

- **dimension** — the basic kind of a quantity: `[currency]`, `[time]`, `[area]`, the
  isolated working-hours dimension `[hours]`, the count dimension `[person]`, one
  **grouping-level** dimension per group identifier (`[hh]`, `[bg]`, …), or
  dimensionless. The grouping levels are not interconvertible: there is no fixed factor
  between a household and a Bedarfsgemeinschaft, so they are distinct base dimensions,
  not units of one shared dimension.
- **unit** — a particular way of measuring a dimension, such as Euros for `[currency]`
  or years for `[time]`. A unit carries a conversion factor to the dimension's base
  unit, so e.g. `1 month = 1/12 year`. Grouping-level dimensions are the exception: each
  has exactly one unit and no conversion partner.
- **compositional unit** — the way a declaration spells a unit: a **base** optionally
  divided by an **area**, a **period**, and a **grouping level**, in that canonical
  order, joined by `_PER_` — `CURRENCY_PER_SQUARE_METER_PER_MONTH_PER_BG`. A bare base
  (`DIMENSIONLESS`, `YEARS`) is a complete unit with no denominators
  ({ref}`grammar <gep-10-vocabulary>`).
- **flow** — a quantity per unit of time, marked by a **period** denominator
  (`CURRENCY_PER_MONTH`). A quantity with no period is a *stock*.
- **grouping level** — the entity a quantity is denominated per: per person, per
  household, per Bedarfsgemeinschaft. A leveled quantity carries its level as a
  **denominator** dimension (`CURRENCY_PER_MONTH_PER_HH` is a household monthly amount);
  a head count carries one level over another (`PERSON_PER_HH`, `[person] / [hh]`, is
  persons per household). The individual leaf level is **implied, never spelled**: a
  bare `CURRENCY_PER_MONTH` is a per-person amount.
- **index level vs. unit level** — a column's *index* level is pure data layout: which
  group it has one row per, recorded by the {ref}`GEP 1 <gep-1>` aggregation suffix and
  the {ref}`GEP 2 <gep-2>` `*_id` machinery. Its *unit* level is the dimensional
  denominator above. For aggregations the two are kept in sync (T8); for a
  non-aggregated intensive column they can diverge (an age compared to a universal
  threshold is level-less even at a group suffix).

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
   by `1.95583` by a maintainer before being written to YAML, with the original value
   preserved only in a free-text `note`. There is no machine-checkable provenance and no
   guard against a transcription error. This is both prone to errors and violates
   GETTSIM's law-to-code approach.

1. **Hand-written time arithmetic.** `ttsim/unit_converters.py` implements ~50
   conversion functions (`y_to_m`, `per_y_to_per_m`, …) and their stock/flow duals by
   hand. The resulting arithmetic has itself been a source of bugs.

**Scope.** The GEP covers `ttsim` (the framework) and `gettsim` (the German currencies
and the policy annotations). GEP 1's `_y`/`_q`/`_m`/`_w`/`_d` and aggregation-level
suffix automation is preserved; only the *arithmetic* behind the conversions, and the
*checking* of dimensions and levels, moves onto the unit engine.

(gep-10-vocabulary)=

## The unit vocabulary

A unit is **compositional**: a base optionally divided by denominators, in a fixed
canonical order, joined by `_PER_`:

```text
unit        := base ( "_PER_" denominator )*
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
  denominator is exactly what makes a unit a **flow**.
- **Canonical order, one per kind.** Denominators appear in the order
  `area · period · level`, at most one of each; a non-canonical spelling
  (`..._PER_BG_PER_MONTH`) or a repeat is rejected, so there is **exactly one spelling
  per unit**.
- **The person leaf is implied, never spelled.** The individual level is the default for
  every leveled quantity, so it is never written: a per-person monthly amount is
  `CURRENCY_PER_MONTH`, and `_PER_PERSON` is a build error. Only *group* levels are
  spelled (`CURRENCY_PER_MONTH_PER_HH`). See
  {ref}`the person-leaf convention <gep-10-convention>`.

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

The fluent builder spells the same units in `.py`, with autocomplete and the canonical
order enforced by the staged return types:

```python
Unit.CURRENCY.PER_MONTH.PER_BG  # -> "CURRENCY_PER_MONTH_PER_BG"
Unit.CURRENCY  # a stock, per person
Unit.PERSON.PER_BG  # a declared head count
Unit.DIMENSIONLESS  # a share, or a person-level boolean
Unit.DIMENSIONLESS.PER_FAM  # a fam-level boolean
Unit.HOURS.PER_WEEK
```

`Unit.CURRENCY` *is* `CompositeUnit(base="CURRENCY")`; `.PER_<area>` / `.PER_<period>`
are properties on small staged types, and `.PER_<level>` is added per build for each
registered grouping level. Only the ~6 bases and ~13 denominators are hand-written; the
cross product is reached by chaining (no code generation, no giant enum). YAML declares
the flat string parsed by the *same* core, so `.py` and YAML round-trip:
`str(Unit.CURRENCY.PER_MONTH.PER_BG) == "CURRENCY_PER_MONTH_PER_BG"`.

A special, but common, case is the currency dimension. GETTSIM supports two currencies:
Euros (EUR) and Deutsche Mark (DM). Policy functions are written to be currency-agnostic
— they run in either currency without change — so only parameters and input data carry a
concrete currency base ({ref}`Currency <gep-10-currency>`).

(gep-10-convention)=

## The person-leaf convention

One rule governs how a leveled quantity spells its level, everywhere — columns, policy
functions, parameters, schedule axes, and aggregations:

> **The person leaf is implied and never spelled; every group level is spelled.**

So a per-person amount is `CURRENCY_PER_MONTH`, a per-Bedarfsgemeinschaft amount is
`CURRENCY_PER_MONTH_PER_BG`, and `CURRENCY_PER_MONTH_PER_PERSON` is a build error. The
payoff is that there is exactly one spelling per unit, the common case is the short one,
and a level in a spelling is always a *group* level worth reading.

Which quantities carry a level at all is the **extensive/intensive** distinction
({ref}`below <gep-10-extensive>`), with booleans added in:

- **Leveled** — *extensive* bases (currency, area, the `[person]` count) and
  **booleans**. An unspelled level means the person leaf; a spelled level is a group.
- **Level-less** — *intensive* bases (durations, calendar points, plain `DIMENSIONLESS`
  shares and rates). No level, spelled or implied.

How the spelling is read differs only in where the period and level come from:

- **Columns and policy functions** spell their period and any group level, and the
  framework **validates them against the name suffix** ({ref}`GEP 1 <gep-1>`): a `_m`
  name must spell `..._PER_MONTH`, a `_hh` name must spell `..._PER_HH`, an unsuffixed
  name is at the person leaf. A `_hh`-named extensive column that fails to spell
  `_PER_HH` is rejected — the person leaf is the only level a column may leave implicit.
- **Parameters** have no name suffix, so they spell their period and group level in the
  unit string directly; the person leaf is still implied (a per-person threshold is
  `EUR_PER_YEAR`, a per-family one `EUR_PER_YEAR_PER_FAM`). A scalar parameter's *name*
  may carry a time suffix, which must agree with the spelled period.

## Usage and Impact

Every parameter and policy function carries a `unit=` declaration. The declaration on a
policy function is a guard rail: GETTSIM checks that the unit that falls out of the
function body — its physical dimension, its flow period, *and* its grouping level —
matches the declaration and the name suffixes, so a mismatch is a loud error at
definition time.

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

A per-person parameter spells its period and is level-less of any *group* — the person
leaf is implied:

```yaml
sparerfreibetrag_y:
  unit: EUR_PER_YEAR        # a yearly allowance "per person"; doubled per couple
  type: scalar
  2009-01-01:
    value: 801
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
- **`unit` is repurposed; `reference_period` and `reference_level` are removed.** `unit`
  becomes a compositional spelling. The period a flow used to record in
  `reference_period`, and the level a per-group amount used to record in
  `reference_level`, are now **folded into the unit string** (`EUR_PER_YEAR_PER_FAM`),
  so there is a single source of truth and the two fields are gone.
- **Head counts change dimension.** A `COUNT` aggregation now auto-assigns the count
  dimension (`[person] / [group]`) rather than `DIMENSIONLESS`. This is invisible to
  user code — counts are still integers at run time — but per-person parameters that
  scale a count are now `[person]`-aware ({ref}`Grouping levels <gep-10-levels>`).
- **Group-level booleans carry their level.** A `_fam` boolean is `1 / [fam]`, not a
  bare number, and is declared `DIMENSIONLESS_PER_FAM`
  ({ref}`Leveled booleans <gep-10-booleans>`). Run-time arrays are unaffected — a
  boolean is still `{0, 1}`.
- **No blanket opt-out.** As with the {ref}`GEP 9 <gep-9>` beartype claw, there is no
  env-var escape hatch that switches the unit check off wholesale. Users can opt out for
  specific functions (`verify_units=False`, {ref}`see below <gep-10-checks>`) or by
  turning off GETTSIM's fail-if nodes.

## Detailed Description

(gep-10-levels)=

### Grouping levels

GETTSIM data lives at grouping levels: the individual (the leaf, identified by `p_id`),
and one group per `*_id` column ({ref}`GEP 2 <gep-2>`) — in gettsim the household
(`hh`), the Familiengemeinschaft (`fg`), the Bedarfsgemeinschaft (`bg`), the tax unit
(`sn`), the Einsatzgemeinschaft (`eg`), the Ehegemeinschaft (`ehe`), and the
wohngeldrechtlicher Teilhaushalt (`wthh`). The framework discovers the levels from the
`*_id` columns of the policy environment and registers each as a base dimension; `ttsim`
ships no fixed list. The fluent builder learns a `PER_<level>` step for each.

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
is spelled in the unit string. Either way the person leaf is implied
({ref}`the convention <gep-10-convention>`), so `betrag_m` is
`CURRENCY / month / [person]` and `betrag_m_hh` is `CURRENCY / month / [hh]`.

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

A head count need not come from an aggregation. The `PERSON` base lets a parameter (a
cap on the number of family members considered), a hand-written function (a count
clamped to that cap), or a raw input column *declare* a head count: `PERSON_PER_FAM`
resolves to the identical `[person] / [fam]` a `COUNT` mints, so a declared cap and an
aggregated count compose and compare without an opt-out. A head count *per person* — the
persons an `agg_by_p_id` count attributes to one individual — is the bare `PERSON`:
`[person] / [person]` resolves (the person leaf implied) to a plain dimensionless
number, exactly what a count-per-individual is.

(gep-10-booleans)=

### Leveled booleans

A boolean is a *leveled* quantity: a truth value about an entity at some level. A
person-level indicator is `1 / [person]`, a family-level one `1 / [fam]`. Booleans
follow {ref}`the person-leaf convention <gep-10-convention>` like any leveled quantity —
a person boolean is bare `DIMENSIONLESS` (the leaf implied), a group boolean spells its
level, `DIMENSIONLESS_PER_FAM`. A node is recognised as a boolean by its `-> bool`
return type (orthogonal to its declared unit), and that is what distinguishes a boolean
from a plain dimensionless *share*: a share stays level-less, a boolean carries its
level.

This catches a class of wrong-level predicate bugs that level-less booleans let through.
A `_fam`-named predicate that actually compares *person*-level quantities infers
`1 / [person]`, which disagrees with its `_fam` suffix and is rejected — where before
the dimensionless result bypassed the suffix-level check entirely:

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

— and it is implemented in the dry-run's logical operators directly, rather than left to
pint's multiplicative algebra (which has a product, never the *meet* a per-person result
needs). A comparison of a leveled quantity against a scalar yields a boolean at that
level; `~` preserves the level.

(gep-10-hours)=

### Working hours are their own dimension

Working hours are a genuine dimension `[hours]`, registered as `working_hour` and
**isolated from pint's `[time]`**. This is deliberate: if working hours were based on
the `[time]` `hour`, then `hours / week` would be `[time] / [time]` and collapse to a
bare number — adding working hours to a share would not be caught, and an hours quantity
could not be told from a dimensionless one. With its own dimension, `HOURS_PER_WEEK` is
`[hours] / [time]`, distinct from both a share and a currency, so
`arbeitsstunden_w + anteil` is a dimension mismatch and fails.

`HOURS_PER_WEEK → HOURS_PER_MONTH` re-bases the **period** only (the existing
time-conversion machinery), leaving the `[hours]` numerator untouched. There is no
conversion between `[hours]` and `[time]`: `working_hour` has no `[time]` partner, so
`HOURS ↔ MONTHS` is impossible by construction. pint's own `hour` is left intact (the
calendar units depend on `day = 24 · hour`) but is not an admissible declaration token.

### Calendar points are distinct from durations

A year *on the calendar* — a birth year, the policy year — is an affine *point*, not a
*duration*. The two do not share arithmetic: subtracting two points gives a duration,
and shifting a point by a duration gives a point, but two points cannot be added and a
point cannot be scaled. The `CALENDAR_YEAR` / `CALENDAR_MONTH` / `CALENDAR_DAY` bases
carry the point on each axis (pint offset units); `YEARS` / `MONTHS` / `DAYS` carry the
corresponding duration. The dry-run enforces the algebra (the duration `D` of a point
`P`):

| operation                 | result    | example                              |
| ------------------------- | --------- | ------------------------------------ |
| `P − P`                   | duration  | `policy_year − geburtsjahr` → an age |
| `P ± D` (same axis)       | point     | `geburtsjahr + statutory_age`        |
| `P + P`, `P × n`, `P / n` | **error** | two calendar years cannot be added   |
| mixing calendar axes      | **error** | a year point plus a month duration   |

This is one of the cases where a quantity's kind decides whether an operation is
*allowed*, not just whether two units match (the others are mixing two grouping levels
and combining booleans across levels): the affine point and its duration have the same
dimension but obey different algebra. A *cyclic* ordinal — a month-of-year
(`geburtsmonat` 1–12), a day-of-week, a quarter — is **not** a calendar point but
`DIMENSIONLESS`: it is a recurring label, not a position on a running calendar.

(gep-10-extensive)=

#### Which quantities carry a level

Whether a base carries a level is the **extensive/intensive** distinction — a quantity
carries `/[level]` exactly when summing the level's members sums it meaningfully:

- **Carries its level** (extensive): `CURRENCY`, the `[person]` count, `SQUARE_METER` /
  `HECTARE`. A household income is the sum of its members' incomes; a dwelling's area
  divides by a head count to a per-capita area. **Booleans** carry a level too
  ({ref}`above <gep-10-booleans>`), though their base is dimensionless.
- **Level-less** (intensive): `YEARS` / `MONTHS` / `DAYS`, `CALENDAR_*`, `HOURS`, and a
  plain `DIMENSIONLESS` share or rate. Summing ages is meaningless; a rate or a per-m²
  cap is the same regardless of how many people it applies to. An intensive quantity is
  the multiplicative scalar that *scales* a leveled amount (`amount * share`), so it
  must carry no level of its own.

This keeps the per-capita bridges working (dwelling area divides by a head count just
like currency) while avoiding false positives on intensive quantities: an age limit is a
level-agnostic `YEARS`, so `alter < altersgrenze` is a plain duration comparison, not a
level mismatch.

The distinction anchors **base columns** (inputs) and **parameters**. **Derived columns
get their level from the algebra**, and an intensive-but-leveled result is normal: the
per-person rent share above is `CURRENCY / month / [person]` — intensive (you do not sum
per-capita shares), yet leveled, because the division *put* a `[person]` in the
denominator. Such a quantity has the *identical* unit to a genuinely extensive
person-level amount (an individual's own income is also `CURRENCY / month / [person]`);
the unit captures dimension, not extensive-vs-intensive provenance, and need not tell
the two apart.

(gep-10-index-vs-unit)=

#### Index level vs. unit level

A column's **index level** — which group it stores one row per — is pure data layout,
owned by the aggregation suffix and the {ref}`GEP 2 <gep-2>` `*_id` machinery. Its
**unit level** is the dimensional denominator above.

For **aggregations** the two are kept *in sync* (T8, {ref}`below <gep-10-auto>`): every
group aggregation resolves to the level its suffix names, so a `_fg` aggregate is
`…/[fg]` whatever the aggregation type — including a `MIN`-of-age, which acquires `[fg]`
rather than staying level-less. The suffix and the unit level agree by construction, and
an aggregation node and its auto-generated time-conversion variant cannot drift apart.

They can still **diverge** for a *non-aggregated* intensive column. A boolean or share
read at a group index but compared to universal quantities stays level-less; the suffix
then does a pure *index* job. The result check honours the split: **when an inferred
unit carries a level denominator it must equal the column's suffix level**; a level-less
result is exempt, its index-correctness being the structural system's concern. So
mis-naming the per-person rent share `bruttokaltmiete_m_hh` (inferred `…/[person]`,
suffix `[hh]`) is caught, while a level-less rate at a group suffix passes.

**Identifiers and pure shares are dimensionless** (`DIMENSIONLESS`), and therefore
level-less: an identifier (`p_id`, `*_id`, `p_id_*`) carries no dimension; a share
computed as `count / count` cancels its levels
(`anteil_kinder_hh = anzahl_kinder_hh / anzahl_personen_hh = ([person]/[hh]) / ([person]/[hh])`)
and is dimensionless by construction. A *boolean* is the exception that
{ref}`carries a level <gep-10-booleans>`.

**There are no exemptions** from declaring a unit — every active node has one. Most
nodes declare it directly. Derived nodes get one auto-assigned
({ref}`see below <gep-10-auto>`); framework-injected date nodes get theirs from the
framework (`policy_year` is a `CALENDAR_YEAR`). So `UNSET_UNIT` has a single meaning —
*no declaration was made* — which the mandatory-units check always reports as an error.

### pint runs at build time only

The foundational constraint is that pint never wraps a live array. A `pint.Quantity` is
not a JAX pytree and does not trace under `jit`; wrapping runtime columns would fight
both JAX and the GEP-9 `FloatColumn` vocabulary. Instead, pint is used in two build-time
roles:

- to compute conversion **factors** (time and currency), which are baked into the
  compiled workers as plain numeric constants; and
- to run the **dry-run** dimensionality check on representative `Quantity`s.

The numeric runtime path stays pure arrays, single currency, and JAX-safe. Time and the
isolated working hours are first-class pint dimensions here, and so are the grouping
levels: the level dimensions carry no conversion factor (there is nothing to convert),
only the algebra that catches mixing them. The suffix auto-generation and naming follow
the {ref}`GEP 1 <gep-1>` conventions.

(gep-10-currency)=

### Currency

Currencies live in the framework as a `[currency]` dimension, with concrete currencies
registered by downstream packages via
`register_currency(name, *, base=False, definition=None)`. GETTSIM registers `EUR`
(base) and `DM = EUR / 1.95583`. Registration does two things: it provides the
**conversion factors**, with pint as the single source of truth for the rate; and it
makes the upper-cased currency name a valid compositional **base** (`DM`,
`DM_PER_MONTH`, `DM_PER_SQUARE_METER_PER_MONTH`, `EUR_*`, …), so parameters can pin down
the concrete currency their numbers are written in.

**Agnostic and concrete bases.** The **currency-agnostic** base `CURRENCY` is a
placeholder for any registered currency: it declares the unit of a function or column
for which it does not matter which currency the model runs in. A **concrete currency**
base (`DM`, `EUR`) names one specific currency; what it adds over the agnostic base is
**denomination** — it names the currency a parameter's stored numbers are written in,
which the build-time conversion reads off the declaration. The level facet is orthogonal
to currency: both acquire their level from the convention just like everything else.

**Parameters must be concrete; functions must be agnostic.** A parameter's numbers are
written in *some* currency, so once a concrete currency is registered, an agnostic
`CURRENCY` base on a parameter is a build error — the declaration must name the
denomination (`EUR_PER_YEAR`, not `CURRENCY_PER_YEAR`). Columns and functions may *only*
declare the agnostic `CURRENCY`. A derived node — a time-conversion variant or an
aggregation of a concrete-currency parameter — inherits the **agnostic** counterpart, as
it computes on values already converted to the run currency.

**The run currency.** The `currency` argument to `main()` defaults to the registered
base currency; it is the currency the input data is taken to be in and that the outputs
come out in. At environment build, every currency-denominated *parameter* is converted
from its declared denomination to the run currency.

**A changeover within one parameter's history.** A dated entry may restate the unit
field, overriding the top-level declaration for that entry's numbers. This is how the
DM→Euro switch is written — entries before the reform denominated in the legacy
currency, entries from the reform date in the new one:

```yaml
arbeitnehmerpauschbetrag_y:
  unit: DM_PER_YEAR
  type: scalar
  1990-01-01:
    value: 2000
  2002-01-01:
    unit: EUR_PER_YEAR   # the changeover: denominated in Euro from here on
    value: 1044
```

`updates_previous` cannot cross a changeover: an entry that restates the unit must
restate the full value, because a merged value would mix numbers denominated in
different currencies.

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
the age bracket it applies to — is neither shape and is **split** into separate
homogeneous parameters (the amount as a currency parameter, the ages as a `YEARS`
parameter), each independently declarable and checkable. A homogeneous (single-`unit:`)
converter that is found to produce a function-like value is rejected at build time, with
the error pointing the author at the per-axis declaration.

### Parameters

A parameter spells its unit fully (period and group level), with the person leaf
implied. The shape of the `unit:` declaration follows the parameter `type:`:

**Scalar.** One token; the parameter's *name* may carry a time suffix, which must agree
with the spelled period (`lump_sum_deduction_y` declaring `EUR_PER_YEAR`).

**Dict with homogeneous leaves.** One token for the whole structure. Integer keys carry
no time suffix, so the period is spelled in the token:

```yaml
satz_nach_kindanzahl:
  unit: EUR_PER_MONTH       # one token; per person (leaf implied)
  type: dict
  2024-01-01:
    1: 250.0
    2: 250.0
```

**Dict with heterogeneous leaves.** `unit:` is a **mapping from leaf keys to tokens**. A
string-keyed flow leaf may take its period from the key's own time suffix; every leaf is
spelled (`DIMENSIONLESS` for a dimensionless leaf), nested mappings recurse:

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

(gep-10-checks)=

### Build-time checks and boundary conversion

The checks run in two layers, both at build time:

|        | **Layer 1 — DAG validity**                                        | **Layer 2 — boundary**                                                                                                                 |
| ------ | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| when   | `fail_if` on the assembled environment                            | where GEP-9 normalises user input into canonical arrays                                                                                |
| input  | none — synthetic `Quantity`s                                      | the user's unit-annotated input tree                                                                                                   |
| checks | inferred body unit vs. declaration; producer↔consumer edges agree | tag currency → run currency; period vs. suffix; level vs. suffix; unknown spelling rejected; every tag equivalent to its resolved unit |

#### Layer 1: the **dry-run** dimensionality check.

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
`EUR / month / [person]` — matching the declaration *and* the unsuffixed (person-level)
name.

**Broadcast changes the index, preserves the unit.** When a coarser-level input is used
in a finer-level body, the framework broadcasts it down — replicating the household's
value onto each member. The *index* becomes the finer level, but the *unit* level is
untouched: a broadcast `einkommen_m_hh` is still `CURRENCY / month / [hh]` on each
person's row. This is what makes grouping-level safety fall out for free.
`einkommen_m_hh − einkommen_m_bg`, even after both broadcast to persons, is
`CURRENCY/month/[hh] − CURRENCY/month/[bg]` → a dimension mismatch, while a *reconciled*
cross-level mix passes: `miete_m_hh * (anzahl_personen_wthh / anzahl_personen_hh)`
cancels `[hh]` against the count ratio and lands at `CURRENCY/month/[wthh]`.

**Every branch is covered, by re-running.** To evaluate `if befreit:` Python needs a
yes/no, but a unit stand-in has no value to compare. So the stand-in intercepts the
*truth test* itself (Python's `__bool__`) and hands it to a small driver — the **path
explorer** — that decides which way to go, re-running the body and steering the open
branches differently each time (a depth-first walk of the decision tree, in the style of
*concolic* execution) until every syntactically reachable branch combination is driven.
A body whose branching exceeds an internal cap is rejected (it must opt out), never
passed with some combinations left unchecked. Each run's result is checked on its own,
so a unit slip on a single arm is caught even though the other arms are clean. A
`return 0.0` arm yields a dimensionless result and falls back to the declaration, so the
ubiquitous `if befreit: return 0.0` guard never raises a false alarm.

**What the dry-run catches:**

- a body whose inferred unit disagrees with its declaration, on any reachable branch — a
  stock times a per-year rate labelled as a stock, a `_m` flow returned where `_y` is
  declared, or a `…/[person]` result on a `_hh` name;
- an addition or subtraction of two non-equivalent quantities — a monthly flow plus a
  yearly one (`betrag_m + freibetrag_y`), a stock plus a flow, working hours plus a
  share, **or two different grouping levels** (`einkommen_m_hh − einkommen_m_bg`). At
  run time the assembled DAG computes on bare arrays with no pint, so such a combination
  is unit-blind and silently wrong; the dry-run rejects it rather than letting pint's
  build-time auto-conversion of same-dimension operands paper over it;
- an ordering comparison (`<`, `<=`, `>`, `>=`) of two non-equivalent quantities, or of
  a quantity against a bare non-zero literal — the literal silently carries the
  quantity's unit, so promote the bound to a parameter (only `0` is allowed inline).
  Equality (`==`, `!=`) is deliberately **not** screened: it is the operator for
  sentinel and exact-marker tests — a person-pointer's no-link marker
  (`p_id_empfänger == -1`) or an exact-zero guard (`kindersatz_m == 0.0`) — where the
  literal is a deliberate marker, not a hidden dimensioned bound;
- a logical operator (`&`, `|`, `^`, `~`) applied to a non-boolean operand —
  `wealth & is_adult`, where `wealth` is a stock — and a cross-level boolean combination
  is resolved by the {ref}`combine rule <gep-10-booleans>` (downcast to person), not
  silently swallowed;
- a missing unit, and malformed declarations: a non-canonical or repeated denominator, a
  spelled person leaf (`_PER_PERSON`), a flow token without a period, a
  currency-agnostic base on a parameter, a group column or boolean that fails to spell
  its level, or a spelled level disagreeing with the name suffix.

**What it cannot catch:**

- **anything that reduces to dimensionless.** The check is *dimensional*, not
  *semantic*: two genuine `DIMENSIONLESS` shares are interchangeable, and a body whose
  result *infers* dimensionless (an early `return 0.0`, or arithmetic that cancels)
  falls back to the declaration. So the engine guarantees *dimensional* soundness, not
  that every quantity is the intended *kind*. (Working hours, now their own dimension,
  are no longer in this blind spot — `HOURS_PER_WEEK` does not collapse.)
- **grouping-level mixing among level-less quantities.** Two intensive non-aggregated
  quantities at different group indices are both level-less and combine without
  complaint. Level safety holds precisely for the leveled (currency, count, area,
  boolean) quantities, which is where the high-stakes mixing happens; enforcing it on
  level-less ones would require an index-level lint that would also flag the legitimate
  broadcasts GETTSIM relies on.

**A note on cross-level ratios.** A ratio of two extensive quantities at different
levels comes out as a *level-conversion* dimension, not bare `DIMENSIONLESS`: a person's
share of household income, `einkommen_m / einkommen_m_hh`, is
`(CURRENCY/[person]) / (CURRENCY/[hh]) = [hh] / [person]` — dimensionally "one over
persons-per-household", which is exactly what an equal-split share is. It multiplies
back cleanly (`[hh]/[person] · CURRENCY/[hh] = CURRENCY/[person]`), but a body that
declares such a share `DIMENSIONLESS` will be told its true unit; declare it for what it
is, or form it as a `count / count` ratio that cancels to dimensionless.

**A body the dry-run cannot evaluate must opt out explicitly.** The dry-run executes a
*scalar* body symbolically, so a body it cannot trace must opt out: vectorized functions
(`vectorization_strategy="not_required"`), piecewise polynomials and lookup tables,
bodies calling `join` or a raw `xnp` op, bodies returning an opaque value, and the
genuine cross-level bodies that T8 no longer special-cases (comparing a group `MAX` back
against a person value). Rather than silently trusting such a body, the check
**rejects** it unless the author marks it `verify_units=False`. The opt-out is of body
*inference only*: the declared output unit still stands, so every *consumer* of this
node is still checked against it, and the units flowing *into* the body are themselves
verified producer outputs.

#### Layer 2: the **boundary check** on the unit-annotated input tree.

**Layer 2** is offered through the unit-annotated input tree (a sibling of the ordinary
input tree in which every leaf is a pint `Quantity`). When the mode is used **every**
leaf must be tagged, including identifiers and other dimensionless columns (tagged
`dimensionless`). The boundary check compares each tagged input to the unit the
environment resolves for that leaf. Three axes are verified elsewhere and so are divided
out first: currency (by the strip path), a flow's reference period, and the grouping
level (the latter two owned by the suffix guard). What remains is the physical dimension
— so a same-dimension error, such as a `HECTARE` column tagged `m²` or a `YEARS` input
tagged in months, is rejected rather than silently mis-scaled. It feeds no node, so it
adds no back-edge to the boundary and needs no declared unit threaded through
`processed_data`. Symmetrically, the **unit-annotated result tree** relabels each output
leaf with its precise run-currency unit (`euro/month`, not the agnostic `CURRENCY`) —
pure naming, since results are already computed in the run currency.

(gep-10-auto)=

### Auto-generated nodes

Auto-generated nodes receive auto-assigned units. Time-conversion variants inherit the
source's base and re-base the period off the variant's own suffix
(`CURRENCY_PER_MONTH → CURRENCY_PER_YEAR`). Auto-aggregations derive their unit from the
source and the aggregation type, paralleling how {ref}`GEP 4 <gep-4>` resolves their
types — and, with grouping levels in the unit, the aggregation is where a level is
minted, swapped, or acquired:

| aggregation                    | physical base   | level (T8)                                                             |
| ------------------------------ | --------------- | ---------------------------------------------------------------------- |
| `SUM` / `MEAN` / `MIN` / `MAX` | preserved       | **target** level — source level swapped, level-less source acquires it |
| `COUNT`, `SUM` over a boolean  | `[person]`      | **minted** `[person] / [target]` (a head count)                        |
| `ANY` / `ALL`                  | `DIMENSIONLESS` | boolean **at the target level** (`1 / [target]`)                       |

**T8 — group aggregations resolve to their target level.** All of
`SUM`/`MEAN`/`MIN`/`MAX` resolve to the level the node's suffix names: the source's own
level (if any) is swapped for the target, and a level-less source *acquires* it. So a
`SUM` of person incomes to the household gives `CURRENCY/month/[hh]`, and a `MIN` over
level-less ages to the Familiengemeinschaft gives `MONTHS/[fg]` (not level-less
`MONTHS`). This keeps a column's `_xx` suffix and its unit level always in sync on an
aggregation result, and makes an aggregation node agree by construction with its own
auto-generated time-conversion variant. The few genuine cross-level bodies this no
longer special-cases — comparing a group `MAX` back against a person value — opt out
locally with `verify_units=False`.

A **head count** — `COUNT`, *or* a `SUM` over a *boolean* (a per-person indicator, so
its sum counts the persons it is true for) — mints `[person]/[target]`; the two are the
same kind of quantity and must agree, so `anzahl_erwachsene_bg` reached by `COUNT` and
by summing an `ist_erwachsen` flag carry the identical `[person]/[bg]` — the same unit a
`PERSON_PER_BG` declaration resolves to. `ANY`/`ALL` yield a *boolean* (not a count) at
the target level: bare `DIMENSIONLESS` for an individual result,
`DIMENSIONLESS_PER_<target>` for a group one. A `@group_creation_function` group id is
auto-assigned `DIMENSIONLESS` (an identifier). Where the source pins down a concrete
currency (a parameter), the derived node inherits the **agnostic** counterpart.

A hand-written aggregation also carries an author-declared unit (one is required to pass
the mandatory-units check), and that declaration is **checked against the derived
unit**, the same declared-vs-produced contract a `@policy_function` body is held to: its
physical *kind* — currency, the `[person]` count, area, a duration — must match what the
aggregation produces, so a `SUM` over a boolean declared `DIMENSIONLESS` rather than
`PERSON_PER_BG` is rejected.

### Literals

The dry-run executes a body on representative `Quantity`s, so a bare numeric literal
combined *additively* with a unit-carrying value raises (pint refuses to add a
dimensionless number to a currency). A literal that is only a multiplicative factor
(`betrag * 0.5`) is fine — multiplying by a dimensionless number preserves the unit.

Most apparent cases dissolve once the quantities are declared correctly: an ordinal such
as `geburtsmonat` (the month 1–12) is `DIMENSIONLESS`, so `geburtsmonat - 1` is
dimensionless arithmetic and needs no tag. For a genuine constant of a real dimension,
either **promote it to a parameter** (the norm — it then gets the same provenance,
currency conversion, level, and checking as any other parameter, and the body becomes
dry-runnable), or **opt the body out** with `@policy_function(verify_units=False)` for
genuine code-level constants where a parameter would be artificial.

Promotion means the constant moves into a YAML parameter file (as any other parameter,
{ref}`GEP 3 <gep-3>`) and the function gains it as an argument — not a Python-level
declaration. An inline bound is rejected because the literal silently inherits the
operand's unit:

```python
@policy_function(unit=Unit.DIMENSIONLESS)
def anspruchsberechtigt(einkommen_m: float) -> bool:
    return einkommen_m < 1000.0  # 1000.0 silently carries EUR/month → rejected
```

Promoting the bound to a parameter makes the body dry-runnable, with no opt-out:

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

Delivered as a stacked set of PRs, with the framework proven on `mettsim` before any
German annotation. The compositional vocabulary, the `[hours]` dimension, leveled
booleans, and the T8 aggregation rule are surface and model changes over a shared pint
core; the dimensional resolution, conversion factors, dry-run algebra, and input/output
boundary are reused throughout. The ttsim delivery stack is:

- ttsim [#138](https://github.com/ttsim-dev/ttsim/pull/138) — dimensional core (the pint
  registry, the full dimension model: time, currency, the `[hours]` dimension,
  **grouping levels and the `[person]` count**, mandatory units + edge-consistency)
- ttsim [#139](https://github.com/ttsim-dev/ttsim/pull/139) — currency knob + Layer-2
  boundary conversion
- ttsim [#140](https://github.com/ttsim-dev/ttsim/pull/140) — compositional units + the
  T8 aggregation-level rule
- ttsim [#141](https://github.com/ttsim-dev/ttsim/pull/141) — annotate `mettsim`
  end-to-end (the worked example), switch the check on, CI test over all dates

The gettsim rollout is tracked by issues
[#1191](https://github.com/ttsim-dev/gettsim/issues/1191) (register EUR/DM currencies)
and [#1192](https://github.com/ttsim-dev/gettsim/issues/1192) (annotate everything,
switch the check on); the implementation PRs are not yet open.

Each package's params schema validates the compositional spelling (a coarse
`^[A-Z][A-Z0-9_]*$` pattern, with `parse_compositional_unit` enforcing the grammar at
load time) and enforces, per parameter `type:`, the `unit:` XOR
`input_unit:`/`output_unit:` split, the shape of the declaration (a `type: scalar`
`unit:` is a single token; the leaf-keys mapping form is admitted only for
`type: dict`), and the concrete-currency rule for parameters. The schema shipped with
ttsim (listing mettsim's `SILVER_PENNY`/`CASTAR` currencies and Middle-Earth levels) is
the template; the copy at `docs/geps/params-schema.json` is migrated together with the
YAML files in #1192.

## Alternatives

### Counting quantities as plain `DIMENSIONLESS`

Rejected — this was an earlier draft of this GEP. Treating head counts as
`DIMENSIONLESS` follows SI and pint convention and needs no `[person]` dimension, but it
throws away the grouping-level information that makes the per-capita conversions
checkable: a count is then indistinguishable from a share,
`wohnen__bruttokaltmiete_m_hh / anzahl_personen_hh` infers a bare currency rather than a
per-person amount, and a household total cannot be told from a Bedarfsgemeinschaft
total. Adopting `[person]` (the count dimension) and the grouping-level dimensions is
what turns the cross-level bodies GETTSIM already writes into self-checking arithmetic.

### Grouping levels on every dimensionless quantity

Rejected — but the line is drawn between **booleans** and **shares**. The temptation is
to give *every* dimensionless quantity a level, so that a family-level share reads as
dimensionally distinct from a person-level one. This fails on shares: a family's share
of household income is a pure number, yet the level algebra leaves a residual,

```text
anteil_fam = einkommen_m_fam / einkommen_m_hh
  = (CURRENCY / month / [fam]) / (CURRENCY / month / [hh])
  = [hh] / [fam]      # currency and period cancel; the levels do not
```

— the name says `_fam`, the algebra says `[hh]/[fam]`, the truth is "no level, it is a
ratio", and no single declaration satisfies all three. So a plain `DIMENSIONLESS` share
stays level-less. A **boolean** is different: it is not formed by dividing two
extensives, it is a truth value *about an entity at a level*, and the operation that
combines two of them is not pint's product but the {ref}`combine rule <gep-10-booleans>`
(the conservative *meet*, downcasting to person). That is why booleans carry a level and
shares do not — and the `-> bool` return type is what tells the framework which it is
looking at.

### Spelling the person leaf

Rejected. The person leaf could be spelled (`CURRENCY_PER_MONTH_PER_PERSON`) for full
symmetry with group levels. But then two spellings would denote the same unit (the bare
and the `_PER_PERSON` form), violating the one-spelling-per-unit invariant, and the
common case — a per-person amount — would carry the noisiest spelling. Implying the leaf
and rejecting `_PER_PERSON` keeps one canonical spelling and the short form for the
common case; only group levels, which genuinely vary, are spelled.

### A single generic `[count]` dimension with no level

Rejected. An intermediate design promoted counts to one generic `[count]` and per-person
parameters to `CURRENCY / count`, with no grouping level. It is weaker than the adopted
model on both ends: a single `[count]` cannot say *which* group a count is over, so
`anzahl_personen_hh` and `anzahl_personen_bg` are interchangeable and a cross-level mix
still type-checks; and `CURRENCY / count` reads where the law says "Euros per month".
The adopted model fixes both: `[person]` is the *one* count dimension (children and
adults are persons, so they share it and remain addable), the *group* it counts within
rides in the denominator (`[person]/[hh]` ≠ `[person]/[bg]`), and a per-person amount
stays plain `EUR_PER_MONTH`.

### Opaque single-word tokens

Rejected — the predecessor of the compositional spelling. A fixed enum of tokens
(`CURRENCY_FLOW`, `HEADCOUNT`, `CURRENCY_PER_SQUARE_METER_FLOW`, `DIMENSIONLESS_FLOW`)
plus split `reference_period` / `reference_level` side-fields meant a reader memorised a
table and the period/level lived in two places. The compositional grammar dissolves the
special tokens into spelling (`PERSON_PER_BG`, `CURRENCY_PER_SQUARE_METER_PER_MONTH`,
`DIMENSIONLESS_PER_YEAR`) and folds the side-fields into the one unit string, leaving a
single source of truth read off the spelling.

### Flat tokens with a generated `.pyi` stub

Considered, as an alternative to the fluent builder: a flat token surface identical in
`.py` and YAML, with a generated stub for autocomplete. Rejected in favour of the fluent
builder, which needs no generated file to maintain and enforces the canonical order
through its staged return types; the flat string remains the YAML and display form, and
the two round-trip.

### Grouping levels as a separate, non-unit tag

Considered. The level could be tracked beside the pint unit rather than inside it, as
the column's index level already is ({ref}`GEP 2 <gep-2>`). Rejected because the payoff
— head counts and per-capita divisions that type-check, cross-level additions that fail
— comes precisely from the level participating in pint's own dimensional algebra. A
separate tag would re-implement that algebra and could not make
`(CURRENCY/[hh]) / ([person]/[hh])` cancel to `CURRENCY/[person]` for free. The index
level stays a structural tag; the unit level is a pint dimension.

### Runtime pint Quantities flowing through the DAG

Rejected. `Quantity` is not a JAX pytree, breaks tracing, contradicts the GEP-9 column
vocabulary, and adds hot-path cost. Units in a tax-transfer model are static structural
properties of nodes, not of data, so runtime wrapping buys nothing the build-time check
does not already provide.

### Keep hand-written time conversions; use pint only for checks

Possible, but the stock/flow duality is exactly what a unit engine encodes for free.
Sourcing the factors from pint removes a class of hand-maintained arithmetic without
touching the naming.

### Make functions time-agnostic

Rejected. Collapsing `betrag_m` and `betrag_y` into one node would erase the law-to-code
correspondence GEP 1 is built on.

## References and Footnotes

- [gettsim #1174 (the originating DM-values discussion)](https://github.com/ttsim-dev/gettsim/issues/1174)
- [pint](https://pint.readthedocs.io)
- [NEP 18 (NumPy `__array_function__`)](https://numpy.org/neps/nep-0018-array-function-protocol.html)

## Copyright

This document has been placed in the public domain.
