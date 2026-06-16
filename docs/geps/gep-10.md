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
  example, parameters denominated in Deutsche Mark can be automatically converted to
  Euros at build time, so a parameter's history can include values in both currencies
  and the user can run in either one without hand-converting the numbers. Similarly, the
  framework can perform time conversions of flows. The existing `_y`/`_m`/`_w` suffix
  convention is preserved.

The engine is [pint](https://pint.readthedocs.io), and it runs **only while the model is
built**: it checks dimensions and converts units, then steps aside. The numeric runtime
is unchanged. As in {ref}`GEP 9 <gep-9>`, the checks fire at definition time, catching a
whole class of unit bugs before they can reach a result.

### Terminology

These terms are used in the GEP:

- **dimension** — the basic kinds of a quantity: `[currency]`, `[time]`, `[area]`, or
  dimensionless. Counting quantities (children, adults, household members) are
  dimensionless, following the SI and pint convention.
- **unit** — a particular way of measuring a dimension, such as Euros for `[currency]`
  or years for `[time]`. A unit carries a conversion factor to the dimension's base
  unit, so e.g. `1 month = 1/12 year`. The available units are called **unit tokens**.
- **currency-agnostic token** - a token that is a placeholder for any currency. Used to
  declare the unit of a function for which it doesn't matter what currency it runs in,
  so the same function can serve a Euro run and a DM run unchanged.
- **concrete currency token** — a token that names one specific currency, used to
  declare the unit of a parameter's stored numbers (or input data), which are in some
  particular currency and converted to the run currency at build time.

## Motivation and Scope

Three long-standing problems motivate this GEP.

1. **No dimensional safety.** The DAG carries quantities of many kinds, but a function
   body may add, subtract, or compare them freely. `betrag_m + miete_pro_qm` (Euros per
   month plus Euros per month per square meter) is a bug that runs silently today and
   surfaces, if at all, as an implausible number far downstream.

1. **Hand-converted historical currency.** Every Deutsche-Mark-era parameter is divided
   by `1.95583` by a maintainer before being written to YAML, with the original value
   preserved only in a free-text `note`. There is no machine-checkable provenance and no
   guard against a transcription error. This is both prone to errors and violates
   GETTSIM's law-to-code approach.

1. **Hand-written time arithmetic.** `ttsim/unit_converters.py` implements ~50
   conversion functions (`y_to_m`, `per_y_to_per_m`, …) and their stock/flow duals by
   hand. The resulting arithmetic was the source of some bugs (that are hopefully fixed
   by now).

**Scope.** The GEP covers `ttsim` (the framework) and `gettsim` (the German currencies
and the policy annotations). GEP 1's `_y`/`_m`/`_w` suffix automation are preserved
unchanged; only the *arithmetic* behind the conversions moves onto the unit engine.

## Usage and Impact

### Units come from parameters and inputs; functions supply the timing

Units enter the model through its **data**: every parameter and every input column
carries a `unit=` declaration. From there the framework works out the unit of whatever a
policy function computes, by running the body on its inputs (the dry-run). A function
still restates that unit in `unit=`, checked against the inferred result so its
declaration is a guard rail, not a new source of truth.

The only exception are tokens that include a "flow" time dimension (`CURRENCY_FLOW`,
`HOURS_FLOW`, …). For those, the period is taken from the name suffix (e.g. `betrag_m`)
or from `reference_period` (if its a parameter):

```python
@policy_function(unit=Unit.CURRENCY_FLOW)  # name betrag_m -> resolved CURRENCY/month
def betrag_m(satz: float, anzahl: int) -> float:
    return satz * anzahl


@policy_function(unit=Unit.CURRENCY_STOCK)  # a stock; a time suffix would be an error
def vermögen(aktien: float, immobilien: float) -> float:
    return aktien + immobilien
```

```yaml
arbeitnehmerpauschbetrag:
  unit: DM_FLOW         # a flow, denominated in DM; build-time -> run currency
  reference_period: Year  # functional: supplies /year
  type: scalar
  1975-01-01:
    value: 564
```

A dimensionless parameter declares `unit: DIMENSIONLESS` — and never carries a
`reference_period`:

```yaml
beitragssatz:
  unit: DIMENSIONLESS   # a rate is dimensionless
  reference_period: null
  type: scalar
  2024-01-01:
    value: 0.013
```

A *per-period* dimensionless quantity is not `DIMENSIONLESS` — it is its own flow token.
The pension Zugangsfaktor moves by a fixed factor for each year of earlier or later
retirement (`zugangsfaktor_veränderung_pro_jahr`, § 77 SGB VI). The factor is a pure
number, but *per year* it is `1/year` — **not** dimensionless — so
`unit: DIMENSIONLESS_FLOW` with `reference_period: Year`. Multiplied by the gap in
`YEARS` between the actual and the reference retirement age, the years cancel and it
yields the dimensionless Zugangsfaktor adjustment.

### Functions work in any currency; one setting picks the run currency

A policy function never names a concrete currency; it uses the agnostic tokens only,
which is what lets the same function serve a Euro run and a DM run unchanged.
Parameters, by contrast, record their legal currency in the unit token itself
(`DM_FLOW`, `EURO_STOCK`). An optional `currency` argument to `main()` chooses the
currency the model runs in, defaulting to the registered base currency (`"euro"` for
GETTSIM); at build time every currency-denominated parameter is converted from its
stored currency to that run currency, so a Deutsche-Mark value and a Euro value can sit
in the same parameter's history and both come out in the run currency.

### Units at the boundary

Tagging input data with pint units is **optional**. A column may be passed as a bare
array — taken to be in the run currency, exactly as today — or as a pint `Quantity`, in
which case the framework converts its *currency* to the run currency at the boundary and
strips the tag, so a user holding DM figures can feed them into a Euro run without
converting them by hand. Only the currency is rescaled. The tag's **period must match
the column's `_y`/`_m` suffix exactly** — a `_m` column needs a `/month` tag, an
unsuffixed column a tag with no period — so a contradictory period (a `_m` column tagged
per year) fails loudly.

Results are returned as bare arrays in the run currency.

### Errors are loud and early

- A `unit=` value that is not in the list of allowed tokens fails at decoration time
  (functions) or load time (parameters).
- A period that is given twice and disagrees fails at build, with no precedence rule to
  paper over it: where both a name suffix and a `reference_period` apply, they must
  agree. Naming a quantity as if it had a period when it does not — a one-off amount
  written `vermögen_m`, or a `reference_period` on a token that is already complete or
  dimensionless — fails the same way.
- A `…_FLOW` token with no period at all (no suffix, no `reference_period`) fails: the
  framework cannot tell what the quantity is *per*.
- A currency in the wrong place fails at decoration or build: a concrete currency token
  on a column or function (these must stay currency-neutral); an agnostic `CURRENCY_*`
  token on a parameter once a currency is registered (the stored numbers are in *some*
  currency, and the declaration must say which); a plain `unit:` on a schedule or lookup
  parameter, which uses `input_unit:`/`output_unit:` instead.
- `updates_previous` across a currency changeover fails at load: an entry that switches
  the currency must restate the whole value, not patch the previous one.
- A dimensionally invalid operation inside a function body fails at environment build,
  naming the function.
- A unit that does not line up across a DAG edge — a producer feeding a consumer that
  expects something else — fails at build.
- A missing `unit=` fails at environment build, the way a missing return type does under
  GEP 9. `DIMENSIONLESS` is *not* missing — it states that the quantity carries no
  dimension.

## Backward Compatibility

- **User code shape is unchanged.** Bare arrays and the DataFrame/mapper interface keep
  working; `currency` defaults to `"euro"` and output stays in Euros.
- **The `unit`/`reference_period` metadata is repurposed.** `unit` becomes one member of
  the token vocabulary and `reference_period` becomes *functional* (it supplies the
  period for `…_FLOW` parameters) rather than purely descriptive.
- **No opt-out.** Unlike the {ref}`GEP 9 <gep-9>` beartype claw, the unit check has no
  env-var escape hatch.
- **A migration is required.** Every node must declare a unit and every bare literal in
  mixed-unit arithmetic must be unit-tagged.

## Detailed Description

### The unit vocabulary

A declaration is one member of the **token vocabulary**. Its backbone is a closed core
enumeration — a `Unit` `StrEnum` shipped by `ttsim`, spelled identically in code
(`Unit.CURRENCY_FLOW`) and in YAML (`unit: CURRENCY_FLOW`):

| token                            | kind     | resolves to                      | typical use              |
| -------------------------------- | -------- | -------------------------------- | ------------------------ |
| `CURRENCY_FLOW`                  | flow     | `CURRENCY / period`              | wages, claims, benefits  |
| `CURRENCY_STOCK`                 | complete | `CURRENCY`                       | wealth, asset thresholds |
| `DIMENSIONLESS`                  | complete | `dimensionless`                  | shares, rates, counts    |
| `DIMENSIONLESS_FLOW`             | flow     | `1 / period`                     | Zugangsfaktor per year   |
| `YEARS`                          | complete | `year`                           | ages, durations          |
| `HOURS_FLOW`                     | flow     | `hour / period`                  | working hours            |
| `SQUARE_METERS`                  | complete | `meter ** 2`                     | dwelling size            |
| `HECTARES`                       | complete | `hectare`                        | land area                |
| `CURRENCY_PER_SQUARE_METER_FLOW` | flow     | `CURRENCY / meter ** 2 / period` | rent caps                |

Tokens are not pint syntax. Internally each token resolves to a pint unit (flow tokens
after the period is filled in); pint expressions never appear in a declaration. The core
enumeration lives in `ttsim`, is shared by all downstream packages, and grows only by an
upstream PR. The full vocabulary adds one set of **concrete currency tokens** per
currency a package registers: `register_currency("DM", ...)` derives one variant per
currency-dimensioned core token — `DM_STOCK`, `DM_FLOW`, `DM_PER_SQUARE_METER_FLOW` —
spelled by replacing the agnostic `CURRENCY` prefix with the upper-cased currency name.
The JSON schema for the parameter YAMLs stays statically enumerable: each package's copy
lists the core tokens plus its own currency tokens. The currency-dimensioned rows of the
table above are the *agnostic* tokens; they belong to columns and functions, while
parameters declare the concrete variants (see {ref}`Currency <gep-10-currency>` below).

**Counting quantities are dimensionless**, following SI and pint convention. A
per-person parameter declares the same token as any other amount (`EURO_FLOW` for a
monthly Regelsatz); scaling it by a head count is a plain multiplication that preserves
the unit. A dimensionless quantity (a share, a rate, a head count) declares
`DIMENSIONLESS` (`unit: DIMENSIONLESS`).

**Boolean nodes are dimensionless by construction** and are structurally exempt: they
declare no unit, and declaring one on a boolean node is an error. The same structural
exemption covers identifiers (`p_id`, `*_id`, `p_id_*`) and `@group_creation_function`s
— identifiers are labels, not quantities.

### pint runs at build time only

The foundational constraint is that pint never wraps a live array. A `pint.Quantity` is
not a JAX pytree and does not trace under `jit`; wrapping runtime columns would fight
both JAX and the GEP-9 `FloatColumn` vocabulary. Instead, pint is used in two build-time
roles:

- to compute conversion **factors** (time and currency), which are baked into the
  workers exactly as the literal `12` is baked into `y_to_m` today; and
- to run the **dry-run** dimensionality check on representative `Quantity`s.

The numeric runtime path is unchanged: pure arrays, single currency, JAX-safe.

### Units, suffixes, and periods

A flow token is completed by exactly one period source; complete tokens admit none. The
rules are checked in both directions, and wherever two sources could apply to the same
quantity they must coincide — there is no precedence order:

- **Columns and functions.** A time suffix (`_y/_q/_m/_w/_d`) requires a `…_FLOW` token,
  and a `…_FLOW` token requires a time suffix; the suffix supplies the period. A
  complete token on a suffixed name — or a flow token on an unsuffixed one — fails at
  build. This makes the {ref}`GEP 1 <gep-1>` convention machine-checked: a node named
  `…_m` whose body computes a stock cannot be declared.
- **Scalar parameters.** A `…_FLOW` token requires a non-null `reference_period`, which
  supplies the period; a complete or `DIMENSIONLESS` declaration requires
  `reference_period: null`. A parameter whose *name* carries a time suffix
  (`lump_sum_deduction_y`) is thereby a flow with a second period source: the suffix
  must coincide with `reference_period`, and a complete or `DIMENSIONLESS` token under a
  suffixed name fails.

Time is a first-class pint dimension. The hand-written arithmetic in
`unit_converters.py` is reimplemented so factors are sourced from pint
(`Quantity(1, "year").to("month")`), while the suffix auto-generation and naming are
kept verbatim.

### Dict parameters with heterogeneous leaves

A dict parameter whose leaves carry different units declares `unit:` as a **mapping from
leaf names to tokens** (or `DIMENSIONLESS` for a dimensionless leaf). A flow leaf gets
its period from the leaf key's own time suffix, or — for keys that cannot carry one,
such as integer keys — from the dict-level `reference_period`:

```yaml
schedule:
  unit:
    child_amount_y: EURO_FLOW   # period from the leaf key's _y
    max_age: YEARS
  reference_period: null
  type: dict
  2024-01-01:
    child_amount_y: 3000.0
    max_age: 18
```

```yaml
satz_nach_kindanzahl:
  unit: EURO_FLOW           # uniform: one token for all leaves
  reference_period: Month   # integer keys carry no suffix
  type: dict
  2024-01-01:
    1: 250.0
    2: 250.0
```

The strict-coincidence rule applies per leaf:

- a suffixed flow leaf under a non-null `reference_period` must **agree** with it —
  disagreement is a build error, the suffix does not win;
- a suffix-less flow leaf takes the dict-level `reference_period`; if that is `null`,
  the leaf has no period source and fails;
- mixed-period dicts are legal when each flow leaf carries its own suffix
  (`base_amount_m` next to `annual_bonus_y`): every period is explicit in a key, so
  nothing is left to convention.

In the dry-run, dict parameters become dicts of representative `Quantity`s (uniform for
a scalar `unit:`, per-leaf for a mapping), so bodies that subscript them are verifiable.
The mandatory-units check covers every leaf of the value active at the policy date; a
leaf missing from the `unit:` mapping is a *missing* declaration, a `DIMENSIONLESS` leaf
is a dimensionless one.

### Function-like parameters: one token per axis

A schedule or lookup table is not a quantity — it is a *function between quantities*,
with a domain and a codomain. The function-like parameter types (the `piecewise_*`
family, the lookup tables, the phase-in/out types) therefore declare `input_unit:` and
`output_unit:` instead of `unit:`; a `unit:` on them is an error, and the JSON schema
enforces the split per `type:`:

```yaml
tarif:
  input_unit: EURO_FLOW    # taxable income per year in ...
  output_unit: EURO_FLOW   # ... tax per year out
  reference_period: Year
  type: piecewise_quadratic
  ...
```

Each axis token follows the same kind rules as a scalar declaration; per-axis
declarations are single tokens (or `DIMENSIONLESS` for a dimensionless axis), never
mappings. The single `reference_period` supplies the period of *every* flow axis; a
`reference_period` that no flow axis consumes is dangling and fails; a time suffix on
the parameter's *name* must coincide with the **output** axis — the suffix names what
the parameter yields.

(gep-10-currency)=

### Currency

Currencies live in the framework as a `[currency]` dimension with concrete currencies
registered by downstream packages via
`register_currency(name, *, base=False, definition=None)`. `gettsim` registers `euro`
(base) and `DM = euro / 1.95583`. Registration does two things: it provides the
**conversion factors**, with pint as the single source of truth for the rate; and it
derives the currency's **declaration tokens** — one concrete variant per
currency-dimensioned core token (`DM_STOCK`, `DM_FLOW`, `DM_PER_SQUARE_METER_FLOW`,
`EURO_*`, …) — extending the registering package's unit vocabulary.

**Agnostic and concrete tokens.** The agnostic tokens (`CURRENCY_STOCK`,
`CURRENCY_FLOW`, …) stand for any registered currency; for every dimensionality check a
concrete token means exactly what its agnostic counterpart means. The dry-run and the
edge check compare at the dimensionality level and never see a concrete currency — a
DM-denominated parameter feeds a currency-agnostic function without further ado, while
adding Euros to Euros per square meter is still caught. What a concrete token adds is
**denomination**: it names the currency the parameter's numbers are written in, which
the build-time conversion to the run currency reads off the declaration.

**Parameters must be concrete; functions must be agnostic.** A parameter's numbers are
written in *some* currency, so once a concrete currency is registered, an agnostic
`CURRENCY_*` token on a parameter is a build error — the declaration must name the
denomination (`DM_FLOW`, not `CURRENCY_FLOW`). Columns and functions may *only* declare
agnostic tokens

**The run currency.** The `currency` argument to `main()` defaults to the registered
base currency (`"euro"` for GETTSIM); it is the currency the input data is taken to be
in and that the outputs come out in. At environment build, every currency-denominated
*parameter* is converted from its declared denomination to the run currency: scalar
values, dict parameters leaf by leaf (each currency leaf by its own token), schedules
axis by axis, and lookup-table values (see the per-axis rules above). The factors are
baked in at build time; the numeric runtime path stays single-currency.

**A changeover within one parameter's history.** A dated entry may restate the unit
field(s), overriding the top-level declaration for that entry's numbers. This is how the
DM→Euro switch is written: entries before the reform are denominated in the legacy
currency, entries from the reform date in the new one —

```yaml
arbeitnehmerpauschbetrag:
  unit: DM_FLOW
  reference_period: Year
  type: scalar
  1990-01-01:
    value: 2000
  2002-01-01:
    unit: EURO_FLOW   # the changeover: denominated in Euro from here on
    value: 1044
```

`updates_previous` cannot cross a changeover: an entry that restates the unit
declaration must restate the full value, because a merged value would mix numbers
denominated in different currencies.

### Unit checking and input conversion at build time

- **Layer 1 — DAG validity (data-independent).** Each function is checked in isolation:
  its inputs are wrapped in `Quantity`s of their *declared* units, the scalar body is
  executed in NumPy+pint, and the result must carry no dimensional error and match the
  declared output unit. An *edge-consistency* pass then confirms each producer's unit
  equals the consumer's declared expectation. No user data or fabricated dataset is
  needed. Layer 1 runs as an build-time `fail_if` on the assembled environment.
- **Layer 2 — input conversion (boundary).** Users *may* attach a pint `Quantity`s to
  their input data. At the GEP-9 canonicalisation boundary the tag's *currency* is
  converted to the run currency — a DM-tagged column feeds a Euro run, rescaled at the
  boundary — and the tag is stripped to a bare array for the numeric path. The tag's
  *period* is checked against the column's GEP-1 time suffix. A bare, untagged column is
  taken to already be in the run currency. Validating the tag's *dimension* against the
  column's declared unit (to reject e.g. a currency tag on an age column) would have to
  thread that declared unit to the boundary and is deferred to future work.

**Booleans in the dry-run.** Boolean inputs are not quantities: they enter the dry-run
as bare `True`/`False`. Because branch selection hinges on them, a body with boolean
inputs is dry-run **twice** — once with all of them truthy, once falsy — so both arms of
the dominant guard pattern (`if exempt: return 0.0 else: <real arithmetic>`) are
verified.

### Auto-generated nodes

Auto-generated nodes receive auto-assigned units: time-conversion variants inherit the
source's base token and the variant's period is read off its own suffix;
auto-aggregations derive their token from the source and the aggregation type
(SUM/MEAN/MIN/MAX preserve; COUNT, ANY, and ALL are dimensionless), paralleling how
{ref}`GEP 4 <gep-4>` resolves their types. An automatic SUM over a boolean column is a
head count and resolves to dimensionless; an explicit SUM aggregation declares its unit
(`unit=DIMENSIONLESS` when the source is boolean). Where the source's token pins down a
concrete currency (a parameter), the derived node inherits the **agnostic counterpart**.

### Literals

Bare numeric literals in mixed-unit arithmetic must be unit-tagged in code
(`geburtsmonat - 1 * month`, `regelaltersgrenze + 0.00001 * year`). This is strict by
choice: it makes the ambient unit explicit and lets the check catch a wrong literal.

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
`docs/geps/params-schema.json` (the validation target for all German parameter YAMLs)
still describes the pre-GEP-10 label vocabulary and is migrated together with the YAML
files in #1192, adding the `DM_*`/`EURO_*` tokens.

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
counts `count`. The intended payoff was catching a forgotten per-capita scaling
(comparing a per-person threshold against a family-level income without multiplying by
the family size would not type-check). It was dropped because:

- the protection is weaker than it looks: a single generic `[count]` cannot distinguish
  per-child from per-adult from per-household, so scaling by the *wrong* count still
  type-checks — only the forgot-entirely case is caught;
- the annotation tax lands on every per-capita parameter in the system (Regelsätze,
  Kindergeld, Freibeträge, …), which would read `CURRENCY / count` where the law and
  every practitioner say "Euros per month";
- SI and pint treat counting quantities as dimensionless; deviating from that convention
  surprises anyone who knows either.

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
Returning results as pint-labelled `Quantity`s, rather than the bare arrays produced
today, is left as future work.

## References and Footnotes

- [gettsim #1174 (the originating DM-values discussion)](https://github.com/ttsim-dev/gettsim/issues/1174)
- [pint](https://pint.readthedocs.io)
- [NEP 18 (NumPy `__array_function__`)](https://numpy.org/neps/nep-0018-array-function-protocol.html)

## Copyright

This document has been placed in the public domain.
