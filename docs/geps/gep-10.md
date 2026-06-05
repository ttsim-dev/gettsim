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
- **unit** — a concrete measure within a dimension: `euro`, `month`, `meter**2`.
  Declared as a pint-parseable string in the new `unit=` field. The vocabulary is closed
  at the *token* level: a declaration may only combine units GETTSIM knows about;
  anything else is rejected.
- **dimensionless declaration** — a share, a rate, a head count declares *no* unit:
  `unit=None` in code, `unit: null` in YAML. Spelled-out synonyms (`"dimensionless"`,
  pint's built-in `count`) are rejected so there is exactly one way to write it.
- **flow** — a per-period quantity (Euros *per month*). Its time period is supplied by
  the name suffix (`_m`) for columns/functions or by `reference_period` for parameters.
- **CURRENCY** — the token used in a `unit=` string to mean "of the `[currency]`
  dimension, currency-agnostic". Checks compare at the dimensionality level; the
  concrete currency is resolved separately.
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
carries a `unit=` string for its **non-time** part. The flow period is supplied by the
name suffix (columns/functions) or by `reference_period` (parameters); intrinsically
temporal quantities (ages, durations) declare the time unit directly.

```python
@policy_function(unit="CURRENCY")  # name betrag_m -> resolved unit CURRENCY/month
def betrag_m(satz: float, anzahl: int) -> float:
    return satz * anzahl
```

```yaml
arbeitnehmerpauschbetrag:
  unit: CURRENCY        # non-time part
  reference_period: Year  # functional: supplies /year
  source_currency: DM   # stored in the legal currency; build-time -> run currency
  type: scalar
  1975-01-01:
    value: 564
```

A dimensionless parameter declares `unit: null`:

```yaml
beitragssatz:
  unit: null            # a rate is dimensionless
  reference_period: null
  type: scalar
  2024-01-01:
    value: 0.013
```

### Functions are currency-agnostic; one knob sets the currency

A new optional `main()` input `currency` (default `"euro"`) sets the currency of the
input data and of the output. Parameters carry their legal source currency and are
converted to the run currency at build time. Functions never mention a currency.

### Errors are loud and early

- A `unit=` string involving a unit GETTSIM does not know about fails at decoration time
  (functions) or load time (parameters).
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
- **The `unit`/`reference_period` metadata is repurposed.** `unit` becomes a
  pint-parseable string (the non-time part) and `reference_period` becomes *functional*
  (it supplies the flow period for parameters) rather than purely descriptive.
- **No opt-out.** Unlike the {ref}`GEP 9 <gep-9>` beartype claw, the unit check has no
  env-var escape hatch. It is data-independent and runs at build time (cacheable per
  `policy_date`), so it imposes no runtime cost that would justify one.
- **A migration is required.** Every node must declare a unit and every bare literal in
  mixed-unit arithmetic must be unit-tagged. This is delivered as one large,
  per-namespace gettsim PR; until it lands the check is exercised only on `mettsim`.

## Detailed Description

### The unit vocabulary

The vocabulary is closed at the **token** level: a declared unit may only combine units
GETTSIM knows about — the time units (`year`, `quarter_year`, `month`, `week`, `day`,
`hour`), the area units (`meter`, `hectare`), and `CURRENCY` plus the concrete
currencies registered via `register_currency`. Every other token is rejected at
declaration time, *including* pint built-ins that happen to live in an admissible
dimension (`count`, `percent`, prefixed units like `kilometer`): there is exactly one
way to write every unit. New units require a GEP amendment.

**Counting quantities are dimensionless**, following SI and pint convention. A
per-person parameter is plain `CURRENCY`; scaling it by a head count is a plain
multiplication that preserves the unit. A dimensionless quantity (a share, a rate, a
head count) declares **no unit at all** — `unit=None` in code, `unit: null` in YAML —
and the spelling `"dimensionless"` is rejected. Declaring nothing is distinct from a
*missing* declaration: an omitted `unit=` is an error under mandatory units, an explicit
`None`/`null` is a statement that the quantity carries no dimension.

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

`unit=` holds the non-time part. The flow period is supplied by the name suffix
(`_y/_q/_m/_w/_d`) for columns/functions or by `reference_period` for parameters.
Intrinsically temporal quantities (ages, durations) put the time unit directly in
`unit=` and carry no flow-suffix. The check enforces suffix ⟺ period agreement, so a
`_m`-named node that resolves to a per-year unit fails.

Time is a first-class pint dimension. The hand-written arithmetic in
`unit_converters.py` is reimplemented so factors are sourced from pint
(`Quantity(1, "year").to("month")`), while the suffix auto-generation and naming are
kept verbatim.

### Dict parameters with heterogeneous leaves

A dict parameter whose leaves carry different units declares `unit:` as a **mapping from
leaf names to complete unit strings** (or `null` for a dimensionless leaf);
`reference_period` must then be `null`, since each leaf's unit is already complete:

```yaml
schedule:
  unit:
    child_amount_y: CURRENCY / year
    max_age: year
  reference_period: null
  type: dict
  2024-01-01:
    child_amount_y: 3000.0
    max_age: 18
```

In the dry-run, dict parameters become dicts of representative `Quantity`s (uniform for
a scalar `unit:`, per-leaf for a mapping), so bodies that subscript them are verifiable.
The mandatory-units check covers every leaf of the value active at the policy date.

### Currency

Currencies live in the framework as a `[currency]` dimension with concrete units
registered by downstream packages via
`register_currency(name, *, base=False, definition=None)`. `gettsim` registers `EUR`
(base) and `DM = EUR / 1.95583`; `mettsim` registers its own currency. The `CURRENCY`
token in a `unit=` string denotes the `[currency]` dimensionality; the check compares
dimensions (so `EUR` and `DM` are compatible and `EUR + EUR/m**2` is not), and the
concrete currency is fixed by the `currency` knob at factor-baking time.

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
source's non-time unit with the period swapped; auto-aggregations derive their unit from
the source and the aggregation type (SUM/MEAN/MIN/MAX preserve; COUNT, ANY, and ALL are
dimensionless), paralleling how {ref}`GEP 4 <gep-4>` resolves their types. An automatic
SUM over a boolean column is a head count and resolves to dimensionless; an explicit SUM
aggregation declares its unit (`unit=None` when the source is boolean).

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

The schema copy at `docs/geps/params-schema.json` (the validation target for all German
parameter YAMLs) still describes the pre-GEP-10 label vocabulary; it is migrated
together with the YAML files in #1192, mirroring the updated schema shipped with ttsim.

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

### A `"dimensionless"` unit string instead of `null`

Rejected. With counts dimensionless, pint would happily parse `"count"`,
`"dimensionless"`, and `"CURRENCY / count"` (silently equal to `"CURRENCY"`) — three
spellings for two meanings, and a trap. Declaring *nothing* (`unit=None` / `unit: null`)
is the single canonical form; the mandatory-units check distinguishes it from an omitted
declaration via a sentinel, so nothing is lost.

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
