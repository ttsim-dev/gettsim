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
  unit, so e.g. `1 month = 1/12 year`. The available units are called **unit tokens**.

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

## Usage and Impact

Units enter the model through its **data**: every parameter and every input column
carries a `unit=` declaration. From there the framework works out the unit of whatever a
policy function computes by running the body on its inputs (the *dry-run*); the function
still restates that unit in `unit=`, checked against the inferred result so its
declaration is a guard rail, not a new source of truth. Flow tokens (`CURRENCY_FLOW`, …)
take their period from the {ref}`GEP 1 <gep-1>` name suffix:

```python
@policy_function(unit=Unit.CURRENCY_FLOW)  # name betrag_m -> resolved CURRENCY/month
def betrag_m(regelsatz_m: float, anzahl: int) -> float:
    return regelsatz_m * anzahl


@policy_function(unit=Unit.CURRENCY)  # a stock; a time suffix would be an error
def vermögen(aktien: float, immobilien: float) -> float:
    return aktien + immobilien
```

A policy function names no particular currency, so the same body serves a Euro run and a
DM run unchanged; parameters, by contrast, record their legal currency in the token
itself (`DM_FLOW`, `EUR_FLOW`). One optional `currency` argument to `main()` picks the
currency the model runs in — defaulting to the registered base currency (`"EUR"` for
GETTSIM) — and every currency-denominated parameter is converted to it at build time.

Tagging input data with units is **optional**, through a dedicated unit-annotated input
tree; results can likewise be returned as a unit-annotated tree in precise run-currency
units. And every mistake the framework can see — a mistyped token, mixing incompatible
quantities, a unit that does not line up across a DAG edge, a missing declaration —
surfaces when the model is *defined* (at decoration, load, or environment build), never
as a wrong number at run time. `DIMENSIONLESS` is a real declaration — it states that
the quantity carries no dimension — not a blank one.

The rest of this GEP is the reference: the {ref}`token vocabulary <gep-10-vocabulary>`,
the {ref}`period sources <gep-10-periods>`, the {ref}`currency model <gep-10-currency>`,
and {ref}`exactly what the checks catch <gep-10-checks>`.

## Backward Compatibility

- **User code shape is unchanged.** Bare arrays and the DataFrame/mapper interface keep
  working; `currency` defaults to `"EUR"` and output stays in Euros.
- **The `unit`/`reference_period` metadata is repurposed.** `unit` becomes one member of
  the token vocabulary and `reference_period` becomes *functional* (it supplies the
  period for `…_FLOW` parameters that no name can carry) rather than purely descriptive.
- **No blanket opt-out.** Unlike the {ref}`GEP 9 <gep-9>` beartype claw, there is no
  env-var escape hatch that switches the unit check off wholesale; the only opt-out is
  per-function and body-only (`verify_units=False`, {ref}`see below <gep-10-checks>`).
- **A migration is required.** Every node must declare a unit; suffix-less flow
  parameters are renamed to carry a time suffix (`arbeitnehmerpauschbetrag` →
  `arbeitnehmerpauschbetrag_y`), since the suffix is now the period source wherever a
  name can carry one; and a bare literal of a real dimension is promoted to a parameter
  or its function body opts out with `verify_units=False`.

## Detailed Description

(gep-10-vocabulary)=

### The unit vocabulary

A declaration is one member of the **token vocabulary**. Its backbone is a closed core
enumeration — a `Unit` `StrEnum` shipped by `ttsim`, spelled identically in code
(`Unit.CURRENCY_FLOW`) and in YAML (`unit: CURRENCY_FLOW`):

| token                            | resolves to                      | typical use              |
| -------------------------------- | -------------------------------- | ------------------------ |
| `CURRENCY_FLOW`                  | `CURRENCY / period`              | wages, claims, benefits  |
| `CURRENCY`                       | `CURRENCY`                       | wealth, asset thresholds |
| `DIMENSIONLESS`                  | `dimensionless`                  | shares, rates, counts    |
| `DIMENSIONLESS_FLOW`             | `1 / period`                     | Zugangsfaktor per year   |
| `YEARS`                          | `year`                           | ages, durations          |
| `HOURS_FLOW`                     | `hour / period` (dimensionless)  | working hours            |
| `SQUARE_METERS`                  | `meter ** 2`                     | dwelling size            |
| `CURRENCY_PER_SQUARE_METER_FLOW` | `CURRENCY / meter ** 2 / period` | rent caps                |

A token ending in `…_FLOW` needs a period; every other token is complete as written and
takes no period. So the `…_FLOW` suffix is the only flow marker — there is no separate
"stock" spelling, a currency stock is the bare `CURRENCY` token. Tokens are not pint
syntax: each resolves internally to a pint unit (flow tokens after the period is filled
in), but pint expressions never appear in a declaration.

`HOURS_FLOW` is the one flow token that resolves to a *dimensionless* quantity: hours
and the period are both `[time]`, so hours per week is a time-over-time ratio. It is
kept as a distinct token so the time-suffix and time-conversion bookkeeping still apply
to working hours, but dimensionally it cannot be told apart from a bare `DIMENSIONLESS`
quantity. Likewise, a *per-period* dimensionless quantity is `DIMENSIONLESS_FLOW`, not
`DIMENSIONLESS`: the pension Zugangsfaktor moves by a fixed factor per year of earlier
or later retirement (`zugangsfaktor_veränderung_y`, § 77 SGB VI) — a pure number, but
*per year* it is `1/year`, and multiplied by the gap in `YEARS` the years cancel to the
dimensionless adjustment.

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

**There are no exemptions** — every active node has a unit; only its *source* differs.
Most nodes declare it. Derived nodes get one auto-assigned
({ref}`see below <gep-10-auto>`); the framework-injected date nodes get theirs from the
framework (`policy_year` is in years, etc.). So `UNSET_UNIT` has a single meaning — *no
declaration was made* — which the mandatory-units check always reports as an error, with
no second "legitimately blank" reading to disambiguate.

Beyond the core enumeration, the full vocabulary adds one set of **concrete currency
tokens** per registered currency ({ref}`see Currency <gep-10-currency>`); the
currency-dimensioned rows of the table above are the *agnostic* tokens. The core
enumeration lives in `ttsim`, is shared by all downstream packages, and grows only by an
upstream PR; each package's params JSON schema stays statically enumerable, listing the
core tokens plus its own currency tokens.

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

### Units, suffixes, and periods

A flow token is completed by exactly one period source; complete tokens admit none. The
period comes from the **name suffix wherever a name or key can carry one**, and from
`reference_period` only where it cannot:

| node kind                                 | flow period from              | `reference_period` |
| ----------------------------------------- | ----------------------------- | ------------------ |
| column / policy function                  | name suffix `_y/_q/_m/_w/_d`  | forbidden          |
| scalar parameter / string-keyed dict leaf | name (or key) suffix          | forbidden          |
| integer-keyed dict leaf                   | dict-level `reference_period` | required           |
| function-like parameter axis              | `reference_period`            | required           |

Where the suffix supplies the period it is also *mandatory and exclusive*: a time suffix
requires a `…_FLOW` token and a `…_FLOW` token requires a time suffix, so a complete
token on a suffixed name — or a flow token on an unsuffixed one — fails at build. This
makes the {ref}`GEP 1 <gep-1>` convention machine-checked: a node named `…_m` whose body
computes a stock cannot be declared. Because `reference_period` is forbidden there,
there is nothing to reconcile; only where no name carries a suffix (integer keys,
schedule axes) is `reference_period` functional.

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

Where a leaf key carries a suffix *and* the dict also sets a `reference_period`, the two
must coincide — there is no precedence order. Mixed-period dicts are legal when each
flow leaf carries its own suffix (`base_amount_m` next to `annual_bonus_y`).

**Leaves that change name across the parameter's history.** The `unit:` mapping is a
**union over all dated entries**: the mandatory-units check looks only at the leaves
present in the value active at the policy date and ignores mapping entries for leaves
that exist only at other dates. So a leaf renamed across a reform is covered by listing
both names (`child_amount_y` before, `base_amount_y` after). A value leaf with no entry
in the mapping is a *missing* declaration and is flagged, so a mistyped key cannot pass
silently. When the renamed leaves share a token, the simpler **uniform** form — a single
scalar `unit: EUR_FLOW` with the period read from each leaf's own suffix — makes the
rename irrelevant; the mapping is only for genuinely heterogeneous leaves. A leaf whose
*currency* changes across dates is a changeover ({ref}`see Currency <gep-10-currency>`).

In the dry-run, dict parameters become dicts of representative `Quantity`s (uniform for
a scalar `unit:`, per-leaf for a mapping), so bodies that subscript them are verifiable.

### Function-like parameters: one token per axis

A schedule or lookup table is not a quantity — it is a *function between quantities*,
with a domain and a codomain. The function-like parameter types (the `piecewise_*`
family, the lookup tables, the phase-in/out types) therefore declare `input_unit:` and
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

Each axis token follows the same kind rules as a scalar declaration; per-axis
declarations are single tokens (or `DIMENSIONLESS`), never mappings. The single
`reference_period` supplies the period of *every* flow axis; a `reference_period` that
no flow axis consumes is dangling and fails; a time suffix on the parameter's *name*
must coincide with the **output** axis — the suffix names what the parameter yields.

(gep-10-currency)=

### Currency

Currencies live in the framework as a `[currency]` dimension, with concrete currencies
registered by downstream packages via
`register_currency(name, *, base=False, definition=None)`. `gettsim` registers `EUR`
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
declaration. For every *dimensionality* check a concrete token means exactly what its
agnostic counterpart means: the dry-run and the edge check compare at the dimension
level and never see a concrete currency, so a DM-denominated parameter feeds a
currency-agnostic function without further ado, while adding Euros to Euros per square
meter is still caught.

**Parameters must be concrete; functions must be agnostic.** A parameter's numbers are
written in *some* currency, so once a concrete currency is registered, an agnostic
`CURRENCY_*` token on a parameter is a build error — the declaration must name the
denomination (`DM_FLOW`, not `CURRENCY_FLOW`). Columns and functions may *only* declare
agnostic tokens.

**The run currency.** The `currency` argument to `main()` defaults to the registered
base currency; it is the currency the input data is taken to be in and that the outputs
come out in. At environment build, every currency-denominated *parameter* is converted
from its declared denomination to the run currency: scalar values, dict parameters leaf
by leaf (each currency leaf by its own token), schedules axis by axis, and lookup-table
values. The factors are baked in at build time; the numeric runtime path stays
single-currency.

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

(gep-10-checks)=

### Build-time checks and boundary conversion

The checks run in two layers, both at build time, neither needing a fabricated dataset:

|        | **Layer 1 — DAG validity**                                                                              | **Layer 2 — boundary**                                                                                          |
| ------ | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| when   | `fail_if` on the assembled environment                                                                  | GEP-9 canonicalisation boundary                                                                                 |
| input  | none — representative `Quantity`s                                                                       | the user's unit-annotated input tree                                                                            |
| checks | inferred body unit vs. declaration; `+`/`−`/ordering operands equivalent; producer↔consumer edges agree | tag currency → run currency; period vs. suffix; unknown token rejected; every tag's dimension vs. resolved unit |

**Layer 1** runs each scalar body in NumPy+pint, infers the unit that falls out, and
checks it against the declaration; an edge-consistency pass then confirms each
producer's unit equals its consumer's declared expectation. The mechanics are below.

**Layer 2** is offered through the unit-annotated input tree (a sibling of the ordinary
input tree in which every leaf is a pint `Quantity`). Only the tree interface carries
tags — a DataFrame column has nowhere to hang a per-column unit, so the DataFrame modes
and the bare tree stay tag-free and are taken to already be in the run currency. When
the mode is used **every** leaf must be tagged, including identifiers and other
dimensionless columns (tagged `dimensionless`) — a full-coverage contract that is what
lets the dimension check be exhaustive. The dimension check reads the extracted input
units against the resolved environment units; it feeds no node, so it adds no back-edge
to the boundary and needs no declared unit threaded through `processed_data`.
Symmetrically, the **unit-annotated result tree** relabels each output leaf with its
precise run-currency unit (`euro/month`, not the agnostic `CURRENCY_FLOW`) — pure
naming, since results are already computed in the run currency.

**How the dry-run checks one body.** The check *runs the function body*, but with
**units in place of numbers**. Each input becomes a stand-in carrying its resolved unit
and a throwaway magnitude of `1`; pint carries the units through the body's arithmetic,
and the unit that falls out of the `return` is compared to the declaration. Because the
magnitude is never used, no real data is needed:

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
*concolic* execution) until every reachable path is driven. The number of runs is the
number of *reachable* paths, not `2^n`: when `befreit` is true the body returns before
the income test, so that comparison never even becomes a question. Each run's result is
checked on its own, so a unit slip on a single arm — say, returning a yearly figure
where `_m` was declared — is caught even though the other arms are clean. A `return 0.0`
arm yields a dimensionless result and falls back to the declaration, so the ubiquitous
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
- an ordering comparison (`<`, `<=`, `>`, `>=`) of two non-equivalent quantities;
- a missing unit, and malformed declarations: a flow token without a period, a
  currency-agnostic token on a parameter, disagreeing period sources, or a boolean node
  carrying a concrete unit.

**What it cannot catch:**

- **wrong magnitudes** — a coefficient, rate, or constant with the correct unit but the
  wrong value (a 2.5% rate written as `0.25`); units are not values;
- **a result that comes out dimensionless** — a body inferring a dimensionless value (an
  early `return 0.0`, or arithmetic that cancels) falls back to the declaration;
- **equality comparisons** — `==` and `!=` are not unit-screened, unlike ordering.

**A body the dry-run cannot evaluate must opt out explicitly.** The dry-run executes a
*scalar* body symbolically, so a body it cannot trace must opt out: vectorized functions
(`vectorization_strategy="not_required"`, no scalar form for pint to walk), piecewise
polynomials and lookup tables (evaluated by table machinery), and bodies calling `join`
or a raw `xnp` op. Rather than silently trusting such a body, the check **rejects** it
unless the author marks it `verify_units=False` on the decorator. The opt-out is of body
*inference only*: the declared unit still stands and the body's edges are still checked.
Because the flag is explicit, every un-verified body is greppable — a deliberate choice,
and a ready-made worklist should the dry-run later learn to evaluate these operations.

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
plus the concrete variants of that package's registered currencies. It also enforces the
`unit:` XOR `input_unit:`/`output_unit:` split per parameter `type:` and admits the
per-entry overrides in dated entries. The schema shipped with ttsim (listing mettsim's
`CASTAR_*`/`SILVER_PENNY_*` tokens) is the template; the copy at
`docs/geps/params-schema.json` (the validation target for all German parameter YAMLs) is
migrated together with the YAML files in #1192, adding the `DM_*`/`EUR_*` tokens.

## Alternatives

### Runtime pint Quantities flowing through the DAG

Rejected. `Quantity` is not a JAX pytree, breaks tracing, contradicts the GEP-9 column
vocabulary, and adds hot-path cost. Units in a tax-transfer model are static structural
properties of nodes, not of data, so runtime wrapping buys nothing the build-time check
does not already provide.

### Inference-only (no declared units)

Rejected in favour of mandatory declarations. Inference alone localises a bug only where
dimensions clash downstream; a mandatory declared return unit localises it at the
offending function and is self-documenting, at the cost of annotation churn the codebase
largely already absorbs for types.

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

## Discussion

(Open. To be resolved on Zulip.) Known points for debate: the strictness of literal
tagging; whether per-capita scaling should ever get dedicated dimensions (see the
rejected `[count]` alternative — revisit if missing-scale bugs accumulate); and whether
the gettsim rollout should be a single large PR or staged behind a temporary gate.

## References and Footnotes

- [gettsim #1174 (the originating DM-values discussion)](https://github.com/ttsim-dev/gettsim/issues/1174)
- [pint](https://pint.readthedocs.io)
- [NEP 18 (NumPy `__array_function__`)](https://numpy.org/neps/nep-0018-array-function-protocol.html)

## Copyright

This document has been placed in the public domain.
