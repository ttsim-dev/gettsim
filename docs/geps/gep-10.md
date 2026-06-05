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

- GETTSIM mixes quantities of incompatible kinds on the same DAG — Euros, Euros per
  square meter, shares, ages in years, counts of people — but nothing checks that the
  arithmetic combining them is dimensionally sound. A monthly amount can be added to a
  per-square-meter rent, or a stock to a flow, and the model runs silently.
- Historical parameters denominated in Deutsche Mark are converted to Euros *by hand* in
  the YAML files (e.g. a 1975 value stored as `288` with `note: 564 DM`). The conversion
  is invisible to the machine and easy to get wrong
  ([gettsim #1174](https://github.com/ttsim-dev/gettsim/issues/1174)).
- This GEP adopts [pint](https://pint.readthedocs.io) as the unit engine and introduces
  a dimensionality check across the DAG, automatic currency resolution, and a
  pint-backed reimplementation of the time-conversion arithmetic. The win, in the spirit
  of {ref}`GEP 9 <gep-9>`, is that a whole class of unit bugs becomes a loud error at
  definition time instead of a silent numerical fault.
- Crucially, pint runs **only at environment-build time** and at the **input boundary**.
  It never wraps a live array, so the JAX/NumPy runtime — and the GEP-9 type vocabulary
  — are untouched.

### Terminology

- **dimension** — a kind of quantity: `[currency]`, `[time]`, `[area]`, or
  dimensionless. Counting quantities (children, adults, members) are dimensionless,
  following SI and pint convention.
- **unit token** — the value of the `unit=` field: one member of the token vocabulary,
  which is a closed core enumeration (`Unit.CURRENCY_FLOW`, `Unit.YEARS`, …; spelled as
  the identical string in YAML) plus the **currency tokens** each package derives by
  registering its currencies (`DM_STOCK`, `EURO_FLOW`, …). Tokens come in two kinds:
  **flow tokens** (named `…_FLOW`) denote a per-period quantity and are completed by a
  period supplied elsewhere; all other tokens are **complete** as written. Internally
  every token resolves to a pint unit; declarations never contain pint syntax. Some
  tokens are units in the strict metrological sense (`YEARS`), others denote a family of
  units closed over the period (`CURRENCY_FLOW`) — the field is called `unit=` for the
  colloquial question it answers.
- **flow** — a per-period quantity (Euros *per month*). Declared with a `…_FLOW` token;
  the period is supplied by the name suffix (`_m`) for columns/functions or by
  `reference_period` for parameters. A **stock** (wealth, an asset threshold) and other
  intrinsically a-temporal or intrinsically temporal quantities (ages) use complete
  tokens and carry no period source.
- **dimensionless declaration** — a share, a rate, a head count declares *no* unit:
  `unit=None` in code, `unit: null` in YAML. Spelled-out synonyms (`"dimensionless"`,
  pint's built-in `count`) are rejected so there is exactly one way to write it. A
  dimensionless declaration never combines with a period source; a dimensionless
  quantity *per period* is its own flow token (`SHARE_FLOW`).
- **agnostic vs. concrete currency tokens** — the agnostic tokens (`CURRENCY_FLOW`,
  `CURRENCY_STOCK`, …) denote the *union* of the registered currencies: "of the
  `[currency]` dimension, in whatever currency". Registering a currency derives one
  concrete variant per agnostic token (`DM_FLOW`, `EURO_STOCK`, …). For every
  dimensionality check a concrete token means exactly what its agnostic counterpart
  means; in addition it names the currency a parameter's numbers are written in. Columns
  and functions declare agnostic tokens only — that is what makes them provably
  currency-agnostic; parameters must pin down the concrete currency.
- **dry-run** — the build-time pass that executes a function body on representative pint
  `Quantity`s to infer and check its unit. Never runs on user data values and never
  under `jit`.

## Motivation and Scope

Three long-standing problems motivate this GEP.

1. **No dimensional safety.** The DAG carries quantities of many kinds, but a function
   body may add, subtract, or compare them freely. `betrag_m + miete_pro_qm` (Euros per
   month plus Euros per month per square meter) is a bug that runs silently today and
   surfaces, if at all, as an implausible number far downstream.

1. **Hand-converted historical currency.** Every Deutsche-Mark-era parameter is divided
   by `1.95583` by a maintainer before being written to YAML, with the original value
   preserved only in a free-text `note`. There is no machine-checkable provenance and no
   guard against a transcription error.

1. **Hand-written time arithmetic.** `ttsim/unit_converters.py` implements ~50
   conversion functions (`y_to_m`, `per_y_to_per_m`, …) and their stock/flow duals by
   hand. The stock/flow split is exactly the kind of distinction a unit engine gets
   right by construction.

**Scope.** The GEP covers `ttsim` (the framework), `gettsim` (German currencies and
policy annotations), and `gettsim-personas`/`mettsim` (the example system, used as the
end-to-end proof). It deliberately does **not** make policy functions time-agnostic: the
`_y`/`_m`/`_w` suffix automation and the law-to-code naming of {ref}`GEP 1 <gep-1>` are
preserved. Only the *arithmetic* behind the conversions changes.

## Usage and Impact

### Maintainers annotate units; the period stays implicit for flows

Every `@policy_function`, `@policy_input`, `@param_function`, and `@agg_*_function`
carries a `unit=` token. Flow tokens (`…_FLOW`) get their period from the name suffix
(columns/functions) or from `reference_period` (parameters); complete tokens are the
whole unit and admit no period source. Reading a declaration requires no rule book: a
token either names the complete unit, or says in its own name that it is a flow.

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

A dimensionless parameter declares `unit: null` — and never carries a
`reference_period`:

```yaml
beitragssatz:
  unit: null            # a rate is dimensionless
  reference_period: null
  type: scalar
  2024-01-01:
    value: 0.013
```

A *per-period* dimensionless quantity is not `null` — it is its own flow token. The
wealth-tax rate (one percent of the stock, per year) is `unit: SHARE_FLOW` with
`reference_period: Year`, resolving to `1/year`; multiplied by a `CURRENCY_STOCK` it
yields a well-formed `CURRENCY_FLOW`.

### Functions are currency-agnostic; one knob sets the currency

A new optional `main()` input `currency` (defaulting to the registered base currency,
`"euro"` for GETTSIM) sets the currency of the input data and of the output. Parameters
name their legal denomination in the unit token itself (`DM_FLOW`, `EURO_STOCK`), and
every currency-denominated number is converted to the run currency at build time.
Functions only ever declare the agnostic tokens and never mention a concrete currency.

### Errors are loud and early

- A `unit=` value that is not a member of the token vocabulary fails at decoration time
  (functions) or load time (parameters); the YAML schema enumerates the legal strings —
  the core tokens plus the package's own currency tokens — so pre-commit catches it
  before GETTSIM even loads the file.
- A kind/period-source mismatch fails at build, with no precedence rules: a time suffix
  on a node with a complete token; a `…_FLOW` token with no period source; a
  `reference_period` on a complete or `null` declaration; a suffix and a
  `reference_period` that disagree. Wherever two period sources apply to the same
  quantity they must coincide — disagreement is an error, never resolved silently.
- A currency-placement error fails at decoration or build: a concrete currency token on
  a column or function (functions are currency-agnostic); an agnostic `CURRENCY_*` token
  on a parameter once a concrete currency is registered (the numbers are written in
  *some* currency, and the declaration must name it); a `unit:` on a function-like
  parameter type, which declares `input_unit:`/`output_unit:` instead.
- `updates_previous` across a currency changeover fails at load: a dated entry that
  restates the unit declaration must restate the full value.
- A dimensionally invalid operation inside a body fails at environment build, naming the
  function.
- A producer/consumer unit mismatch across a DAG edge fails at build.
- A missing `unit=` fails at environment build, paralleling GEP-9's mandatory return
  types. `unit=None` / `unit: null` is *not* missing — it declares a dimensionless
  quantity.
- An input column tagged with a pint `Quantity` whose unit disagrees with the declared
  unit fails loudly at the boundary.

## Backward Compatibility

- **User code shape is unchanged.** Bare arrays and the DataFrame/mapper interface keep
  working; `currency` defaults to `"euro"` and output stays in Euros.
- **The `unit`/`reference_period` metadata is repurposed.** `unit` becomes one member of
  the token vocabulary and `reference_period` becomes *functional* (it supplies the
  period for `…_FLOW` parameters) rather than purely descriptive. As under the pre-GEP
  schema, the legal `unit:` values are enumerable in the JSON schema — each package's
  copy lists the core tokens plus its own currency tokens.
- **No opt-out.** Unlike the {ref}`GEP 9 <gep-9>` beartype claw, the unit check has no
  env-var escape hatch. It is data-independent and runs at build time (cacheable per
  `policy_date`), so it imposes no runtime cost that would justify one.
- **A migration is required.** Every node must declare a unit and every bare literal in
  mixed-unit arithmetic must be unit-tagged. This is delivered as one large,
  per-namespace gettsim PR; until it lands the check is exercised only on `mettsim`.

## Detailed Description

### The unit vocabulary

A declaration is one member of the **token vocabulary**. Its backbone is a closed core
enumeration — a `Unit` `StrEnum` shipped by `ttsim`, spelled identically in code
(`Unit.CURRENCY_FLOW`) and in YAML (`unit: CURRENCY_FLOW`):

| token                            | kind     | resolves to                      | typical use              |
| -------------------------------- | -------- | -------------------------------- | ------------------------ |
| `CURRENCY_FLOW`                  | flow     | `CURRENCY / period`              | wages, claims, benefits  |
| `CURRENCY_STOCK`                 | complete | `CURRENCY`                       | wealth, asset thresholds |
| `SHARE_FLOW`                     | flow     | `1 / period`                     | wealth-tax rate          |
| `YEARS`                          | complete | `year`                           | ages, durations          |
| `HOURS_FLOW`                     | flow     | `hour / period`                  | working hours            |
| `SQUARE_METERS`                  | complete | `meter ** 2`                     | dwelling size            |
| `HECTARES`                       | complete | `hectare`                        | land area                |
| `CURRENCY_PER_SQUARE_METER_FLOW` | flow     | `CURRENCY / meter ** 2 / period` | rent caps                |

The naming follows one principle: a bare token is **complete as written**; a `…_FLOW`
token **needs a period**, supplied by the name suffix or `reference_period`; and where
both kinds of a quantity exist, both are marked (`CURRENCY_STOCK` / `CURRENCY_FLOW`) — a
bare `CURRENCY` is deliberately unwritable, so no token can be misread as complete when
it is not. Every token has exactly one meaning, independent of any other field.

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
the unit. A dimensionless quantity (a share, a rate, a head count) declares **no unit at
all** — `unit=None` in code, `unit: null` in YAML — and the spelling `"dimensionless"`
is rejected. Declaring nothing is distinct from a *missing* declaration: an omitted
`unit=` is an error under mandatory units, an explicit `None`/`null` is a statement that
the quantity carries no dimension. A `null` declaration never combines with a period
source — `unit: null` next to a non-null `reference_period` is an error, not a
per-period rate. The per-period dimensionless quantity has its own token, `SHARE_FLOW`.

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
  `…_m` whose body computes a stock cannot be declared consistently.
- **Scalar parameters.** A `…_FLOW` token requires a non-null `reference_period`, which
  supplies the period; a complete or `null` declaration requires
  `reference_period: null`. A parameter whose *name* carries a time suffix
  (`lump_sum_deduction_y`) is thereby a flow with a second period source: the suffix
  must coincide with `reference_period`, and a complete or `null` token under a suffixed
  name fails.

Time is a first-class pint dimension. The hand-written arithmetic in
`unit_converters.py` is reimplemented so factors are sourced from pint
(`Quantity(1, "year").to("month")`), while the suffix auto-generation and naming are
kept verbatim.

### Dict parameters with heterogeneous leaves

A dict parameter whose leaves carry different units declares `unit:` as a **mapping from
leaf names to tokens** (or `null` for a dimensionless leaf). A flow leaf gets its period
from the leaf key's own time suffix, or — for keys that cannot carry one, such as
integer keys — from the dict-level `reference_period`:

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
- a non-null `reference_period` that no flow leaf consumes is dangling and fails,
  mirroring the scalar rule;
- mixed-period dicts are legal when each flow leaf carries its own suffix
  (`base_amount_m` next to `annual_bonus_y`): every period is explicit in a key, so
  nothing is left to convention.

In the dry-run, dict parameters become dicts of representative `Quantity`s (uniform for
a scalar `unit:`, per-leaf for a mapping), so bodies that subscript them are verifiable.
The mandatory-units check covers every leaf of the value active at the policy date; a
leaf missing from the `unit:` mapping is a *missing* declaration, a `null` leaf is a
dimensionless one.

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
declarations are single tokens (or `null` for a dimensionless axis), never mappings. The
single `reference_period` supplies the period of *every* flow axis; a `reference_period`
that no flow axis consumes is dangling and fails; a time suffix on the parameter's
*name* must coincide with the **output** axis — the suffix names what the parameter
yields.

The pair also resolves an ambiguity a single `unit:` cannot: *which* of a schedule's
numbers a currency conversion rescales. Scaling the input axis by $f_{in}$ and the
output axis by $f_{out}$ rescales the interval bounds by $f_{in}$, the intercepts by
$f_{out}$, and the order-$j$ coefficients by $f_{out} / f_{in}^j$. For an income-tax
schedule (both axes the same currency) the slopes are invariant and bounds and
intercepts move together; for a property-tax schedule (`HECTARES` in, currency out) the
bounds stay put and the slopes carry the full output factor. A single token could not
say which case applies. Lookup-table values convert by the output token; a
concrete-currency *input* axis on a lookup table is rejected — its domain is
integer-keyed (ages, birth years) and cannot be rescaled.

(gep-10-currency)=

### Currency

Currencies live in the framework as a `[currency]` dimension with concrete currencies
registered by downstream packages via
`register_currency(name, *, base=False, definition=None)`. `gettsim` registers `euro`
(base) and `DM = euro / 1.95583`; `mettsim` registers Gondor's `castar` (base) and the
Shire's `silver_penny = castar / 4`. Registration does two things: it provides the
**conversion factors**, with pint as the single source of truth for the rate; and it
derives the currency's **declaration tokens** — one concrete variant per
currency-dimensioned core token (`DM_STOCK`, `DM_FLOW`, `DM_PER_SQUARE_METER_FLOW`,
`EURO_*`, …) — extending the registering package's unit vocabulary.

**Union semantics.** The agnostic tokens (`CURRENCY_STOCK`, `CURRENCY_FLOW`, …) denote
the union of the registered currencies; for every dimensionality check a concrete token
means exactly what its agnostic counterpart means. The dry-run and the edge check
compare at the dimensionality level and never see a concrete currency — a DM-denominated
parameter feeds a currency-agnostic function without further ado, while adding Euros to
Euros per square meter is still caught. What a concrete token adds is **denomination**:
it names the currency the parameter's numbers are written in, which the build-time
conversion to the run currency reads off the declaration.

**Parameters must be concrete; functions must be agnostic.** A parameter's numbers are
written in *some* currency, so once a concrete currency is registered, an agnostic
`CURRENCY_*` token on a parameter is a build error — the declaration must name the
denomination (`DM_FLOW`, not `CURRENCY_FLOW`). Columns and functions may *only* declare
agnostic tokens (`unit=` accepts core-enumeration members and rejects concrete currency
tokens) — that is what makes them provably currency-agnostic.

**The run currency.** The `currency` knob defaults to the registered base currency
(`"euro"` for GETTSIM) and sets the currency of the input data and of the output. At
environment build, every currency-denominated number is converted from its declared
denomination to the run currency: scalar values, dict parameters leaf by leaf (each
currency leaf by its own token), schedules axis by axis, and lookup-table values (see
the per-axis rules above). The factors are baked in at build time; the numeric runtime
path stays single-currency.

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

The example system proves the mechanic end to end: mettsim's currency reform of 2020
replaces the Shire's silver penny with Gondor's castar at four pennies to the castar.
Pre-reform parameters are denominated in `SILVER_PENNY_*`; the wealth threshold and the
standard payroll schedule carry pure-redenomination changeover entries; a test asserts
the changeover is value-continuous in either run currency; and policy cases run in the
period-appropriate currency (pre-reform cases declare `currency: silver_penny` and keep
their numbers, while the same household run in both currencies yields exactly fourfold
currency outputs).

### The two-layer check

- **Layer 1 — DAG validity (data-independent).** Because return units are mandatory on
  every node, each function is checked in isolation: its inputs are wrapped in
  `Quantity`s of their *declared* units, the scalar body is executed in NumPy+pint, and
  the result must carry no dimensional error and match the declared output unit. An
  *edge-consistency* pass then confirms each producer's unit equals the consumer's
  declared expectation. No user data or fabricated dataset is needed. Layer 1 runs as a
  CI test over all policy dates and as an always-on build-time `fail_if` on the
  assembled environment.
- **Layer 2 — input compatibility (boundary).** Users *may* attach pint `Quantity`s to
  individual input columns. At the GEP-9 canonicalisation boundary the tag is a pure
  *assertion* against the `@policy_input`'s declared unit (currency must equal the run
  knob; period must match): a mismatch fails loudly. The quantity is then stripped to a
  bare array. Tags never convert.

`vectorization_strategy="not_required"` functions, which use raw `xnp` column ops, are
checked by running them in NumPy+pint on small synthetic arrays; a declared output unit
is the last-resort fallback.

**Booleans in the dry-run.** Boolean inputs are not quantities: they enter the dry-run
as bare `True`/`False`. Because branch selection hinges on them, a body with boolean
inputs is dry-run **twice** — once with all of them truthy, once falsy — so both arms of
the dominant guard pattern (`if exempt: return 0.0 else: <real arithmetic>`) are
verified. The falsy run is what concretely catches a stock×rate body whose rate is
missing its time component.

### Auto-generated nodes

Auto-generated nodes receive auto-assigned units: time-conversion variants inherit the
source's token **verbatim** — a flow token is period-invariant by construction, and the
variant's period is read off its own suffix; auto-aggregations derive their token from
the source and the aggregation type (SUM/MEAN/MIN/MAX preserve; COUNT, ANY, and ALL are
dimensionless), paralleling how {ref}`GEP 4 <gep-4>` resolves their types. An automatic
SUM over a boolean column is a head count and resolves to dimensionless; an explicit SUM
aggregation declares its unit (`unit=None` when the source is boolean). Where the
source's token pins down a concrete currency (a parameter), the derived node inherits
the **agnostic counterpart** — derived nodes are functions, they compute on
already-converted run-currency values.

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

### Pint-string declarations (the superseded draft scheme)

An earlier draft of this GEP — fully implemented and reviewed — declared units as
pint-parseable strings holding the **non-time part** of the unit, closed at the token
level (`unit="CURRENCY"` on `claim_of_child_y`, completed to `CURRENCY/year` by the `_y`
suffix at resolution time). It was DRY and automation-friendly, but it failed the
legibility test that anchors this design: *a declaration must read correctly to someone
who has not read the GEP*. Concretely, the same string meant different things depending
on other fields —

- `unit: CURRENCY` was a monthly flow on one parameter (`reference_period: Month`) and a
  stock on the next (`reference_period: null`);
- `unit: null` meant dimensionless — except next to `reference_period: Year`, where it
  silently meant `1/year`;
- and a string like `"CURRENCY"` *looks* like a complete pint unit while not being one,
  inviting exactly the misreading it invited (twice, during review, by the scheme's own
  author).

The kind tokens keep the scheme's structure (period-abstracted declarations, the same
resolution machinery, verbatim inheritance for auto-variants) while making the
incompleteness visible in the token's own name.

Two neighbouring corners of the design space were rejected at the same time:

- **Full units everywhere** (`unit="CURRENCY / year"`, checked redundantly against the
  suffix): locally legible, but repeats the period on hundreds of declarations, forces
  the variant generator to rewrite the time component, and makes every `_m`→`_y` rename
  touch the declaration. The kind tokens deliver the same legibility without the
  redundancy.
- **An enumeration of complete units** (the pre-GEP label vocabulary: "Euros", "Euros
  per Year", …): members multiply across periods (`EUROS_PER_YEAR`, `EUROS_PER_MONTH`,
  …) and the period stated in the label duplicates the suffix. Abstracting the period
  into the flow kind is what keeps the enumeration at eight members.

### Currencies outside the declarations (a `source_currency:` key)

An intermediate revision — also fully implemented — kept concrete currencies out of the
unit vocabulary entirely: parameters declared the agnostic token and named their legal
denomination in a separate top-level `source_currency:` key, and `EUR`/`DM` appeared
nowhere else. The appeal was a vocabulary that stays a single closed enumeration. It
fell for two reasons:

- it forced a **parallel declaration channel**: two keys jointly encode one fact (what
  the parameter's numbers mean), with cross-field consistency rules the reader must hold
  in their head — exactly the failure mode the kind tokens were introduced to kill; and
- it could not express a **changeover within one parameter's history**: a top-level
  `source_currency` denominates *all* dated entries, so a parameter whose pre-2002
  entries are legislated in DM and whose later entries are legislated in Euro had no
  faithful spelling.

Folding the currency into the token (`DM_FLOW`) makes a declaration self-contained, and
the per-entry override falls out of the ordinary YAML structure for free. The cost — the
vocabulary is no longer one static enumeration but core plus per-package currency tokens
— is contained: each package's JSON schema copy still enumerates its complete vocabulary
statically.

### A `"dimensionless"` unit string instead of `null`

Rejected. A `DIMENSIONLESS` token (or accepting pint's `"count"`/`"dimensionless"`
spellings) would be a second way to write what declaring *nothing* already says.
`unit=None` / `unit: null` is the single canonical form; the mandatory-units check
distinguishes it from an omitted declaration via a sentinel, so nothing is lost.

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
