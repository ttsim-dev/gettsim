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
meter, persons per household — declared on parameters, policy functions, and
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

The engine is [pint](https://pint.readthedocs.io), and it runs **only while the model is
built**: it checks dimensions and converts units, then steps aside. The numeric runtime
is unchanged. As in {ref}`GEP 9 <gep-9>`, the checks fire at definition time, catching a
whole class of unit bugs before they can reach a result.

### Terminology

- **dimension** — the basic kind of a quantity: `[currency]`, `[time]`, `[area]`, the
  count dimension `[person]`, or one **grouping-level** dimension per group identifier
  (`[hh]`, `[bg]`, …), or dimensionless. The seven group levels are not
  interconvertible: there is no fixed factor between a household and a
  Bedarfsgemeinschaft, so they are distinct base dimensions, not units of one shared
  dimension.
- **unit** — a particular way of measuring a dimension, such as Euros for `[currency]`
  or years for `[time]`. A unit carries a conversion factor to the dimension's base
  unit, so e.g. `1 month = 1/12 year`. Group-level dimensions are the exception: each
  has exactly one unit and no conversion partner.
- **grouping level** — the entity a quantity is denominated per: per person, per
  household, per Bedarfsgemeinschaft. A leveled quantity carries its level as a
  **denominator** dimension (`CURRENCY / month / [hh]` is a household monthly amount); a
  head count carries one level over another (`[person] / [hh]` is persons per
  household).
- **index level vs. unit level** — a column's *index* level is pure data layout: which
  group it has one row per, recorded by the {ref}`GEP 1 <gep-1>` aggregation suffix and
  the {ref}`GEP 2 <gep-2>` `*_id` machinery. Its *unit* level is the dimensional
  denominator above. The two usually coincide, but diverge for intensive aggregates (the
  youngest member's age is fg-*indexed* but level-less in its *unit*).

## Motivation and Scope

Four long-standing problems motivate this GEP.

1. **No dimensional safety.** The DAG carries quantities of many kinds, but a function
   body may add, subtract, or compare them freely. `betrag_m + miete_pro_qm_m` (a
   monthly amount plus a monthly rent *per square meter*) is a bug that runs silently
   today and surfaces, if at all, as an implausible number far downstream.

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

## The available units

Every quantity in GETTSIM is declared as one of a small, fixed set of **unit tokens**,
and the framework completes that token with two facts it reads off the quantity's name
or declaration: a **flow period** (per month, per year) and a **grouping level** (per
person, per household). The token names the physical kind; the period and the level are
orthogonal facets layered on top.

A special, but common, case is the currency dimension. GETTSIM supports two currencies:
Euros (EUR) and Deutsche Mark (DM). Policy functions are written to be currency-agnostic
— they run in either currency without change — so only parameters and input data carry a
concrete currency declaration.

Policy functions and columns declare their unit as one of the **agnostic tokens**:

- **`CURRENCY`** is a *stock* — an amount of money at a point in time, such as wealth or
  an asset threshold.
- **`CURRENCY_FLOW`** is a *flow* — an amount of money per unit of time. The period (per
  month, per year, …) is read off the {ref}`GEP 1 <gep-1>` name suffix (`_m`, `_y`, …),
  and the grouping level off the aggregation suffix (`_hh`, `_bg`, …): a `betrag_m`
  resolves to `CURRENCY / month / [person]`, a `betrag_m_hh` to
  `CURRENCY / month / [hh]`.

Parameters, which record a legal amount in a specific historical currency, instead use
the *concrete* currency tokens `EUR` / `EUR_FLOW` and `DM` / `DM_FLOW`.

The remaining tokens cover the other dimensions GETTSIM needs:

| token                                               | measures                                                |
| --------------------------------------------------- | ------------------------------------------------------- |
| `DIMENSIONLESS`                                     | shares, rates, booleans, identifiers                    |
| `DIMENSIONLESS_FLOW`                                | a pure number per period (change of Zugangsfaktor p.a.) |
| `YEARS` / `MONTHS` / `DAYS`                         | *durations*: an age, a number of years/months/days      |
| `CALENDAR_YEAR` / `CALENDAR_MONTH` / `CALENDAR_DAY` | *calendar points*: a birth year, the policy date        |
| `HOURS_FLOW`                                        | working hours per period                                |
| `SQUARE_METERS`                                     | dwelling size                                           |
| `CURRENCY_PER_SQUARE_METER_FLOW`                    | rent caps                                               |
| `HEADCOUNT`                                         | a *declared* head count: persons per reference level    |

Head counts are **not** dimensionless. A count of persons is the count dimension
`[person]`; aggregated to a group it is persons-over-group (`[person] / [hh]`). This is
the change that makes the per-capita conversions GETTSIM already performs type-check,
and it is spelled out in the {ref}`vocabulary <gep-10-vocabulary>` below. A `COUNT`
aggregation *mints* this unit; the `HEADCOUNT` token lets a parameter, a hand-written
function, or an input column *declare* the very same `[person] / [level]` directly.

A *calendar point* (a year/month/day **on** the calendar) is distinct from a *duration*
(a number of years/months/days): the difference of two calendar points is a duration
(`policy_year - geburtsjahr` is an age in `YEARS`), but two calendar points cannot be
added. The {ref}`vocabulary <gep-10-vocabulary>` spells out the algebra.

## Usage and Impact

Every parameter and policy function carries a `unit=` declaration. The declaration on a
policy function is a guard rail: GETTSIM checks that the unit that falls out of the
function body — its physical dimension, its flow period, *and* its grouping level —
matches the declaration and the name suffixes, so a mismatch is a loud error at
definition time.

```python
@policy_function(unit=Unit.CURRENCY_FLOW)  # betrag_m_bg -> CURRENCY / month / [bg]
def betrag_m_bg(regelsatz_m_bg: float, mehrbedarf_m_bg: float) -> float:
    return regelsatz_m_bg + mehrbedarf_m_bg


@policy_function(unit=Unit.CURRENCY)  # a stock; a time suffix would be an error
def vermögen(aktien: float, immobilien: float) -> float:
    return aktien + immobilien
```

A per-person parameter records the level it is denominated per through a
`reference_level:` field, the grouping-level counterpart of `reference_period:`:

```yaml
sparerfreibetrag:
  unit: EUR_FLOW
  reference_period: Year
  reference_level: person   # an allowance "per person"; doubled per couple
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
- **The `unit`/`reference_period` metadata is repurposed, and `reference_level` is
  new.** `unit` becomes one member of the token vocabulary; `reference_period` becomes
  *functional* — it supplies the period for structured flow parameters that cannot read
  a name suffix ({ref}`Flow tokens <gep-10-periods>`); and `reference_level` is a new,
  optional field naming the grouping level a parameter is denominated per
  ({ref}`Grouping levels <gep-10-levels>`). Its default is *level-agnostic*, so a
  parameter that needs no level (a rate) is unaffected.
- **Head counts change dimension.** A `COUNT` aggregation now auto-assigns the count
  dimension (`[person] / [group]`) rather than `DIMENSIONLESS`. This is invisible to
  user code — counts are still integers at run time — but per-person parameters that
  scale a count must declare `reference_level: person` for the multiplication to
  type-check ({ref}`Grouping levels <gep-10-levels>`).
- **No blanket opt-out.** As with the {ref}`GEP 9 <gep-9>` beartype claw, there is no
  env-var escape hatch that switches the unit check off wholesale. Users can opt out for
  specific functions (`verify_units=False`, {ref}`see below <gep-10-checks>`) or by
  turning off GETTSIM's fail-if nodes.

## Detailed Description

(gep-10-vocabulary)=

### The unit vocabulary

A declaration is one member of the **token vocabulary**. Its backbone is a closed core
enumeration — a `Unit` `StrEnum` shipped by `ttsim`, spelled identically in code (e.g.
`unit=Unit.HOURS_FLOW`) and in YAML (e.g. `unit: HOURS_FLOW`):

| token                                               | resolves to                                   | typical use               |
| --------------------------------------------------- | --------------------------------------------- | ------------------------- |
| `CURRENCY_FLOW`                                     | `CURRENCY / period / [level]`                 | wages, claims, benefits   |
| `CURRENCY`                                          | `CURRENCY / [level]`                          | wealth, asset thresholds  |
| `DIMENSIONLESS`                                     | `dimensionless`                               | shares, rates, booleans   |
| `DIMENSIONLESS_FLOW`                                | `1 / period`                                  | Zugangsfaktor per year    |
| `YEARS` / `MONTHS` / `DAYS`                         | a duration in `year`/`month`/`day`            | an age, a span            |
| `CALENDAR_YEAR` / `CALENDAR_MONTH` / `CALENDAR_DAY` | a calendar point                              | a birth year, policy date |
| `HOURS_FLOW`                                        | `hour / period` (dimensionless physical part) | working hours             |
| `SQUARE_METERS`                                     | `meter ** 2 / [level]`                        | dwelling size             |
| `CURRENCY_PER_SQUARE_METER_FLOW`                    | `CURRENCY / meter ** 2 / period`              | rent caps                 |
| `HEADCOUNT`                                         | `[person] / [level]`                          | a declared head count     |

Tokens are not pint syntax: each resolves internally to a pint unit (flow tokens after
the period is filled in, leveled tokens after the level is filled in), but pint
expressions never appear in a declaration. The `[level]` shown for the leveled tokens is
supplied separately, as {ref}`the next section <gep-10-levels>` describes; for a token
that does not carry a level (the durations, calendar points, dimensionless quantities,
and the per-area rate) the `[level]` slot is simply absent.

`HOURS_FLOW` is the one flow token whose *physical* part resolves to a *dimensionless*
quantity: hours and the period are both `[time]`, so hours per week is a time-over-time
ratio. It is kept as a distinct token so the time-suffix and time-conversion bookkeeping
still apply to working hours, but its physical part cannot be told apart from a bare
`DIMENSIONLESS` quantity. Likewise, a *per-period* dimensionless quantity is
`DIMENSIONLESS_FLOW`, not `DIMENSIONLESS`: the pension Zugangsfaktor moves by a fixed
factor per year of earlier or later retirement (`zugangsfaktor_veränderung_y`, § 77 SGB
VI) — a pure number, but *per year* it is `1/year`, and multiplied by the gap in `YEARS`
the years cancel to the dimensionless adjustment.

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

This is one of two cases where a quantity's token decides whether an operation is
*allowed*, not just whether two units match (the other is mixing two grouping levels):
the affine point and its duration have the same dimension but obey different algebra. A
*cyclic* ordinal — a month-of-year (`geburtsmonat` 1-12), a day-of-week, a quarter — is
**not** a calendar point but `DIMENSIONLESS`: it is a recurring label, not a position on
a running calendar.

(gep-10-levels)=

### Grouping levels

GETTSIM data lives at grouping levels: the individual (the leaf, identified by `p_id`),
and one group per `*_id` column ({ref}`GEP 2 <gep-2>`) — in gettsim the household
(`hh`), the Familiengemeinschaft (`fg`), the Bedarfsgemeinschaft (`bg`), the tax unit
(`sn`), the Einsatzgemeinschaft (`eg`), the Ehegemeinschaft (`ehe`), and the
wohngeldrechtlicher Teilhaushalt (`wthh`). The framework discovers the levels from the
`*_id` columns of the policy environment; `ttsim` ships no fixed list.

**Each level is a base dimension.** There is no fixed conversion between a person and a
household — a household holds a *variable* number of persons — so the levels are not
units of one shared dimension (the way `month` and `year` are units of `[time]`) but
distinct, non-interconvertible base dimensions: `[person]`, `[hh]`, `[bg]`, and so on.
The individual level `[person]` doubles as the **count dimension**: counting persons and
denominating something per person are the same `[person]`, which is what lets head
counts and per-person amounts cancel cleanly (below).

**A level is a denominator, supplied by the aggregation suffix.** A leveled quantity
carries its level as a denominator, exactly as a flow carries its period as one. The
aggregation suffix names it: an unsuffixed name is at `[person]`, a `_hh` name at
`[hh]`. So `betrag_m` resolves to `CURRENCY / month / [person]` and `betrag_m_hh` to
`CURRENCY / month / [hh]`. The author writes only `unit=Unit.CURRENCY_FLOW`; the period
and the level are read off the name.

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
einnahmen__kapitalerträge_y_sn − familie__anzahl_personen_sn * sparerfreibetrag
  = CURRENCY / year / [sn] − ([person] / [sn]) · (CURRENCY / year / [person])
  = CURRENCY / year / [sn] − CURRENCY / year / [sn]      # the count bridges person → sn
```

The head count is the conversion factor between levels, and these cross-level bodies —
the per-capita divisions and the multiply-by-count splittings GETTSIM already performs —
type-check on their own once counts carry `[person]` and per-person parameters carry
`reference_level: person`. `ANY`/`ALL`/booleans stay `DIMENSIONLESS`: they are not
counts.

A head count need not come from an aggregation. The `HEADCOUNT` token lets a parameter
(a cap on the number of family members considered), a hand-written function (a count
clamped to that cap), or a raw input column *declare* a head count, resolving to the
identical `[person] / [target]` a `COUNT` mints — so a declared cap and an aggregated
count compose and compare without an opt-out. A head count is always persons per
*something*: the reference level is mandatory (a `HEADCOUNT` parameter sets
`reference_level`; a `HEADCOUNT` column reads it from the name position). The individual
level is allowed and meaningful — a count *per person* (the persons an `agg_by_p_id`
count attributes to one individual) is `[person] / [person]`, which *is* a plain
dimensionless number — but it must be stated, not left bare.

(gep-10-extensive)=

#### Which quantities carry a level

Not every quantity has a level. Whether a token carries one is the
**extensive/intensive** distinction — a quantity carries `/[level]` exactly when summing
the level's members sums it meaningfully — and it is a per-token **default**,
overridable on a single declaration:

- **Carries its level** (extensive): `CURRENCY` / `CURRENCY_FLOW`, the `[person]` count,
  `SQUARE_METERS` / `HECTARES`. A household income is the sum of its members' incomes; a
  dwelling's area divides by a head count to a per-capita area.
- **Level-less** (intensive): `YEARS` / `MONTHS` / `DAYS`, `CALENDAR_*`,
  `DIMENSIONLESS(_FLOW)`, `HOURS_FLOW`, `CURRENCY_PER_SQUARE_METER_FLOW`. Summing ages
  is meaningless; a rate or a per-m² cap is the same regardless of how many people it
  applies to. Tokens whose physical part is already dimensionless (`HOURS_FLOW`,
  `DIMENSIONLESS(_FLOW)`) stay level-less by necessity — a level on a dimensionless base
  would make it a bare inverse-level and break comparisons against plain numbers
  (`arbeitsstunden_w > 15`).

This default keeps the per-capita bridges working (dwelling area divides by a head count
just like currency) while avoiding false positives on intensive quantities: an age limit
is a level-agnostic `YEARS`, so `alter < altersgrenze` is a plain duration comparison,
not a level mismatch. Where a token's default is wrong for one column — a working-hours
*total* versus an hours *rate* — an explicit per-declaration override flips it.

The distinction is a heuristic for anchoring **base columns** (inputs) and
**parameters** only. **Derived columns get their level from the algebra**, and an
intensive-but-leveled result is normal and falls out automatically: the per-person rent
share above is `CURRENCY / month / [person]` — intensive (you do not sum people's
per-capita shares), yet leveled, because the division *put* a `[person]` in the
denominator. Such a quantity has the *identical* unit to a genuinely extensive
person-level amount (an individual's own income is also `CURRENCY / month / [person]`);
the unit captures dimension, not extensive-vs- intensive provenance, and need not tell
the two apart.

(gep-10-index-vs-unit)=

#### Index level vs. unit level

A column's **index level** — which group it stores one row per — is pure data layout,
owned by the aggregation suffix and the {ref}`GEP 2 <gep-2>` `*_id` machinery. Its
**unit level** is the dimensional denominator above. For extensive quantities the two
coincide (a household total is hh-indexed and `…/[hh]`-leveled). They **diverge** for an
intensive quantity aggregated to a group: `alter_monate_jüngstes_mitglied_fg` — the
youngest member's age, a `MIN` over the Familiengemeinschaft — is fg-*indexed* (one row
per fg) but its unit is level-less `MONTHS`, because age is level-less throughout (it is
compared to universal age limits) and `MIN` invents no level. The `_fg` suffix still
does its index job; the unit simply has no level to carry.

The check honours the split: **when an inferred unit carries a level-denominator, it
must equal the column's suffix level**; a level-less result is exempt, its
index-correctness being the structural system's concern. So mis-naming the per-person
rent share `bruttokaltmiete_m_hh` (inferred `…/[person]`, suffix `[hh]`) is caught,
while the level-less min-age at `_fg` passes.

**Booleans, identifiers, and pure shares are dimensionless** (`DIMENSIONLESS`), and
therefore level-less: a boolean is a `{0, 1}` value; an identifier (`p_id`, `*_id`,
`p_id_*`) carries no dimension; a share computed as `count / count` cancels its levels
(`anteil_kinder_hh = anzahl_kinder_hh / anzahl_personen_hh = ([person]/[hh]) / ([person]/[hh])`)
and is dimensionless by construction.

**There are no exemptions** from declaring a unit — every active node has one. Most
nodes declare it directly. Derived nodes get one auto-assigned
({ref}`see below <gep-10-auto>`); framework-injected date nodes get theirs from the
framework (`policy_year` is a `CALENDAR_YEAR`). So `UNSET_UNIT` has a single meaning —
*no declaration was made* — which the mandatory-units check always reports as an error.

Beyond the core enumeration, the full vocabulary adds one set of **concrete currency
tokens** per registered currency ({ref}`see Currency <gep-10-currency>`). The core
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
first-class pint dimension here, and so are the grouping levels: the level dimensions
carry no conversion factor (there is nothing to convert), only the algebra that catches
mixing them. The suffix auto-generation and naming follow the {ref}`GEP 1 <gep-1>`
conventions.

(gep-10-periods)=

### Flow tokens and the level facet

A flow token needs a reference period, and a leveled token needs a grouping level. Both
are read off the name suffix for single values, with a declaration fallback for the
structured values that have no name to suffix:

| what you declare                                         | period from                  | level from              |
| -------------------------------------------------------- | ---------------------------- | ----------------------- |
| single value — column, policy function, scalar parameter | name suffix `_y/_q/_m/_w/_d` | name suffix `_hh/_bg/…` |
| structured value — dict, schedule, lookup table          | `reference_period`           | `reference_level`       |

Where the **time** suffix supplies the period it is *mandatory and exclusive*: a time
suffix requires a `…_FLOW` token and a `…_FLOW` token requires a time suffix, so a
non-flow token on a suffixed name — or a flow token on an unsuffixed one — fails at
build. This makes the {ref}`GEP 1 <gep-1>` convention machine-checked.

The **aggregation** suffix is *not* symmetric in the same way, because of the
index-vs-unit split ({ref}`above <gep-10-index-vs-unit>`): an aggregation suffix records
the index level and *may* but need not imply a unit level. A `_fg` name may be a leveled
household-style total (`…/[fg]`) or a level-less intensive aggregate (the min-age,
`MONTHS`). So the rule is one-directional: **a unit level, when present, must match the
suffix level**, but a level-less unit on a suffixed name is allowed. An unsuffixed name
is at the `[person]` index, and a leveled token there resolves to `…/[person]`.

`reference_period` and `reference_level` exist only for the structured values that have
no suffix to read; declaring either on a single value — a column, a policy function, or
a **scalar parameter** — is an error for the period (the JSON schema rejects
`reference_period` on `type: scalar`). `reference_level` is the one asymmetry: a scalar
parameter has no aggregation suffix and no body to infer a level from, so a per-person
or per-group amount declares `reference_level` directly. Its default is level-agnostic;
the {ref}`dry-run <gep-10-checks>` forces it where the algebra demands one — a
per-person allowance left agnostic produces a unit mismatch at the multiply-by-count
site, pointing the author at the missing `reference_level: person`.

### Dict parameters with heterogeneous leaves

A dict parameter whose leaves carry different units declares `unit:` as a **mapping from
leaf keys to tokens** (or `DIMENSIONLESS` for a dimensionless leaf). A flow leaf with a
string key takes its period from the key's own time suffix; an integer-keyed flow leaf,
which has no suffix to carry, takes it from the dict-level `reference_period`. A
per-level leaf takes its level from the dict-level `reference_level`:

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
  reference_level: person   # ... and per person
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
declaration. The level facet is orthogonal to currency: both agnostic and concrete
currency tokens acquire their `[level]` from the suffix or `reference_level` just like
everything else.

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

|        | **Layer 1 — DAG validity**                                        | **Layer 2 — boundary**                                                                                                              |
| ------ | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| when   | `fail_if` on the assembled environment                            | GEP-9 canonicalisation boundary                                                                                                     |
| input  | none — synthetic `Quantity`s                                      | the user's unit-annotated input tree                                                                                                |
| checks | inferred body unit vs. declaration; producer↔consumer edges agree | tag currency → run currency; period vs. suffix; level vs. suffix; unknown token rejected; every tag equivalent to its resolved unit |

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
@policy_function(unit=Unit.CURRENCY_FLOW)  # -> CURRENCY / month / [person]
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
*concolic* execution) until every syntactically reachable branch combination is driven —
the explorer tracks no path constraints, so it counts branch combinations, not strictly
feasible paths. A body whose branching exceeds an internal cap is rejected (it must opt
out), never passed with some combinations left unchecked. Each run's result is checked
on its own, so a unit slip on a single arm is caught even though the other arms are
clean. A `return 0.0` arm yields a dimensionless result and falls back to the
declaration, so the ubiquitous `if befreit: return 0.0` guard never raises a false
alarm.

**What the dry-run catches:**

- a body whose inferred unit disagrees with its declaration, on any reachable branch — a
  stock times a per-year rate labelled as a stock, a `_m` flow returned where `_y` is
  declared, or a `…/[person]` result on a `_hh` name;
- an addition or subtraction of two non-equivalent quantities — a monthly flow plus a
  yearly one (`betrag_m + freibetrag_y`), a stock plus a flow, **or two different
  grouping levels** (`einkommen_m_hh − einkommen_m_bg`). At run time the assembled DAG
  computes on bare arrays with no pint, so such a combination is unit-blind and silently
  wrong; the dry-run rejects it rather than letting pint's build-time auto-conversion of
  same-dimension operands paper over it;
- an ordering comparison (`<`, `<=`, `>`, `>=`) of two non-equivalent quantities, or of
  a quantity against a bare non-zero literal — the literal silently carries the
  quantity's unit, so promote the bound to a parameter (only `0` is allowed inline).
  Equality (`==`, `!=`) is deliberately **not** screened: it is the operator for
  sentinel and exact-marker tests — a person-pointer's no-link marker
  (`p_id_empfänger == -1`) or an exact-zero guard (`kindersatz_m == 0.0`) — where the
  literal is a deliberate marker, not a hidden dimensioned bound. The trade-off is that
  an equality between two genuinely non-equivalent quantities is not caught;
- a logical operator (`&`, `|`, `~`) applied to a unit-carrying operand —
  `wealth & is_adult`, where `wealth` is a stock. Logical operators combine truth
  values, so an operand carrying a real unit is a bug the run-time arrays would silently
  swallow;
- a missing unit, and malformed declarations: a flow token without a period, a
  currency-agnostic token on a parameter, disagreeing period or level sources, or a
  boolean node carrying a concrete unit.

**What it cannot catch:**

- **anything that reduces to dimensionless.** The check is *dimensional*, not
  *semantic*: quantities that collapse to the dimensionless dimension are
  indistinguishable to it. A per-period count is `[time]/[time] = 1`, so `HOURS_FLOW`
  reads as a plain number — adding working hours to a share is *not* caught. The same
  blind spot covers a body whose result *infers* dimensionless (an early `return 0.0`,
  or arithmetic that cancels): it falls back to the declaration. So the engine
  guarantees *dimensional* soundness, not that every quantity is the intended *kind*;
- **grouping-level mixing among level-less quantities.** Two intensive aggregates at
  different group indices — the youngest age in the fg versus in the bg — are both
  level-less `MONTHS` and so combine without complaint. Level safety holds precisely for
  the leveled (currency, count, area) quantities, which is where the high-stakes mixing
  happens; for level-less ones it is vacuous, and enforcing it would require an
  index-level lint that would also flag the legitimate broadcasts GETTSIM relies on.

**A note on cross-level ratios.** A ratio of two extensive quantities at different
levels comes out as a *level-conversion* dimension, not bare `DIMENSIONLESS`: a person's
share of household income, `einkommen_m / einkommen_m_hh`, is
`(CURRENCY/[person]) / (CURRENCY/[hh]) = [hh] / [person]` — dimensionally "one over
persons-per-household", which is exactly what an equal-split share is. It is correct,
and it multiplies back cleanly (`[hh]/[person] · CURRENCY/[hh] = CURRENCY/[person]`),
but a body that declares such a share `DIMENSIONLESS` will be told its true unit;
declare it for what it is, or form it as a `count / count` ratio that cancels to
dimensionless.

**A body the dry-run cannot evaluate must opt out explicitly.** The dry-run executes a
*scalar* body symbolically, so a body it cannot trace must opt out: vectorized functions
(`vectorization_strategy="not_required"`), piecewise polynomials and lookup tables,
bodies calling `join` or a raw `xnp` op, and bodies returning an opaque value the
dry-run cannot unit-check. Rather than silently trusting such a body, the check
**rejects** it unless the author marks it `verify_units=False`. The opt-out is of body
*inference only*: the declared output unit still stands, so every *consumer* of this
node is still checked against it, and the units flowing *into* the body are themselves
verified producer outputs. What the opt-out drops is any check *internal* to the body.

**Known limitation.** An opted-out schedule could in principle be evaluated at an
argument whose unit differs from its declared `input_unit` without the dry-run catching
it. The residual risk is small: schedule evaluation goes through a single standardized
primitive, and the argument it receives is itself a verified producer output, so a
mismatch would have to originate inside that machinery. It could escape end to end only
if two opt-out bodies fed one another directly — which does not occur in the current
system.

#### Layer 2: the **boundary check** on the unit-annotated input tree.

**Layer 2** is offered through the unit-annotated input tree (a sibling of the ordinary
input tree in which every leaf is a pint `Quantity`). When the mode is used **every**
leaf must be tagged, including identifiers and other dimensionless columns (tagged
`dimensionless`). The boundary check requires each tagged input to be *equivalent* to
its resolved environment unit once the axes handled elsewhere — currency (converted by
the strip path), a flow's reference period (owned by the suffix guard), and the grouping
level (owned by the suffix guard) — are divided out, so a same-dimension level error
such as a `HECTARES` column tagged `m²`, or a `YEARS` input tagged in months, is
rejected rather than silently mis-scaled. It feeds no node, so it adds no back-edge to
the boundary and needs no declared unit threaded through `processed_data`.
Symmetrically, the **unit-annotated result tree** relabels each output leaf with its
precise run-currency unit (`euro/month`, not the agnostic `CURRENCY_FLOW`) — pure
naming, since results are already computed in the run currency.

(gep-10-auto)=

### Auto-generated nodes

Auto-generated nodes receive auto-assigned units. Time-conversion variants inherit the
source's base token and read the variant's period off its own suffix. Auto-aggregations
derive their token from the source and the aggregation type, paralleling how
{ref}`GEP 4 <gep-4>` resolves their types — and, with grouping levels now in the unit,
the aggregation is also where a level is minted, swapped, or preserved:

| aggregation                   | physical token  | level                                                  |
| ----------------------------- | --------------- | ------------------------------------------------------ |
| `SUM` over an extensive value | preserved       | **swapped** source level → target group level          |
| `COUNT`, `SUM` over a boolean | `[person]`      | **minted** `[person] / [target]` (a head count)        |
| `MEAN`/`MIN`/`MAX`            | preserved       | **preserved** (source level-ness; level-less stays so) |
| `ANY`/`ALL`                   | `DIMENSIONLESS` | level-less (a boolean)                                 |

`SUM` over an extensive value (currency, area) swaps the denominator `[person] → [hh]`,
giving a household total `CURRENCY/month/[hh]`. A **head count** — `COUNT`, *or* a `SUM`
over a *boolean* (a per-person indicator, so its sum counts the persons it is true for)
— mints `[person]/[target]`; the two are the same kind of quantity and must agree, so
`anzahl_erwachsene_bg` reached by `COUNT` and by summing an `ist_erwachsen` flag carry
the identical `[person]/[bg]` — the same unit a `HEADCOUNT` declaration at `bg` resolves
to (the placeholder token a `COUNT` auto-assigns is `HEADCOUNT`). `MEAN`/`MIN`/`MAX`
pick a representative member's value, which is the *same kind* of quantity as the source
— so they preserve its level-ness: the min of person incomes stays `CURRENCY/[person]`,
the min of (level-less) ages stays `MONTHS`. `ANY`/`ALL` yield a *boolean* (not a count)
and auto-assign `DIMENSIONLESS`. A `@group_creation_function` group id is auto-assigned
`DIMENSIONLESS` (an identifier). Where the source's token pins down a concrete currency
(a parameter), the derived node inherits the **agnostic counterpart**.

A hand-written aggregation also carries an author-declared token (one is required to
pass the mandatory-units check), and that declaration is **checked against the derived
unit**, the same declared-vs-produced contract a `@policy_function` body is held to: its
physical *kind* — currency, the `[person]` count, area, a duration — must match what the
aggregation produces, so a `SUM` over a boolean declared `DIMENSIONLESS` rather than
`HEADCOUNT` is rejected. Only the kind is the author's to state; the flow period and the
grouping level are the framework's to derive (a group suffix on a `MEAN`/`MIN`/`MAX` is
a mere *index* level, not a unit level), so they are not compared.

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

Delivered as several PRs, with the framework proven on `mettsim` before any German
annotation. The tracking issues are:

- ttsim [#117](https://github.com/ttsim-dev/ttsim/issues/117) — framework core + tracer
  bullet
- ttsim [#118](https://github.com/ttsim-dev/ttsim/issues/118) — full dimension model
  (time, currency, **grouping levels and the `[person]` count**)
- ttsim [#119](https://github.com/ttsim-dev/ttsim/issues/119) — mandatory units +
  edge-consistency (including the level-vs-suffix check and the aggregation level rules)
- ttsim [#120](https://github.com/ttsim-dev/ttsim/issues/120) — currency knob + Layer-2
  boundary
- ttsim [#121](https://github.com/ttsim-dev/ttsim/issues/121) — annotate mettsim, switch
  check on, CI test
- gettsim [#1191](https://github.com/ttsim-dev/gettsim/issues/1191) — register EUR/DM
- gettsim [#1192](https://github.com/ttsim-dev/gettsim/issues/1192) — gettsim rollout
  (including `reference_level` on per-person/per-group parameters)

Each package's params schema enumerates its own token vocabulary: the core tokens minus
the agnostic currency tokens (the schema governs parameters, which must be concrete)
plus the concrete variants of that package's registered currencies. It also enforces,
per parameter `type:`, the `unit:` XOR `input_unit:`/`output_unit:` split, the shape of
the declaration (a `type: scalar` `unit:` must be a single token; the leaf-keys mapping
form is admitted only for `type: dict`; `type: scalar` may not carry a
`reference_period`), and the `reference_level` value vocabulary (the group names of the
package). The schema shipped with ttsim (listing mettsim's `CASTAR_*`/`SILVER_PENNY_*`
tokens and Middle-Earth levels) is the template; the copy at
`docs/geps/params-schema.json` is migrated together with the YAML files in #1192.

## Alternatives

### Counting quantities as plain `DIMENSIONLESS`

Rejected — this was the earlier draft of this GEP. Treating head counts as
`DIMENSIONLESS` follows SI and pint convention and needs no `[person]` dimension, but it
throws away the grouping-level information that makes the per-capita conversions
checkable: a count is then indistinguishable from a share or a rate,
`wohnen__bruttokaltmiete_m_hh / anzahl_personen_hh` infers a bare currency rather than a
per-person amount, and a household total cannot be told from a Bedarfsgemeinschaft
total. Adopting `[person]` (the count dimension) and the grouping-level dimensions is
what turns the cross-level bodies GETTSIM already writes into self-checking arithmetic.

### A single generic `[count]` dimension with no level

Rejected. An intermediate design promoted counts to one generic `[count]` and per-person
parameters to `CURRENCY / count`, with no grouping level. It is weaker than the adopted
model on both ends: a single `[count]` cannot say *which* group a count is over, so
`anzahl_personen_hh` and `anzahl_personen_bg` are interchangeable and a cross-level mix
still type-checks; and `CURRENCY / count` reads where the law says "Euros per month".
The adopted model fixes both: `[person]` is the *one* count dimension (children and
adults are persons, so they share it and remain addable), the *group* it counts within
rides in the denominator (`[person]/[hh]` ≠ `[person]/[bg]`), and a per-person amount
stays plain `EUR_FLOW` with the level supplied by `reference_level: person` rather than
baked into the token.

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
