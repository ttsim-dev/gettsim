(gep-10)=

# GEP 10 — Value Types, Units, Grain, and Currency

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

This GEP introduces a static value-type system for every node, parameter, input,
generated operation, and result in TTSIM and GETTSIM. A value type records several
independent facts:

1. its physical unit;
1. its policy reference-period signature and conversion convention;
1. its semantic kind, such as number, boolean, share, count, identifier, or category;
1. the entity the value describes and the row domain on which it is represented;
1. any additional named tensor axes;
1. whether the value is extensive, intensive, statistic-derived, or a neutral modifier;
1. any calendar-point, duration, or ordinal semantics;
1. its currency denomination and provenance; and
1. whether it may be missing.

These axes are deliberately not collapsed into one Pint expression. Pint is responsible
only for physical-unit algebra and physical conversion. Policy periods, grouping levels,
identifiers, booleans, counts, storage grain, tensor axes, calendar ordinals, extensity,
and currency provenance are separate type components with separate rules.

TTSIM validates declarations, graph edges, supported policy-function bodies, joins,
aggregations, reductions, schedules, date regimes, rounding rules, and typed data
boundaries. The body checker is a conservative abstract interpreter over a documented
Python subset. It is not described as executing a proof of arbitrary Python. Every
active node and date regime receives an auditable evidence status, and every assertion
or exemption is reported separately from verified code.

For historical currencies, each policy regime is evaluated in the statutory denomination
in which its parameters and coefficients are written. Input and output conversion occurs
at explicit boundaries. Coefficients with inverse-currency or period units declare those
units; statutory-currency evaluation is not a substitute for dimensional correctness.

## Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and
**OPTIONAL** in this document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in
capital letters.

## Motivation and scope

TTSIM policy code currently manipulates ordinary Python, NumPy, and JAX values. Runtime
dtypes can distinguish integers, floating-point numbers, and booleans, but they cannot
by themselves distinguish monthly income from wealth, a household total from a person
amount, a household ID from a tax-unit ID, a calendar year from an age, or a share from
a count.

A reliable validation system must address six independent problem classes.

1. **Physical and period consistency.** Arithmetic must reject incompatible physical
   measures and incompatible policy reference periods. A stock of wealth must not
   silently become a monthly flow. Rent per square meter must not be added to total
   rent.
1. **Semantic-kind consistency.** A boolean, identifier, category, share, probability,
   rate, count, and unrestricted number are not interchangeable merely because each can
   be stored in an integer or floating-point array.
1. **Relational, grain, and axis consistency.** Group membership, keys, row domains,
   broadcast values, joins, cardinality, aggregation, and local tensor axes are
   structural properties. They are not physical dimensions and must not be represented
   as Pint denominators.
1. **Extensity consistency.** Sums, means, extrema, counts, and per-capita
   transformations have different semantics. A mean remains a statistic of the target
   group; it does not become a person-level value because a symbolic group denominator
   happened to cancel.
1. **Calendar consistency.** Absolute dates, year points, year-month points, durations,
   month-of-year ordinals, and day-of-month ordinals support different operations. In
   particular, February and the fifteenth day are not context-free affine points.
1. **Currency and provenance consistency.** A monetary value has a physical currency
   dimension, a denomination, an origin or effective-date rule, and an ordering relative
   to statutory rounding. Historical statutory coefficients may have inverse-currency
   units even when the law prints them as bare numbers.

This GEP covers:

- the canonical static type of scalar and array leaves, plus compound structure and
  mapping types;
- declarations on policy functions, policy inputs, parameters, structured values,
  schedules, rounding specifications, generated nodes, and typed data;
- type rules for supported scalar and vectorized expressions;
- relational operations, including joins, gathers, broadcasts, allocations, and
  aggregations;
- policy reference-period conversion;
- calendar types and operations;
- statutory and data currency handling;
- validation over every distinct policy-date regime;
- evidence, coverage, exceptions, and conformance requirements; and
- the migration of TTSIM, METTSIM, and GETTSIM.

The GEP does **not** claim to prove that a policy formula implements the law, that a
numerical algorithm is stable, that values are finite, or that arbitrary Python is safe.
It provides a sound static contract for the documented expression language and explicit
evidence for the parts it cannot verify.

The naming conventions and generated period conversions in {ref}`GEP 1 <gep-1>`,
grouping and identifier declarations in {ref}`GEP 2 <gep-2>`, DAG and aggregation
concepts in {ref}`GEP 4 <gep-4>`, rounding in {ref}`GEP 5 <gep-5>`, and runtime
user/canonical type split in {ref}`GEP 9 <gep-9>` remain in force except where this GEP
explicitly refines them.

(gep-10-usage)=

## Usage and impact

### Users of existing policy environments

Users may continue to call `main()` with ordinary arrays, mappings, or a DataFrame.
Untyped data remain supported, but the resulting evidence report records that their
non-dtype semantics were **assumed from the policy node**, not independently verified
from the input.

A user may select the denomination of untyped monetary input and computed output with
`data_currency`. The default for GETTSIM remains Euro.

```python
results = main(
    policy_date_str="1999-01-01",
    data_currency="EUR",
    # Other arguments omitted.
)
```

For this run, GETTSIM:

1. resolves the 1999 policy environment and its complete value types;
1. converts monetary input from Euro to the statutory 1999 denomination;
1. evaluates the policy using statutory parameters and coefficients without rewriting
   their legal numerical values;
1. applies statutory rounding in the concrete denomination declared by each rounding
   rule; and
1. converts computed monetary results to Euro after statutory computation is complete.

Requested raw inputs are returned unchanged. Requested parameters retain their statutory
currency and provenance unless the caller explicitly asks for a converted presentation
value.

(gep-10-trees)=

### Fully typed input and output

Users who want the input boundary checked may wrap every leaf in `TypedColumn`. The
wrapper contains ordinary values and a complete source `ValueSpec`.

```python
from gettsim import InputData, MainTarget, TTTargets, main
from gettsim.tt import Entity, Extensity, Index, Key, Period, Q, TypedColumn

input_tree = {
    "p_id": TypedColumn(
        values=[0, 1],
        value_type=Q.identifier(Key.P_ID),
    ),
    "bg_id": TypedColumn(
        values=[0, 0],
        value_type=Q.identifier(Key.BG_ID),
    ),
    "geburtsjahr": TypedColumn(
        values=[1980, 2015],
        value_type=Q.calendar_year_point(
            subject=Entity.PERSON,
            index=Index.unique(Entity.PERSON),
        ),
    ),
    "einkommen_m": TypedColumn(
        values=[2000.0, 0.0],
        value_type=Q.money(
            period=Period.per_month(),
            subject=Entity.PERSON,
            extensity=Extensity.EXTENSIVE,
            currency="EUR",
            index=Index.unique(Entity.PERSON),
        ),
    ),
}

results = main(
    main_target=MainTarget.results.tree_with_value_types,
    policy_date_str="2025-01-01",
    input_data=InputData.tree_with_value_types(input_tree),
    tt_targets=TTTargets(tree={"transfer": {"betrag_m": None}}),
)
```

The boundary requires exact agreement on semantic kind, subject, extensity, calendar
semantics, key domain, and compatible index and local-axis representation. Physical
units and period specifications must be compatible or connected by registered
conversions. A concrete input currency may differ from the computation currency and is
converted at the boundary. A key domain, boolean kind, category domain, or subject grain
is never converted.

`MainTarget.results.tree_with_value_types` returns each computed leaf as a `TypedColumn`
with the fully resolved value type and concrete output denomination. Ordinary result
targets continue to return bare values.

### Contributors: policy functions and inputs

A policy function declares a `value_type`, not a single compositional unit token.

```python
from ttsim.tt import Entity, Extensity, Period, Q


@policy_input(
    value_type=Q.money(
        period=Period.per_month(),
        subject=Entity.BG,
        extensity=Extensity.EXTENSIVE,
    )
)
def regelsatz_m_bg() -> float: ...


@policy_input(
    value_type=Q.money(
        period=Period.per_month(),
        subject=Entity.BG,
        extensity=Extensity.EXTENSIVE,
    )
)
def mehrbedarf_m_bg() -> float: ...


@policy_function(
    value_type=Q.money(
        period=Period.per_month(),
        subject=Entity.BG,
        extensity=Extensity.EXTENSIVE,
    )
)
def betrag_m_bg(regelsatz_m_bg: float, mehrbedarf_m_bg: float) -> float:
    return regelsatz_m_bg + mehrbedarf_m_bg
```

`Q.money()` uses the abstract `STATUTORY` currency in code-side declarations. At a
policy date, the policy environment resolves it to the concrete statutory denomination.
The `_m` suffix must agree with the period signature, and `_bg` must agree with the
declared subject where GEP 1 says the suffix denotes the subject. Suffixes are
consistency checks; they do not supply missing type axes and do not encode storage
layout.

Booleans are declared as booleans, not as dimensionless numbers.

```python
@policy_input(value_type=Q.boolean(subject=Entity.PERSON))
def eligible() -> bool: ...


@policy_function(
    value_type=Q.money(
        period=Period.per_month(),
        subject=Entity.PERSON,
        extensity=Extensity.EXTENSIVE,
    )
)
def transfer_m(eligible: bool, amount_m: float) -> float:
    return amount_m if eligible else 0
```

The condition is checked as `BOOLEAN`. The zero arm is a typed zero literal that adopts
the type of `amount_m`. A currency value, ID, count, or category used directly as the
condition is an error in both scalar and vectorized code.

### Contributors: explicit group operations

Grouping is expressed through typed relations rather than physical-unit denominators.

```python
rent_m_hh = aggregate(
    rent_m_person,
    relation=PERSON_TO_HH,
    how=SUM,
)

average_rent_m_hh = mean_per_member(
    rent_m_hh,
    count=persons_in_hh,
    relation=PERSON_TO_HH,
)

rent_allocation_m_person = allocate_equal(
    rent_m_hh,
    count=persons_in_hh,
    relation=PERSON_TO_HH,
)
```

`rent_m_hh` is an extensive monthly monetary amount with subject `HH`.
`average_rent_m_hh` is an intensive “per member” statistic that remains a property of
the household and is stored once per household. `rent_allocation_m_person` is an
extensive person amount whose allocations sum back to the household total. All three
retain the physical currency unit and monthly period. No `[hh]` dimension is created or
cancelled, and storage grain is not confused with allocation incidence.

A group value aligned to person rows is produced by a typed gather or broadcast.

```python
allowance_m_person = gather(
    foreign_key=hh_id,
    primary_key=hh_table_id,
    target=allowance_m_hh,
    cardinality=MANY_TO_ONE,
    on_missing=MISSING,
)
```

The key domains, primary-key uniqueness, declared cardinality, missing policy, target
type, and source and target row domains are validated. A monetary value cannot be used
as a key, and an `Id[HH]` cannot be joined to an `Id[BG]`.

### Contributors: coefficients with inverse units

Statutory evaluation in a concrete currency does not make fitted or statutory
coefficients dimensionless. Coefficients declare their complete mathematical type.

```yaml
wohngeld_coefficients:
  type: dict
  value_type:
    a:
      unit: one
      period: stock
      kind: number
      subject: global
      extensity: neutral
    b:
      unit: 1 / currency
      period: month
      kind: number
      subject: global
      extensity: neutral
      currency: EUR
    c:
      unit: 1 / currency ** 2
      period: month ** 2
      kind: number
      subject: global
      extensity: neutral
      currency: EUR
  2024-01-01:
    a: 0.04
    b: 0.0002
    c: 0.0001
```

Multiplying `b` by an `EUR_PER_MONTH` income, or `c` by the square of that income,
produces a dimensionless number. Declaring either coefficient as a bare dimensionless
number is rejected. A later statutory-currency regime supplies new dated coefficient
values and matching concrete currency declarations.

## Backward compatibility

This GEP deliberately replaces the one-dimensional compositional-unit model.

- Bare arrays and the DataFrame or mapping interfaces remain supported. Their semantic
  types are assumed from the policy environment and reported as unverified input
  assumptions.
- `data_currency` continues to default to `EUR` in GETTSIM.
- The legacy `unit=` decorator argument and `TTSIMUnit` builder MAY be supported for one
  deprecation cycle as a migration adapter. The adapter may recover only the physical
  unit and a simple standard reference-period signature where that mapping is
  unambiguous. It MUST NOT infer a period convention, semantic kind, subject, extensity,
  key or category domain, row index, local tensor axes, calendar semantics, currency
  provenance, or nullability from a grouping denominator, suffix, runtime dtype, or
  example value.
- `PER_HH`, `PER_BG`, and other group suffixes are removed from physical-unit syntax.
  Grouping is represented by `subject`, `index`, relations, and aggregation metadata.
- `DIMENSIONLESS` is no longer a sufficient declaration. Contributors must declare
  whether a value is a number, boolean, share, probability, rate, count, identifier, or
  category.
- `verify_units=False` is removed. A whole-body exemption requires a structured
  `ValidationExemption` and remains visibly unverified.
- `cast_ttsim_unit` is deprecated. Dimensioned literals, alignment, semantic
  reassignment, and last-resort type assertions use separate operations with structured
  justification.
- Existing functions, policy inputs, parameters, schedules, structured fields, rounding
  rules, joins, hand-written aggregations, and generated nodes require complete resolved
  value types before a policy package can claim conformance.
- Naming suffixes remain mandatory where required by GEP 1, but they are consistency
  checks and never the sole source of a value type.

A project MAY stage migration behind a compatibility flag, but it MUST NOT describe a
legacy adapter result as body-verified or fully typed unless every canonical axis has
been resolved and validated.

## Detailed description

(gep-10-principles)=

### Design principles

The implementation MUST follow these principles.

1. **Independent facts use independent type axes.** A household is an entity domain, not
   a physical denominator. A boolean is a semantic kind, not a dimensionless number.
   February is a calendar ordinal, not an affine month point.
1. **The canonical type is explicit.** Convenience constructors may fill documented
   defaults, but every active leaf is resolved to a complete `ValueSpec` and every
   compound producer to a complete `TypeSpec` before validation.
1. **Operations are conservative.** An operation without a registered type rule fails.
   It does not silently preserve the input type, discard an argument, or fall back to a
   generic dimensionless result.
1. **Scalar and vectorized code share one rule table.** Python operators, `xnp`
   operations, and generated graph operations call the same type-rule implementation.
1. **Relational transformations are explicit.** Broadcast, gather, join, aggregation,
   deduplication, allocation, and per-capita transformations carry relation and
   cardinality metadata.
1. **Assertions are evidence, not verification.** A type assertion or whole-body
   exemption is reported as such and cannot raise verified-body coverage.
1. **All policy regimes are checked.** Validation uses the maximal date partition
   induced by functions, parameters, schemas, units, currencies, rounding rules, and
   generated nodes.
1. **Registries are environment-local.** Currencies, entities, categories, keys,
   primitive signatures, and period systems belong to an immutable `UnitSystem` or
   policy environment. Process-global mutation is not part of the correctness contract.
1. **Claims match evidence.** TTSIM may claim sound checking only for the documented
   expression subset. Unsupported or exempt code remains visible in the evidence report.

(gep-10-guarantee)=

(gep-10-limitations)=

### Validation guarantee and claim vocabulary

For a node marked `BODY_VERIFIED`, the implementation guarantees the following,
conditional on its stated trust boundary: if typed inputs satisfy their declared
contracts, registered relations and primitive signatures are correct, and execution
stays within the supported language, then every syntactic execution path is type safe
under this GEP and every return is compatible with the declared result `TypeSpec`. “Type
safe” means that no operation violates the physical, period, semantic-kind, subject,
index, local-axis, extensity, calendar, currency, or nullability rules.

This guarantee is deliberately conditional. It does not prove that:

- the formula implements the statute or an economic model correctly;
- an asserted relation is true of malformed runtime data unless its value constraints
  are checked;
- a result lies in an economically valid range;
- floating-point evaluation is stable or finite;
- an external primitive's implementation matches its registered signature; or
- code outside the supported language has been analyzed.

The public claim vocabulary is normative.

| Claim                 | Minimum evidence                                                                                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| type-resolved package | every active leaf and interval has a complete `ValueSpec`; no `UNRESOLVED_TYPE`                                                                                     |
| body-verified package | every ordinary body is `BODY_VERIFIED`; every generated node is `DERIVED_BY_GENERATED_RULE`; trusted external primitives are enumerated                             |
| boundary-verified run | the package is body verified and every supplied input leaf is independently typed and validated                                                                     |
| GEP-10 fully verified | body-verified package, complete maximal date partition, no body exemptions, no `TYPE_ASSERTION_USED` qualifier, and a boundary-verified run for the claimed dataset |

A package using untyped input may be body verified, but the run is not boundary
verified. A package containing a reviewed body exemption may be type resolved, but it is
not body verified or fully verified. User interfaces and release notes MUST use these
terms or equally precise terms; they MUST NOT collapse them into “unit checked.”

(gep-10-terminology)=

### Terminology

| Term                  | Meaning                                                                                                                                                                                                        |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| physical unit         | Algebraic measure handled by Pint, such as currency, square meters, hectares, or working hours.                                                                                                                |
| period specification  | Symbolic policy reference-period factor plus the convention and provenance governing conversion, such as a standard annualized month or an actual-day statutory rule. It is distinct from calendar duration.   |
| semantic kind         | Meaning that is not captured by physical units, such as boolean, share, count, identifier, or category.                                                                                                        |
| subject               | Entity the value describes, such as a person, household, or tax unit.                                                                                                                                          |
| index                 | Relational row domain and representation on which a value is stored or evaluated.                                                                                                                              |
| local axis            | Named non-row tensor dimension, such as choice, coefficient order, or stochastic node, with a typed coordinate and reduction contract.                                                                         |
| extensity             | Whether values add over disjoint subject entities (`EXTENSIVE`), are pointwise nonadditive (`INTENSIVE`), are reducer-selected statistics (`STATISTIC`), or act as neutral constants or modifiers (`NEUTRAL`). |
| relation              | Typed mapping between entity domains, including key domains and cardinality.                                                                                                                                   |
| calendar point        | A coordinate on an affine calendar axis, such as a year or absolute date.                                                                                                                                      |
| calendar ordinal      | A cyclic or contextual coordinate, such as month of year or day of month.                                                                                                                                      |
| calendar duration     | A displacement on a calendar axis, such as years or days.                                                                                                                                                      |
| statutory currency    | Concrete denomination in which the applicable law writes monetary parameters and coefficients.                                                                                                                 |
| data currency         | Concrete denomination of user-provided monetary data or requested computed results.                                                                                                                            |
| currency provenance   | Rule identifying where a denomination comes from and which effective date controls it.                                                                                                                         |
| verification evidence | Machine-readable record of how a node's type was obtained and what was checked.                                                                                                                                |
| assertion             | Explicit refinement of unresolved or deliberately broad type information that the checker cannot derive; it cannot overwrite a known conflicting type.                                                         |
| exemption             | Structured decision not to body-check a function. Its declared result remains a consumer contract but is not verified.                                                                                         |

(gep-10-valuespec)=

(gep-10-vocabulary)=

### Canonical value type

Every scalar or array leaf, parameter leaf, schedule coordinate, structured field,
intermediate expression, generated leaf, and result leaf resolves to the following
conceptual immutable type.

```python
@dataclass(frozen=True)
class ValueSpec:
    unit: PhysicalUnit
    period: PeriodSpec
    kind: SemanticKind
    subject: SubjectSpec
    extensity: Extensity
    index: IndexSpec
    axes: tuple[AxisSpec, ...]
    calendar: CalendarSpec | None
    currency: CurrencySpec
    nullable: bool
```

The implementation may use different internal class names, but the fields and their
semantics are normative. The resolved form MUST contain all fields. `None`, omitted
fields, or legacy aliases may exist only before resolution, except that `calendar=None`
is the resolved value for noncalendar kinds and `axes=()` is the resolved value for a
leaf with no local tensor axes.

Compound values use a structural type rather than pretending that a dictionary or
callable has a physical unit.

```python
@dataclass(frozen=True)
class StructSpec:
    fields: Mapping[str, "TypeSpec"]


@dataclass(frozen=True)
class MappingSpec:
    inputs: tuple[ValueSpec, ...]
    output: "TypeSpec"


TypeSpec = ValueSpec | StructSpec | MappingSpec
```

Every compound leaf is therefore checked, while the compound container itself has no
fake unit, subject, or extensity. A value type is not a runtime wrapper around every JAX
array. It is static graph metadata and an abstract-interpreter value. Typed input and
output wrappers expose the same metadata at the boundary.

(gep-10-hours)=

#### Physical unit

`PhysicalUnit` is a Pint unit expression over a policy-package registry. It contains
only physical measures. The registry includes at least:

- dimensionless one;
- abstract currency;
- area, including square meter and hectare;
- working hours; and
- additional package-defined physical measures.

Entity domains, persons, groups, booleans, counts, identifiers, calendar points, and
policy reference periods MUST NOT be Pint base dimensions.

Concrete denominations such as EUR and DM are recorded in `CurrencySpec`; they are not
separate physical dimensions. Both have physical unit `currency`.

Examples:

| Quantity                                        | `unit`                    | period signature |
| ----------------------------------------------- | ------------------------- | ---------------- |
| wealth                                          | `currency`                | `stock`          |
| monthly income                                  | `currency`                | `per_month`      |
| hourly wage                                     | `currency / work_hour`    | `stock`          |
| weekly working hours                            | `work_hour`               | `per_week`       |
| monthly rent per square meter                   | `currency / square_meter` | `per_month`      |
| annual rate applied to a stock                  | `one`                     | `per_year`       |
| Wohngeld coefficient multiplying monthly income | `1 / currency`            | `month`          |

Pint supplies physical equivalence and physical conversion factors. It MUST NOT decide
policy reference periods or conversion conventions, semantic kind, subject, row index,
local tensor axes, extensity, calendar algebra, currency provenance, or nullability.

(gep-10-periods)=

#### Policy reference periods

`PeriodSpec` contains a symbolic signature and a conversion convention.

```python
@dataclass(frozen=True)
class PeriodSpec:
    signature: PeriodSignature
    convention: PeriodConvention
```

`PeriodSignature` is a multiplicative expression over one policy-reference-time
dimension, with named units `YEAR`, `QUARTER`, `MONTH`, `WEEK`, and `DAY`. Its canonical
exponents are signed integers. The named units are convertible under a registered
convention; they are not independent dimensions. The signature is separate from physical
time and from calendar duration.

```text
stock       = 1
per_month   = MONTH^-1
per_year    = YEAR^-1
month       = MONTH
per_month_2 = MONTH^-2
```

The general algebra is required because correct coefficients may carry a period in the
numerator or higher powers. Public convenience constructors SHOULD cover common stock
and flow cases.

`PeriodConvention` identifies why a conversion factor is valid. Required forms are:

```text
NONE
STANDARD_ANNUALIZED[rule_id]
CALENDAR_ACTUAL[rule_id]
STATUTORY[rule_id]
INHERITED[source_node]
```

Stocks use `NONE`. A standard annualized convention may define an exact context-free
ratio such as 12 standard months per standard year. An actual-day or statutory proration
rule may depend on a complete date interval, entitlement days, leap years, or another
legal convention and therefore uses an explicit graph primitive rather than a
context-free generated conversion.

A policy package owns an immutable `PeriodSystem` containing named conventions, exact
factors, valid source and target signatures, and provenance. A generated GEP 1
conversion is permitted only when the source and target `PeriodSpec` are connected by a
registered context-free rule. The conversion node records the rule identifier. It MUST
NOT use a convenient fixed ratio for a quantity declared under an actual-calendar or
statute-specific convention.

Multiplication and division combine period signatures algebraically and retain enough
convention provenance to determine whether factors cancel. Convention compatibility is
checked before period powers cancel; a standard monthly amount and an actual-day
inverse-month coefficient do not become valid merely because their symbolic exponents
sum to zero. When compatible period powers cancel to stock, the result convention is
`NONE` and derivation evidence retains the source conventions. Addition, subtraction,
branch unification, ordering, minimum, maximum, and clipping require equivalent
signatures and compatible conventions after an explicitly permitted conversion.

Let `P(source -> target)` be the exact numerical factor registered for one unit of the
source period convention expressed in the target convention. For period exponent `e`,
conversion multiplies the magnitude by `P(source -> target)^e`. This rule applies to
inverse and higher-power coefficients as well as simple flows.

The checker MUST reject a stock returned as a flow, even when both use currency. It MUST
also reject an untyped coefficient whose missing inverse period happens to be
numerically harmless in one currency regime.

(gep-10-kinds)=

#### Semantic kinds

The minimum closed set of semantic kinds is:

```text
NUMBER
BOOLEAN
SHARE
PROBABILITY
RATE
COUNT[entity_domain]
IDENTIFIER[key_domain]
CATEGORY[category_domain]
CALENDAR_POINT[axis]
CALENDAR_DURATION[axis]
CALENDAR_ORDINAL[axis]
```

Policy packages MAY register additional semantic kinds with explicit operation rules.
They MUST NOT treat an unknown kind as `NUMBER` or `DIMENSIONLESS`.

The built-in kinds have these meanings.

- `NUMBER` is a numeric quantity whose physical unit and period carry its dimensional
  content.
- `BOOLEAN` is a truth value. It alone may appear in a truth context.
- `SHARE` is a dimensionless multiplicative fraction. Optional boundary validation may
  require it to lie in a declared range, commonly `[0, 1]`.
- `PROBABILITY` is a dimensionless probability. It has stricter aggregation and range
  semantics than a generic share.
- `RATE` is a dimensionless or dimensioned multiplicative rate, possibly with a
  non-stock period signature.
- `COUNT[E]` records which entity domain is being counted. Count values are intended to
  be integer-valued and nonnegative; that value constraint is checked at typed
  boundaries and by generated count operations, rather than being inferred from storage
  dtype. A count of persons is not a count of households.
- `IDENTIFIER[K]` is a key in domain `K`. It supports equality, missingness, and
  relational operations, not arithmetic.
- `CATEGORY[C]` is a member of a declared finite or open category domain `C`. Categories
  from different domains are incompatible.
- Calendar kinds are defined in {ref}`Calendar types <gep-10-calendar>`.

`BOOLEAN`, `IDENTIFIER`, `CATEGORY`, and `COUNT` are never inferred from a dimensionless
Pint unit. They must be declared or derived by a typed operation. `COUNT[E]` supports
equality, ordering, and addition or subtraction only with `COUNT[E]` at compatible
subject and index. A package that requires subtraction to preserve nonnegativity
attaches a value constraint or uses a registered `count_difference()` primitive. Counts
do not enter unrestricted numeric arithmetic or stand in for shares, rates, or
identifiers.

The phrase **numeric kind** in this GEP means `NUMBER`, `SHARE`, `PROBABILITY`, `RATE`,
or `COUNT[E]` only where the named operation has a rule for that kind. There is no
implicit coercion from these kinds to `NUMBER`. In particular, physical
dimensionlessness does not authorize arithmetic between a probability, count, and
unrestricted number.

(gep-10-subject-index)=

(gep-10-levels)=

#### Subject and index

`subject` identifies the legal or statistical entity a value describes. `SubjectSpec`
supports `GLOBAL`, one registered entity domain, or a registered composite subject.
Built-in entity domains include `PERSON` and grouping domains such as `HH`, `BG`, `FG`,
`SN`, `EG`, `EHE`, and `WTHH`.

`index` identifies where values are represented. It contains a relational row domain and
a representation contract. The minimum representations are:

```python
Index.scalar()
Index.unique(Entity.PERSON)
Index.unique(Entity.HH)
Index.broadcast(
    source=Entity.HH,
    rows=Entity.PERSON,
    key=Key.HH_ID,
)
Index.gathered(
    source=Entity.HH,
    rows=Entity.PERSON,
    key=Key.HH_ID,
    cardinality=MANY_TO_ONE,
)
```

A subject and an index answer different questions. A household amount repeated on every
person row still has subject `HH`; its index records person rows and a certified
household-key broadcast. This distinction lets the checker reject double-counting a
repeated household value.

Scalar policy parameters use `Index.scalar()` by default. A scalar may be broadcast to
an array index when its subject and semantic role are compatible with the operation.
Array-to-array pointwise operations require aligned row domains. Alignment across
domains occurs only through a typed relation.

The environment MUST know whether an array is unique at its logical source domain or
repeated. It MUST NOT infer uniqueness merely from a suffix or from observed example
values.

`axes` contains every non-row tensor dimension in storage order. Each `AxisSpec` has a
nominal name, a coordinate `ValueSpec` or finite domain, an ordering contract, a
broadcast rule, and the reducers permitted on that axis. Examples include `choice`,
`stochastic_node`, `coefficient_order`, and `age_band`. Pointwise operations require
identical local axes or a registered broadcast. Selecting, stacking, transposing, or
reducing an axis produces a new explicit axis specification. A raw integer `axis=1` is
resolved against this metadata; an untyped axis is rejected.

The relational row index and local tensor axes are independent. A person-row array with
a choice axis has a person `IndexSpec` and one `AxisSpec`; reducing choices does not
aggregate persons, and aggregating persons does not silently reduce choices.

Pointwise operations combine subjects and row indices by the following fail-closed rules
after any explicit gather, broadcast, or scalar expansion has been represented in the
graph.

| Operands                                                                                                    | Result subject and row index                                                          |
| ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| same non-global subject, aligned row index                                                                  | preserve the common subject and aligned index                                         |
| one `GLOBAL`, `NEUTRAL`, scalar operand                                                                     | preserve the other operand's subject and row index                                    |
| one registered neutral or intensive modifier explicitly gathered or broadcast into the other operand's rows | preserve the modified operand's subject and row index; retain relation provenance     |
| different extensive subjects                                                                                | error; use aggregation, allocation, reassignment, or another named semantic primitive |
| different nonmodifier subjects                                                                              | error even when row lengths and dtypes happen to match                                |

A scalar broadcast changes representation only. It never changes a non-global subject,
key domain, or extensity. A relation-mediated broadcast can align rows without
transferring ownership. The primitive's semantic signature decides whether a gathered
value is a modifier, a comparison threshold, a selection condition, or an amount that
still requires allocation.

(gep-10-extensity)=

#### Extensity

`Extensity` has at least five values:

```text
EXTENSIVE
INTENSIVE
STATISTIC
NEUTRAL
NOT_APPLICABLE
```

- `EXTENSIVE` values add over disjoint subject entities. Examples include personal
  income, household rent totals, wealth, and working hours.
- `INTENSIVE` values are pointwise quantities that do not add over disjoint entities.
  Examples include shares, averages, wage rates, prices, and densities.
- `STATISTIC` values are reducer-selected or order-dependent summaries at a target
  subject, such as minima, maxima, quantiles, and a policy-defined first observation.
  They are not totals and are not automatically pointwise modifiers. The derivation
  evidence records the reducer.
- `NEUTRAL` values are constants, thresholds, coefficients, or modifiers whose use may
  preserve the extensity of another operand.
- `NOT_APPLICABLE` is used for booleans, identifiers, categories, and calendar values.

For compatible numeric additions, extensity combines as follows. The table is symmetric
in its left and right operands.

| Left      | Right                  | Result                                            |
| --------- | ---------------------- | ------------------------------------------------- |
| extensive | extensive              | extensive, if subjects match                      |
| extensive | neutral                | extensive, if subjects are compatible             |
| intensive | intensive              | intensive, if subjects match                      |
| intensive | neutral                | intensive, if subjects are compatible             |
| statistic | statistic              | statistic, if subjects and indices match          |
| statistic | neutral                | statistic, if subjects are compatible             |
| neutral   | neutral                | neutral                                           |
| extensive | intensive or statistic | error                                             |
| intensive | statistic              | error unless a named primitive defines the result |

A parameter threshold may be `NEUTRAL` while carrying subject `PERSON`; comparison or
addition to a personal amount is then permitted without making the parameter aggregable.
Aggregation rules use extensity explicitly and are defined separately.

Generic numeric multiplication and division use the following default extensity rules
after semantic-kind, subject, index, and local-axis compatibility has been established.

| Operation                                        | Default result                                                            |
| ------------------------------------------------ | ------------------------------------------------------------------------- |
| `NEUTRAL * X`, `X * NEUTRAL`, `X / NEUTRAL`      | extensity of `X`                                                          |
| `EXTENSIVE * INTENSIVE`, `EXTENSIVE / INTENSIVE` | `EXTENSIVE` when the intensive operand is a registered pointwise modifier |
| `INTENSIVE * INTENSIVE`, `INTENSIVE / INTENSIVE` | `INTENSIVE` only when the semantic-kind rule admits the operation         |
| `STATISTIC * INTENSIVE`, `STATISTIC / INTENSIVE` | `STATISTIC` only when the intensive operand is a registered modifier      |
| `STATISTIC * STATISTIC`, `STATISTIC / STATISTIC` | requires an explicit registered rule                                      |
| `EXTENSIVE * EXTENSIVE`                          | error unless a named primitive defines the resulting meaning              |
| `EXTENSIVE / EXTENSIVE`                          | requires a declared result kind and rule, commonly a share or rate        |
| `NEUTRAL / X`                                    | requires an explicit registered rule                                      |

These defaults make wages times hours and prices per area times area extensive while
rejecting a meaningless product of two totals. A primitive may define another result
only with an explicit signature and tests.

(gep-10-currency-type)=

#### Currency specification and provenance

`CurrencySpec` is required whenever the physical unit contains a nonzero power of
currency. It has the conceptual forms:

```text
NONE
STATUTORY(policy_date)
CONCRETE(code, origin, stage)
DATA(run_argument_or_column_tag)
INHERITED(source_node, origin_date_rule)
PRESENTATION(source_node, target_code, conversion_rule)
```

`NONE` is required when the physical unit has no currency component. `STATUTORY` is used
by currency-agnostic code-side declarations and resolves to a concrete denomination for
a policy regime. Parameters, coefficients, rounding magnitudes, and typed input columns
use a concrete currency or another explicit provenance rule.

`origin` records enough information to answer why a denomination applies. At minimum it
identifies one of:

- the parameter effective date;
- the current policy date;
- the source data tag or `data_currency` assumption;
- a carried value's originating policy period; or
- an explicit conversion node and rate definition.

A single ordinary numeric column MUST NOT contain row-wise mixed denominations. A
package that needs mixed currencies must use a tagged union type and an explicit
normalization operation; that extension is outside the required first implementation.

Currency compatibility is checked independently of physical-unit equivalence. Two
monetary values may both have physical unit `currency` and still be incompatible until a
conversion node aligns their concrete denominations and provenance. Denominations are
aligned before currency powers cancel: multiplying an EUR amount by a DM
inverse-currency coefficient does not become valid merely because Pint would produce a
dimensionless physical unit. After compatible currency factors cancel to exponent zero,
the result has `CurrencySpec.NONE`, while derivation evidence retains the denominations
and conversion rules used.

(gep-10-nullability)=

#### Nullability and typed missing values

`nullable` records whether a value may be absent. Missingness is not represented by an
arbitrary numeric sentinel.

- An optional identifier has type `IDENTIFIER[K]` with `nullable=True`.
- `MISSING_ID[K]` is a typed missing sentinel for identifier domain `K`.
- `MISSING` in a branch or join fallback is a polymorphic missing literal that may unify
  only with a nullable expected type.
- A nonnullable value cannot receive `MISSING` through `where`, join fallback, lookup,
  or branch unification.
- `NaN` is a floating-point value and is not automatically a typed missing value.

The input adapter MAY translate legacy sentinels such as `-1` to `MISSING_ID[K]`, but
the mapping must be declared at the boundary and must not make equality between
unrelated numeric and ID values legal inside policy code.

Missing-value semantics are explicit.

- Ordinary arithmetic and compatible comparisons propagate nullability: if any operand
  may be missing, the result may be missing unless the primitive declares another
  policy.
- `is_missing(value)` and `is_not_missing(value)` return a nonnullable boolean at the
  value's index and local axes. Source syntax `value == MISSING` and `value != MISSING`
  MAY normalize to these primitives; no other equality with an untyped sentinel is
  permitted.
- A nullable boolean cannot control `if`, `where`, masking, `ANY`, or `ALL` until a
  registered operation resolves missing conditions, for example
  `fill_missing(condition, False)`.
- `coalesce(value, fallback)` requires a fallback compatible with the nonnullable form
  of the value and returns that nonnullable form.
- Joins, schedules, reductions, and aggregations declare one of `ERROR`, `PROPAGATE`,
  `SKIP`, or a reducer-specific missing policy. The default is `ERROR`, not
  backend-dependent behavior.
- Typed missingness is represented by masks or an equivalent backend-safe form. The
  checker does not infer it from NaN payloads.

(gep-10-declarations)=

### Declaration syntax and resolution

`ValueSpec` is the canonical leaf representation and `TypeSpec` is the canonical public
type. Python convenience constructors under `Q` and structured YAML mappings are the
public declaration syntaxes.

#### Python constructors

The required constructors include at least:

```python
Q.number(...)
Q.money(...)
Q.boolean(...)
Q.share(...)
Q.probability(...)
Q.rate(...)
Q.count(counted_entity, ...)
Q.identifier(key_domain, ...)
Q.category(category_domain, ...)
Q.calendar_year_point(...)
Q.date_point(...)
Q.year_month_point(...)
Q.calendar_duration(axis, ...)
Q.month_of_year(...)
Q.quarter_of_year(...)
Q.day_of_month(...)
Q.struct(fields={...})
Q.mapping(inputs=(...), output=...)
```

Constructors may provide only documented, type-safe defaults. For example, `Q.money()`
may supply physical unit `currency`, kind `NUMBER`, and code-side currency `STATUTORY`;
it may not infer subject or extensity from a name. `Q.identifier(Key.HH_ID)` supplies
kind and key domain but not an unrelated grouping subject.

#### YAML form

The canonical YAML form is a mapping, not a composite string.

```yaml
value_type:
  unit: currency
  period:
    signature: per_month
    convention: gettsim_standard_annualized
  kind: number
  subject: person
  extensity: extensive
  index: person_unique
  axes: []
  calendar: null
  currency:
    denomination: EUR
    provenance: source_column
  nullable: false
```

Fields that are structurally fixed by the object MAY be omitted from source YAML but
MUST appear in the resolved `ValueSpec`. For example, a scalar parameter has
`index: scalar` and `axes: []`; a generated person-row input has an index supplied by
its graph node. A compact `period: per_month` alias may expand to a package's explicitly
named standard convention, but the canonical serialization contains both signature and
convention. The evidence report records every field that was derived and the named rule
that derived it.

A compact alias MAY be supported if and only if it expands injectively to one canonical
mapping. There must be one canonical serialization for equality, hashing, diagnostics,
and evidence.

#### Declaration matrix

| Object                        | Required declaration                        | Additional validation                                                      |
| ----------------------------- | ------------------------------------------- | -------------------------------------------------------------------------- |
| `@policy_function`            | `value_type=`                               | body, return, suffix, subject, index, local axes, exceptions               |
| `@policy_input`               | `value_type=`                               | suffix, subject, index, local axes, boundary compatibility                 |
| scalar parameter              | `value_type:`                               | dated resolution, concrete currency, leaf shape                            |
| dictionary parameter          | one type or per-leaf types                  | complete leaf coverage per regime                                          |
| mapping or schedule parameter | typed input axes and output                 | arity, domain kinds, output suffix                                         |
| structured parameter function | `Q.struct(fields=...)`                      | field access and source-to-field mapping                                   |
| generated period conversion   | derived `ValueSpec`                         | only period specification, magnitude, and conversion provenance may change |
| generated aggregation         | derived `ValueSpec`                         | relation, uniqueness, extensity, result subject                            |
| join or gather node           | derived `ValueSpec`                         | key domains, cardinality, fallback, row domains                            |
| hand-written aggregation      | result `value_type=` plus relation metadata | exact agreement with derived rule or assertion                             |
| group-creation function       | identifier or relation type                 | key domain, uniqueness, membership                                         |
| rounding specification        | concrete typed magnitudes                   | function type, denomination, effective date                                |
| typed input column            | complete source `ValueSpec`                 | target compatibility and conversion                                        |

A missing declaration is an error unless a unique normative generated rule supplies it.
An opaque `UNSET_UNIT` does not satisfy this requirement. Structured values use a
structured type.

#### Suffix validation

GEP 1 time and grouping suffixes remain useful redundant checks.

- A `_m`, `_y`, `_q`, `_w`, or `_d` suffix must agree with the result's simple flow
  period when the name denotes a flow.
- A group suffix must agree with the declared subject where GEP 1 defines that suffix as
  the subject of the result.
- An identifier suffix determines a candidate key domain but does not turn a number into
  an ID.
- Suffixes do not describe period conventions, extensity, semantic kind, row
  representation, local tensor axes, join cardinality, calendar semantics, currency
  provenance, or nullability.
- A name and declaration disagreement is always an error; neither takes precedence.

(gep-10-rules)=

### Expression type rules

The type checker operates on resolved `ValueSpec` objects. The following rules are
normative. An implementation may use more detailed internal types but may not accept an
expression rejected by these rules without an explicit assertion or exemption.

#### Equivalence, compatibility, and conversion

Two value types are **equivalent** when all canonical axes are equal after resolving
aliases and concrete policy-date metadata. Two value types are **compatible** for a
named operation when the operation's rule explicitly permits a conversion, scalar
broadcast, neutral modifier, nullable unification, or relation-mediated alignment.

Physical, period, and currency conversion MUST be explicit in the typed graph, even when
generated automatically from naming conventions. The abstract interpreter may insert a
generated conversion node only where the graph builder would insert the same numerical
conversion and provenance at runtime.

A type comparison MUST NOT reduce to Pint dimensionality alone.

#### Addition and subtraction

Numeric addition and subtraction require:

- compatible semantic kinds;
- physically equivalent units;
- equivalent period signatures and compatible conventions after an allowed conversion;
- compatible currency denomination and provenance;
- aligned indices and local axes, allowing registered scalar or axis broadcast;
- compatible subjects; and
- a valid extensity combination.

The result preserves the common unit, period specification, kind, subject, index, local
axes, calendar state, and currency; result nullability is the union of operand
nullability unless a registered missing-value rule resolves it. Extensity is combined by
the table above.

Identifiers, categories, booleans, and calendar ordinals do not support ordinary numeric
addition or subtraction. Counts use the same-counted-entity rule above and do not mix
with unrestricted numbers. Calendar points and durations use their separate affine
rules.

A subtraction of two compatible extensive amounts remains extensive. A subtraction of
two calendar points returns a calendar duration. These are different rules and cannot be
selected from dtype alone.

#### Multiplication and division

Multiplication and division combine physical units and period signatures algebraically
and carry period-convention provenance through the registered rule. The operation must
also have a registered semantic, subject, index, local-axis, and extensity rule.

The required built-in rules include:

- `NUMBER × NUMBER` and `NUMBER / NUMBER`, producing `NUMBER` with algebraically
  combined unit and period;
- an extensive or intensive numeric quantity multiplied or divided by a `SHARE`,
  `PROBABILITY`, `RATE`, or neutral coefficient, preserving the quantity's subject and
  extensity unless the rate's declared semantics specify another result;
- a neutral coefficient with inverse unit or period multiplying a quantity, with the
  resulting physical unit, period signature, and convention cancellation checked
  normally;
- a typed group-mean, allocation, or count-scaling rule involving `COUNT[E]` and a
  declared relation; and
- division of like numeric quantities producing a dimensionless `NUMBER`, `SHARE`, or
  `RATE` only when the result kind is declared or uniquely implied by the registered
  primitive.

Plain multiplication by a count does not silently change a person amount into a
household total. The checker requires `total_from_mean()`, `allocate_equal()`, or
another registered equivalent carrying the relation and intended result subject.
Similarly, plain division by a head count does not silently erase or change a group
subject; `mean_per_member()` and `allocate_equal()` encode the two distinct meanings.

The checker rejects semantic products for which no rule exists, even if the physical
Pint expression is valid.

#### Ordering comparisons

`<`, `<=`, `>`, and `>=` require comparable numeric or calendar types. Numeric operands
must have compatible unit, period specification, denomination, subject, extensity role,
index, and local axes. A scalar neutral threshold may compare with a compatible indexed
quantity.

The result is `BOOLEAN` at the aligned row index. Its subject is the subject of the
indexed quantity or the common subject when both are indexed.

Counts may be ordered only against the same `COUNT[E]` kind or a typed count literal.
Identifiers and categories are not ordered unless their nominal domain explicitly
registers an ordering. An ID is not ordered merely because its storage dtype is integer.

#### Equality and inequality

Equality is checked; it is not a blanket exemption.

`==` and `!=` are permitted only for:

- equivalent or operation-compatible numeric types;
- booleans;
- identifiers in the same key domain;
- an optional identifier and `MISSING_ID` of the same key domain;
- categories in the same category domain;
- compatible calendar values of the same calendar kind and axis; and
- a nullable value and the typed `MISSING` sentinel, normalized to `is_missing` or
  `is_not_missing`.

The following are errors:

```python
monthly_income == annual_income
hh_id == bg_id
p_id == -1
month_of_year == benefit_share
category_a == category_from_another_domain
```

Legacy ID sentinel comparisons must be normalized at the input boundary or use a typed
helper such as `is_missing(id_value)`.

(gep-10-booleans)=

#### Boolean operations and truth contexts

Only nonnullable `BOOLEAN` may be consumed by a truth or logical operation unless the
primitive has an explicit missing-condition policy.

Python `if`, conditional expressions, `and`, `or`, `not`, and `assert` require a scalar
boolean: `Index.scalar()` and no non-singleton local axis. A boolean array in a Python
scalar truth context is rejected even though its semantic kind is correct. Loops are
outside the initial supported language.

`xnp.where`, `xnp.select`, `xnp.logical_*`, `&`, `|`, `^`, and `~` accept scalar or
array booleans according to their registered broadcast and alignment rules. Numeric
bitwise operations are outside the default policy-expression subset. `ANY` and `ALL`
consume boolean values through typed reduction rules. Direct boolean indexing or masking
is unsupported unless a registered primitive defines the resulting index, local axes,
and shape contract.

All non-scalar boolean operands must have aligned row indices and local axes. A group
boolean gathered to person rows may combine with a person boolean because the relation
has made the row alignment explicit. The result is a person-row boolean; the gathered
value's provenance remains available in the expression evidence.

The scalar and vectorized implementations MUST call the same rule. In particular,
`xnp.where` MUST validate its condition before unifying its result arms.

#### Conditional expressions and branch joins

For `x if condition else y`, `xnp.where(condition, x, y)`, and every other selection
primitive:

1. `condition` must be boolean and nonnullable, or the selection primitive must declare
   how a missing condition is resolved;
1. both result arms are analyzed;
1. the arms must be equivalent or unify through the typed-zero, typed-missing,
   scalar-broadcast, or explicitly registered numeric-conversion rules; and
1. the result is the least type admitted by that rule, including nullability.

The checker must analyze both branches syntactically. It must not depend on a
placeholder's chosen runtime truth value to discover one branch.

(gep-10-literals)=

#### Numerical literals

`True` and `False` are nonnullable `BOOLEAN` literals with global subject, scalar index,
no local axes, `NOT_APPLICABLE` extensity, and no currency. They may broadcast only
through a registered boolean or selection primitive.

A nonzero numeric literal has type `NUMBER`, physical unit one, stock period, global
subject, neutral extensity, scalar index, and no currency. It cannot be added to,
ordered against, or used as a branch replacement for a dimensioned value without an
explicit typed literal.

```python
income_m < quantity_literal(
    1000.0,
    value_type=Q.money(
        period=Period.per_month(),
        subject=Entity.PERSON,
        extensity=Extensity.NEUTRAL,
    ),
    assertion=AssertionRef("GEP10-LITERAL-001"),
)
```

Statutory constants SHOULD be parameters rather than implementation literals.

Literal zero is represented internally as `ZERO_LITERAL`. It may adopt an expected
numeric type only in these contexts:

- additive identity;
- a conditional or `where` arm;
- a `min`, `max`, or `clip` bound;
- a numeric comparison; or
- a return with a declared numeric expected type.

Zero cannot adopt `BOOLEAN`, `IDENTIFIER`, `CATEGORY`, or a calendar-point type. `False`
is a boolean literal, not a numeric zero. A nonzero ID sentinel is never a
dimensioned-literal exception.

Literal one has a narrower contextual rule. `ONE_LITERAL` may adopt `SHARE` or
`PROBABILITY` only in a registered complement or unit-interval-bound context, such as
`1 - probability` or `share <= 1`. It cannot adopt a count, identifier, category,
dimensioned number, calendar value, or arbitrary rate. Other nonzero share, probability,
rate, or count constants use typed literals. The evidence and diagnostics record every
contextual zero or one adoption.

Category, identifier, count, and calendar constants use nominal typed constructors or
registered enum objects:

```python
category_literal("single", domain=MARITAL_STATUS)
identifier_literal(17, domain=Key.HH_ID)
count_literal(2, counted_entity=Entity.PERSON, subject=Entity.HH)
month_of_year_literal(2)
```

Raw strings and integers do not acquire these kinds from the other operand of an
equality test. Legacy encodings are decoded at a typed boundary.

#### Minimum, maximum, clipping, and rounding

`min`, `max`, `clip`, `xnp.minimum`, `xnp.maximum`, and their registered variants
require compatible numeric operands and preserve the unified value type. They do not
change subject or extensity. A typed zero bound is permitted.

Numerical `round` preserves the value type. Statutory rounding is a graph operation with
a typed `RoundingSpec` and currency rules defined below.

#### Powers and transcendental functions

Integer powers combine physical and period exponents algebraically. A noninteger power
requires a resulting physical unit whose exponents remain representable and
policy-approved, and it is permitted only when the policy reference period remains
stock. Noninteger powers of currency or a policy reference period are rejected by the
standard registry; a specialized primitive must normalize those dimensions before
returning a boundary-convertible value.

`exp`, `log`, and trigonometric functions require dimensionless `NUMBER` inputs with a
stock period and compatible semantic role. They do not accept shares, probabilities,
IDs, counts, or calendar values merely because those are physically dimensionless. A
package may register a specialized transformation with an explicit signature.

(gep-10-calendar)=

### Calendar types

Calendar semantics are separate from physical units and policy reference periods. Every
calendar value has `unit=one`, `period=stock`, `currency=NONE`, and
`extensity=NOT_APPLICABLE`. Its calendar semantic kind is paired with a non-null
`CalendarSpec`:

```python
@dataclass(frozen=True)
class CalendarSpec:
    axis: CalendarAxis
    system: CalendarSystem
    arithmetic_rule: CalendarArithmeticRule | None
    domain: CalendarDomain
```

`axis` identifies `YEAR`, `YEAR_MONTH`, `DATE`, a duration axis, or an ordinal domain.
`system` identifies the civil-calendar system, normally the proleptic Gregorian calendar
for GETTSIM. `arithmetic_rule` names any normalization or end-of-month rule required by
an admitted operation. `domain` records finite ordinal bounds or the representable point
domain. The axis encoded in the calendar semantic kind MUST equal `CalendarSpec.axis`.
Noncalendar kinds require `calendar=None`.

The required calendar types are:

```text
CALENDAR_POINT[YEAR]
CALENDAR_POINT[YEAR_MONTH]
CALENDAR_POINT[DATE]
CALENDAR_DURATION[YEAR]
CALENDAR_DURATION[MONTH]
CALENDAR_DURATION[DAY]
CALENDAR_ORDINAL[QUARTER_OF_YEAR]
CALENDAR_ORDINAL[MONTH_OF_YEAR]
CALENDAR_ORDINAL[DAY_OF_MONTH]
```

A policy package may add compatible axes. The following distinctions are mandatory.

- `1999` as a year point is affine on the year axis.
- `(1999, 2)` as a year-month point is affine under explicit month arithmetic.
- an absolute date is a complete date point.
- `2` as month of year means February and is a cyclic ordinal, not a point.
- `15` as day of month is a contextual ordinal, not a point.
- age in years is a year duration, not a year point and not a policy annual flow period.

#### Supported affine algebra

| Operation                           | Result           | Requirement                               |
| ----------------------------------- | ---------------- | ----------------------------------------- |
| year point − year point             | year duration    | same axis and calendar convention         |
| year point ± year duration          | year point       | same axis                                 |
| year-month point − year-month point | month duration   | same axis and normalization convention    |
| year-month point ± month duration   | year-month point | explicit normalized year-month arithmetic |
| date point − date point             | day duration     | same calendar system                      |
| date point ± day duration           | date point       | calendar-aware date operation             |
| date point ± month or year duration | date point       | explicit end-of-month convention          |
| point ordered against point         | boolean          | same point axis                           |
| duration ± duration                 | duration         | same duration axis                        |
| point + point                       | error            | points are affine, not vectors            |
| point × number                      | error            | no point scaling                          |
| point ordered against duration      | error            | incompatible calendar kinds               |

Month-of-year, quarter-of-year, and day-of-month ordinals support equality and ordering
within the same ordinal domain. They do not support point-plus-duration arithmetic or
subtraction yielding a duration. `December + 2 months` is therefore invalid until
December is paired with a year to form a year-month point and a wrap convention is
explicit.

Boundary validation MUST enforce integer or registered-enum representation, `1..4` for
quarter of year, `1..12` for month of year, and `1..31` for day of month. Fractional
ordinals are invalid. Actual day validity, including leap-day validity, requires a
complete date.

`policy_year` is a year point. `policy_month` is a month-of-year ordinal. `policy_day`
is a day-of-month ordinal. `policy_date` is an absolute date point. The same rules apply
to evaluation date components.

Flow conversion between monthly and annual amounts is unrelated to calendar-point
arithmetic. The implementation MUST use distinct classes and rule paths for these
concepts.

(gep-10-relations)=

### Keys, relations, joins, and alignment

A `RelationSpec` describes a mapping between entity domains. It contains at least:

```python
@dataclass(frozen=True)
class RelationSpec:
    source: EntityDomain
    target: EntityDomain
    foreign_key: KeyDomain
    primary_key: KeyDomain
    cardinality: Cardinality
    missing_policy: MissingPolicy
    uniqueness: UniquenessContract
```

Key domains are nominal. Equal storage dtype or equal numerical values do not make two
key domains compatible.

#### Gather and join

A typed gather has the conceptual signature:

```text
gather(
    foreign_key: Series[Identifier[K]?, source_rows],
    primary_key: Series[Identifier[K], target_rows],
    target: Series[T, target_rows],
    cardinality: MANY_TO_ONE,
    on_missing: MissingPolicy[T],
) -> Series[T, source_rows]
```

Validation requires:

- equal key domain `K` on foreign and primary keys;
- nonnullable and unique primary keys;
- a declared cardinality compatible with the operation;
- source and target row domains matching the relation;
- an `on_missing` value that is exactly compatible with `T`, or typed `MISSING` when the
  resulting gather is nullable;
- no numeric or category key masquerading as an identifier; and
- no silent subject reassignment.

The output preserves the target's physical unit, period specification, kind, subject,
extensity, local axes, calendar, and currency semantics while changing its index to the
source rows and recording gathered provenance. Its nullability is the union of target
nullability and the declared missing policy. A later operation may use it as a modifier
or explicitly reassign or allocate its subject under a policy rule.

One-to-many and many-to-many joins require separate primitives with result-shape
semantics. They must not be accepted by a many-to-one stand-in.

#### Broadcast and scalar expansion

Scalar expansion is permitted when a scalar's subject and semantic role are compatible
with the receiving operation. A group-to-person broadcast requires a relation and a
uniqueness contract. The result index records that values repeat by the declared key.

A repeated value cannot be aggregated over the finer row domain as if every row were an
independent source value. The checker requires deduplication or aggregation at the
logical source domain.

#### Subject reassignment and allocation

Some laws deliberately move or allocate an amount between legal entities. This is not a
unit conversion. It uses a named semantic operation such as:

```python
reassign_subject(
    value,
    to=Entity.BG,
    relation=EG_TO_BG,
    assertion=AssertionRef("SGBXII-TO-SGBII-001"),
)
```

or an allocation operation that declares weights and conservation rules. These
operations retain physical unit, period specification, local axes, and currency type but
change subject and evidence. A generic full-type cast is not the normal interface for
cross-level policy semantics.

(gep-10-aggregations)=

### Aggregations and reductions

An aggregation is typed by the source value, source index, source uniqueness, relation,
reducer, target entity and target universe, any weights or ordering, an explicit
missing-value policy, and an explicit empty-group policy. Physical units alone are
insufficient. The default missing policy is `ERROR`; `SKIP` changes the effective
denominator and must be part of the reducer signature and evidence.

Missing source values and empty target groups are different cases. `EmptyGroupPolicy` is
one of `ERROR`, `MISSING`, or a reducer-specific typed identity. The standard identities
are typed zero for `SUM` and `COUNT`, `False` for `ANY`, and `True` for `ALL`; a package
may instead choose `ERROR` or `MISSING`. `MEAN`, `WEIGHTED_MEAN`, `MIN`, `MAX`, `FIRST`,
and `UNIQUE` have no default identity. A nullable or identity-producing result is
derived from the declared policy; backend accident is never the source of empty-group
semantics.

#### Required aggregation rules

| Aggregation                       | Input requirement                                                                             | Result                                                                        |
| --------------------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `SUM`                             | extensive numeric value, unique at source entities                                            | same unit and period; extensive; subject and unique index become target       |
| `SUM` over boolean                | boolean unique at source entities                                                             | `COUNT[source_entity]`; subject and index target                              |
| `MEAN`                            | numeric value unique at source entities                                                       | same unit and period; intensive statistic; subject and index target           |
| `WEIGHTED_MEAN`                   | numeric values plus aligned dimensionless weights, normalization rule, and zero-weight policy | same unit and period; intensive statistic; subject and index target           |
| `MIN`, `MAX` over numeric values  | ordered numeric values                                                                        | same unit, period, and kind; `STATISTIC`; subject and index target            |
| `MIN`, `MAX` over calendar values | one compatible calendar kind and axis                                                         | same calendar semantics; `NOT_APPLICABLE` extensity; subject and index target |
| `COUNT`                           | rows or values unique at a declared counted entity                                            | `COUNT[counted_entity]`; subject and index target                             |
| `ANY`, `ALL`                      | boolean values                                                                                | boolean; subject and index target                                             |
| `UNIQUE`                          | certified constant or repeated value per target                                               | de-duplicated value at target; otherwise error                                |
| `FIRST`                           | explicit deterministic ordering and policy meaning                                            | same unit, period, and kind; `STATISTIC` at target plus ordering evidence     |

A mean of person wealth by kinstead is currency-valued, intensive, and has subject
kinstead. It is not physically `currency / kinstead`, and it is not a person-level
value.

Weighted means require weights aligned to the source row index and relevant local axes.
The weight kind is `SHARE` or a registered dimensionless weighting kind; standard
weights are nonnegative, and a currency amount or count cannot be used as a weight. The
primitive declares whether it normalizes raw weights, requires them to sum to one, and
what happens when the total weight is zero. A signed-weight estimator requires a
separately named primitive. These value constraints are checked where runtime values are
available and recorded separately from static type evidence.

A sum over a repeated household total on person rows is rejected because the input is
not unique at the source entities. `UNIQUE` or a group-indexed source must be used
first.

A hand-written aggregation must provide the same relation metadata and must declare a
result type that exactly matches the derived rule. A different intended meaning uses a
named assertion or semantic transformation, not `verify_units=False`.

#### Per-member statistics, allocation, and count scaling

Division by a head count has two common meanings and therefore uses two different
primitives.

`mean_per_member(total, count, relation)` requires an extensive total whose subject is
the relation target, a `COUNT[source_entity]` at the same target, and a nonzero-count
policy. It returns an `INTENSIVE` statistic with the same target subject and target
index. The value describes the average per source member, but it remains one group-level
statistic. Broadcasting it to source rows does not change that subject.

`allocate_equal(total, count, relation)` has the same input requirements but returns an
`EXTENSIVE` amount with source-entity subject and a source-row index. It records an
equal-allocation and conservation contract: summing the nonmissing allocations through
the same relation must recover the input total, subject to the declared zero-count and
numerical-rounding policy. Weighted allocation uses
`allocate(total, weights, relation, conservation=...)`; weights must be aligned,
dimensionless shares and their normalization rule must be explicit.

`total_from_mean(mean, count, relation)` may reconstruct an extensive target total from
a target intensive per-member statistic. `sum_allocations(allocation, relation)`
aggregates source allocations normally. No generic division or multiplication by a count
changes subject by itself.

#### In-body array reductions

`xnp.sum`, `xnp.mean`, `xnp.min`, `xnp.max`, and similar reductions MUST inspect
array-axis metadata. A reduction axis is either:

- a local tensor axis with a declared semantic axis and a registered reduction rule; or
- a row/entity axis, in which case a `RelationSpec` and target are required.

A `where` mask on a reduction must be a nonnullable boolean aligned with the reduced
value after registered broadcasting. It is an inclusion mask, not an implicit
missing-value policy. A reduction that removes an axis removes its `AxisSpec`;
`keepdims=True` retains a declared singleton form of that axis. The result index and
remaining local-axis order are derived rather than copied from the input.

A stand-in that discards `axis`, `where`, `keepdims`, weights, initial value, or
row-domain information is nonconforming. If an axis has no static metadata, the
reduction is rejected. Contributors may move the operation into a generated typed
aggregation or register a precise local-tensor signature.

(gep-10-schedules)=

(gep-10-parameters)=

### Parameters, schedules, and structured values

#### Dated scalar and dictionary parameters

A scalar parameter declares one `ValueSpec`. A homogeneous dictionary may share one
type; a heterogeneous dictionary declares a complete type mapping over the union of leaf
paths that can exist in any date regime.

Dated declarations use forward fill only where explicitly specified. A dated type
mapping replaces the prior mapping as a complete mapping unless the schema explicitly
defines fieldwise inheritance. The value-merging rule and type-inheritance rule are
separate.

At each validated date regime:

- every resolved leaf has one type;
- no absent leaf is spuriously required;
- no present leaf is untyped;
- concrete monetary types match the applicable statutory denomination and provenance
  rule; and
- a value change cannot silently retain an incompatible old type.

#### Mapping and schedule parameters

A mapping parameter uses a typed function signature.

```python
Q.mapping(
    inputs=(
        Q.category(DISABILITY_DEGREE),
        Q.count(Entity.PERSON, subject=Entity.HH),
    ),
    output=Q.money(
        period=Period.per_year(),
        subject=Entity.HH,
        extensity=Extensity.NEUTRAL,
        currency="EUR",
    ),
)
```

The number and order of input axes must match every lookup call. Each axis carries the
complete kind, unit, period, calendar, nominal-domain, ordering, and nullability
semantics needed for lookup or interpolation. Output suffix checks apply to the output
type only.

Categorical and identifier axes permit exact lookup only. Numeric or calendar axes
permit interpolation only through a registered method whose signature defines coordinate
conversion, boundary inclusion, extrapolation, missing values, and result type. A
schedule wrapper must forward all coordinates and options; discarding a secondary axis,
interpolation mode, or fallback is a validation failure.

Piecewise-polynomial coefficients declare the mathematically implied unit and period for
each order. For input type `X` and output type `Y`, an order-`j` coefficient has numeric
unit and period `Y / X^j`, with compatible semantic and currency provenance. The
implementation must not label all coefficients dimensionless and rely on
statutory-currency execution to hide the omission.

#### Parameter functions and structures

A structured parameter function returns `Q.struct(fields=...)`, with a value type for
every accessible leaf or nested object. `UNSET_UNIT` is not a type. A converter may
rename, combine, or derive fields, but its body or a registered transformation signature
must explain the output field types.

A source-to-field comparison is made whenever lineage is known. Renamed or derived
fields do not become unchecked merely because paths differ; the converter's typed body
or explicit field mapping supplies the evidence.

Schedule-producing parameter functions declare the complete typed input and output
signature. Every lookup, interpolation, and polynomial evaluation is validated at the
call site and in the producer.

(gep-10-generated)=

(gep-10-auto)=

### Generated nodes

#### Reference-period conversions

A generated period conversion changes only:

- the period signature or convention admitted by the named conversion rule;
- the numerical magnitude by the exact factor and exponent rule in `PeriodSystem`; and
- period-conversion provenance.

It preserves semantic kind, subject, extensity, index, local axes, calendar state,
currency denomination, currency provenance, and nullability. It may also update a name
suffix according to GEP 1.

If a coefficient carries a period in the numerator or a higher power, conversion applies
algebraically. The system must not assume that every monetary value is a simple flow
with exponent `-1`. A date-dependent proration is a named calendar/statutory primitive,
not this generated context-free conversion.

#### Generated grouping nodes

Generated aggregates, joins, group IDs, broadcasts, and per-capita nodes use the
relational rules above. They do not synthesize Pint group dimensions.

A generated group identifier has kind `IDENTIFIER[group_key_domain]`, not `NUMBER` or
`DIMENSIONLESS`. A generated membership relation declares source, target, keys,
cardinality, and missing policy.

#### Generated currency nodes

Currency conversion is represented as an explicit typed boundary or graph node. It
changes the magnitude, concrete denomination, and provenance record while preserving
semantic kind, subject, extensity, index, local axes, calendar semantics, and
nullability. It preserves the physical currency exponent and period specification.

Let `C(source -> target)` denote the exact number of target-currency units equal to one
source-currency unit. If the physical unit contains currency with signed-integer
exponent `k`, conversion multiplies the magnitude by `C(source -> target) ** k`. This
covers inverse-currency coefficients and higher powers; a converter that always
multiplies by the first-power rate is nonconforming. The standard currency boundary
rejects noninteger currency exponents.

(gep-10-currency)=

### Currency and statutory computation

#### Environment-local currency system

Each policy package constructs one immutable `UnitSystem`. Its currency component
contains:

- a currency family identifier;
- a closed set of concrete denominations;
- one exact conversion graph within the family;
- statutory-effective-date history;
- conversion-rate provenance; and
- a policy for carried or retroactive amounts whose denomination is controlled by an
  origin date other than the current policy date.

```python
from fractions import Fraction

UNIT_SYSTEM = UnitSystem(
    currency_family=CurrencyFamily(
        base="EUR",
        to_base={
            "EUR": Fraction(1, 1),
            "DM": Fraction(100_000, 195_583),  # one DM in EUR
        },
        statutory_intervals=(
            CurrencyInterval("1948-06-20", "2001-12-31", "DM"),
            CurrencyInterval("2002-01-01", None, "EUR"),
        ),
        provenance="legally fixed EUR/DM conversion",
    ),
    period_system=GETTSIM_PERIOD_SYSTEM,
    entities=GETTSIM_ENTITIES,
    key_domains=GETTSIM_KEYS,
)
```

The ordering of mapping entries is not the semantic source of truth. The constructor
validates a well-founded conversion graph, one base per family, unique names under case
normalization, and no collision with declaration syntax.

A `UnitSystem` is passed explicitly or owned by a policy environment. Registering a
second policy package in the same process cannot mutate the first package's type
vocabulary or conversion behavior.

#### Statutory denomination

For a policy-date regime, code-side `STATUTORY` monetary types resolve to the concrete
denomination in which the applicable law writes its parameters and coefficients. A
monetary parameter or coefficient declares a concrete currency and origin. The
environment rejects a declaration that is incompatible with its statutory-effective-date
rule unless the parameter explicitly declares another legally meaningful provenance,
such as a carried amount from an earlier period.

Parameters and coefficients retain their written numerical values. They are not
mechanically rewritten into the caller's data currency. This preserves legally rounded
changeover amounts and currency-dependent formula coefficients.

The type checker still requires complete units for coefficients. Statutory evaluation
guarantees a consistent denomination; it does not convert a mathematically
inverse-currency coefficient into a dimensionless number.

#### Carried, retroactive, and mixed-origin amounts

A value whose denomination is determined by an origin or entitlement period rather than
the current policy date uses `INHERITED(source_node, origin_date_rule)` or another
explicit provenance rule. The environment must resolve whether conversion occurs when
the value is created, carried, combined, or paid.

The current policy date MUST NOT silently relabel a carried DM amount as EUR. Combining
amounts with different concrete denominations requires an explicit conversion node and
rate provenance.

Retroactive calculations must state whether statutory rounding occurs in the
origin-period currency before conversion or in a payment-period currency after
conversion. The default is no implicit conversion and therefore a validation error until
the rule is explicit.

#### Boundary conversion order

For ordinary GETTSIM runs, the normative order is:

1. validate or assume the input `ValueSpec`;
1. convert monetary input to the denomination required at its first policy boundary;
1. perform policy arithmetic using statutory parameters and fully typed coefficients;
1. apply each statutory rounding rule in its declared concrete denomination at its
   declared graph location;
1. complete all statutory calculations and retain the canonical statutory result; and
1. derive a requested data-currency presentation view through an explicit output
   conversion.

The presentation view has `PRESENTATION(...)` provenance and records whether the source
value had already undergone statutory rounding. It is not relabeled as a legally rounded
amount in the presentation currency. Typed output can expose both the canonical
statutory result and the presentation view. Presentation rounding after output
conversion is nonstatutory and must use a distinct option and evidence record.

#### Numerical representation at the boundary

Currency rates are stored as exact rationals or exact decimal specifications with source
and legal provenance. Numerical conversion applies the exponent rule above and has the
following dtype contract.

- Nullable arrays preserve their missing-value mask and convert only present values.
- Floating-point arrays preserve their floating dtype unless an explicit output-dtype
  policy says otherwise. The exact factor is rounded once to that dtype under the
  backend's documented rounding mode. A finite input whose exact converted value is
  outside the finite range raises `CurrencyConversionOverflow`; finite input must not
  silently become infinity or NaN.
- Integer monetary data must either promote to a declared noninteger type or prove exact
  divisibility for every present value; silent truncation is forbidden.
- Decimal or exact-rational values use a compatible exact conversion path or fail
  explicitly.
- Complex monetary values are rejected.
- Object arrays are rejected unless one registered converter handles every present
  element and publishes its result dtype.
- Existing NaN and infinities are not unit errors. A separate data-validity option may
  reject or preserve them, and the evidence report must distinguish that policy from
  type validation.
- Underflow and backend rounding of finite floating values follow the declared dtype
  semantics and are covered by numerical conformance tests; the evidence records backend
  and dtype.
- Currency conversion must not alter identifiers, categories, booleans, counts, or
  nonmonetary quantities.

NumPy and JAX front ends must use the same exact registry rate, exponent, promotion
policy, and operation order. Bitwise equality across backends is not promised where
their documented floating-point semantics differ, but each result must satisfy the
package's stated dtype-level numerical tolerance and all no-truncation,
no-silent-overflow, and rounding-order requirements.

(gep-10-rounding)=

### Rounding specifications

A statutory `RoundingSpec` declares typed magnitudes, concrete denomination,
effective-date range, and legal reference.

```python
@policy_function(
    value_type=Q.money(
        period=Period.per_year(),
        subject=Entity.SN,
        extensity=Extensity.EXTENSIVE,
    ),
    rounding_spec=RoundingSpec(
        base=54,
        direction="down",
        to_add_after_rounding=27,
        value_type=Q.money(
            period=Period.per_year(),
            subject=Entity.SN,
            extensity=Extensity.NEUTRAL,
            currency="DM",
        ),
        reference="§ 32a Abs. 2 EStG",
    ),
    end_date="2001-12-31",
)
def zu_versteuerndes_einkommen_y_sn() -> float: ...
```

The rounding magnitude's physical unit, period specification, subject compatibility, and
concrete denomination must match the value being rounded after resolving `STATUTORY`. A
function active across a statutory-currency or rounding-rule change must have dated
rounding regimes or split definitions.

The maximal date partition includes every rounding start, end, and rule change. A
rounding rule cannot be inherited across a denomination change by accident.

(gep-10-validation)=

(gep-10-checks)=

### Validation architecture

Validation has seven distinct stages. Implementations may combine passes internally, but
evidence must preserve the distinction.

| Stage                            | Validates                                                                  |
| -------------------------------- | -------------------------------------------------------------------------- |
| declaration parsing              | syntax, required fields, closed enums, registry membership                 |
| canonical resolution             | complete `ValueSpec`, defaults, aliases, currency and date resolution      |
| graph validation                 | edge compatibility, generated conversions, relations, joins, aggregations  |
| body abstract interpretation     | supported expressions, branches, calls, returns, assertions                |
| regime validation                | maximal policy-date partition and all active declarations in each interval |
| input/output boundary validation | source tags, dtypes, ranges when requested, conversion                     |
| evidence and release gate        | statuses, coverage, exceptions, expiry, conformance suite                  |

Passing declaration parsing does not imply that a body was checked. Passing body
validation at one date does not imply that all parameter or currency regimes were
checked.

(gep-10-body-checker)=

### Function-body abstract interpretation

#### Supported-language contract

TTSIM validates policy bodies by parsing the supported Python subset into a typed
intermediate representation and interpreting that representation over abstract
`ValueSpec` values. It does not claim that arbitrary placeholder execution proves a
function correct.

The supported subset includes, at minimum:

- local assignments and returns;
- arithmetic and comparison operators with registered rules;
- boolean operators, scalar truth contexts, and `assert` statements;
- conditional statements and conditional expressions;
- attribute and field access on typed structures;
- typed indexing, slicing, stacking, and selection with registered index and local-axis
  rules;
- calls to typed policy functions, parameter functions, schedules, and registered
  primitives;
- scalar and vectorized `xnp` operations with registered signatures; and
- explicit assertion and semantic-conversion primitives.

Loops, comprehensions, dynamic dispatch, reflection, mutation, exception-driven control
flow, or calls whose target cannot be resolved are unsupported until a sound rule is
registered.

Unsupported syntax is a validation failure with status `UNSUPPORTED_BODY`. It must not
be executed with a permissive stand-in that guesses a result type.

#### Syntax-directed branch analysis

The checker analyzes every syntactic branch and joins branch result types. It does not
choose a truth value for an abstract operand to discover one path at a time.
Consequently, a function with `n` independent conditions does not require enumerating
`2^n` placeholder executions merely to check branch return types.

Where value-dependent refinement is needed, the checker may refine nullability, category
variants, or other finite type facts. Such refinement must be conservative and
documented. Failure to prove a refinement rejects the dependent operation rather than
assuming it.

A resource limit may protect the checker from pathological source. Crossing it produces
a visible `CHECKER_RESOURCE_LIMIT` failure. It does not turn the body into a verified
declaration.

#### One primitive registry

All operations are registered in one immutable primitive-signature registry owned by the
`UnitSystem`. Scalar, vectorized, and generated front ends lower to the same primitive.

Each registry entry declares every public alias, complete argument roles, result rule,
supported index and local-axis broadcasts, value constraints, backend availability, and
conformance tests. The implementation generates a public operation inventory from this
registry. A scalar or vectorized alias without an entry, or an entry without required
mutation and parity tests, fails the release gate.

Examples:

```text
Python ternary     ─┐
xnp.where          ├─> SELECT(condition, true_value, false_value)
xnp.select         ┘

Python sum         ─┐
xnp.sum            ├─> REDUCE_SUM(value, axis, relation, options)
generated SUM      ┘
```

A vectorized wrapper must forward every type-relevant argument. Ignoring `condition`,
`axis`, `where`, `keepdims`, fallback, key, cardinality, local axes, weights, or missing
policy is nonconforming. The registry test harness mutates each type-relevant argument
independently and requires the scalar, vectorized, and generated aliases to return the
same resolved type or the same type-axis failure whenever their numerical semantics are
equivalent.

#### Return validation

Each return expression is checked against the function's declared `TypeSpec`. Leaf
checks cover all canonical axes, not only Pint dimensionality, and structural checks
cover field names, container shape, and mapping signatures. A return is rejected when,
for example:

- wealth is declared as monthly income;
- a household total is declared as a person amount;
- a mean is declared as extensive;
- an `Id[HH]` is declared as an unrestricted number;
- a nullable branch is declared nonnullable;
- a month-of-year ordinal is declared as a month duration; or
- a concrete currency or provenance is incompatible with the regime.

A function with no verified body may still expose its declared result to consumers only
through a structured exemption. The consumer contract does not retroactively verify the
producer.

(gep-10-date-partition)=

### Maximal policy-date partition

Validation must cover every interval on which the resolved policy environment is
structurally and typically constant. Testing only function start and end dates is
insufficient.

Let `B` be the set of effective boundaries contributed by:

- policy-function and policy-input start dates;
- the calendar day after each inclusive function or input end date;
- every dated parameter value entry;
- every dated parameter type, physical unit, period signature or convention, kind,
  subject, extensity, index, local-axis, currency, nullability, leaf-set, or
  mapping-axis entry;
- parameter-function and structured-field schema changes;
- schedule domain, arity, interpolation, and coefficient-schema changes;
- statutory-currency start dates and conversion-rate regime changes;
- period-conversion convention, factor, and date-aware rule regime changes;
- rounding-rule starts and the day after inclusive ends;
- relation, key-domain, cardinality, grouping, aggregation, and generated-node validity
  changes;
- naming or schema migrations that affect active declarations; and
- the configured beginning and end of the policy package's supported date domain.

The implementation sorts and deduplicates `B`. Each adjacent pair defines a half-open
interval `[B_i, B_{i+1})`; the final boundary defines an open-ended interval if the
policy domain permits one. Validation resolves the environment at the left endpoint of
every interval. Inclusive end dates are represented by adding their successor date to
`B`.

Every boundary carries provenance identifying which declaration introduced it. The
evidence report publishes the complete partition and the source boundaries.

A parameter-only change therefore creates a new validation regime even when every
function remains active. A currency-only or rounding-only change does the same.

Runtime parameters may change magnitudes but MUST NOT change `ValueSpec`, leaf shape,
index, local axes, key domain, or schedule arity within a compiled regime. Such
structural dependence requires separate static regimes. Dynamic container shape or
leaf-set variation is unsupported until a future explicit variant `TypeSpec` is
standardized; an assertion cannot smuggle it through an ordinary `StructSpec` or
`MappingSpec`.

(gep-10-evidence)=

### Verification evidence and coverage

Every active producer in every date interval receives one primary evidence status and
zero or more qualifiers. Compound producers additionally report a resolved `ValueSpec`
and derivation for each active leaf.

Required primary statuses are:

```text
BODY_VERIFIED
DERIVED_BY_GENERATED_RULE
INTERFACE_VERIFIED_ONLY
DECLARED_ONLY_EXEMPTION
UNSUPPORTED_BODY
UNRESOLVED_TYPE
```

Required qualifiers include:

```text
TYPE_ASSERTION_USED
SEMANTIC_REASSIGNMENT_USED
INPUT_TYPE_ASSUMED
RUNTIME_RANGE_CHECKED
CURRENCY_CONVERTED
LEGACY_ADAPTER_USED
```

Their meanings are:

- `BODY_VERIFIED`: the supported body and return were checked by the abstract
  interpreter.
- `DERIVED_BY_GENERATED_RULE`: the node has no ordinary body; a named relation,
  aggregation, conversion, or graph-construction rule derived and checked its type.
- `INTERFACE_VERIFIED_ONLY`: the declaration and boundary contract were checked, but the
  producer body is external or otherwise outside the checker.
- `DECLARED_ONLY_EXEMPTION`: a structured exemption supplies the consumer result
  contract; the body was not verified.
- `UNSUPPORTED_BODY`: the source uses unsupported syntax or an unregistered primitive.
- `UNRESOLVED_TYPE`: one or more canonical axes could not be resolved.

A package cannot pass the default conformance gate with `UNSUPPORTED_BODY` or
`UNRESOLVED_TYPE`. An organization may permit listed `DECLARED_ONLY_EXEMPTION` nodes
under an explicit policy, but it must not report them as verified.

The machine-readable report contains at least:

```json
{
  "interval": ["2024-01-01", "2024-12-31"],
  "node": "housing.amount_m_hh",
  "resolved_value_type": {},
  "primary_status": "BODY_VERIFIED",
  "qualifiers": [],
  "checker_version": "...",
  "source_digest": "...",
  "unit_system_digest": "...",
  "primitive_registry_digest": "...",
  "date_partition_digest": "...",
  "derivation": [],
  "assertions": [],
  "exemptions": []
}
```

The release summary reports separately:

- active nodes and date intervals;
- declaration-resolution coverage;
- body-verified coverage;
- generated-rule coverage;
- interface-only coverage and the enumerated trusted external primitives;
- assertion count and affected nodes;
- semantic-reassignment count;
- whole-body exemption count;
- assumed-input count;
- unsupported and unresolved counts; and
- intervals validated versus intervals in the maximal partition.

“100% annotated” is not a synonym for “100% body verified.” The report must not combine
them into one percentage.

(gep-10-exceptions)=

(gep-10-opt-out)=

### Assertions, semantic conversions, and exemptions

#### Typed literals

`quantity_literal` assigns a type to an implementation constant. It requires an
`AssertionRef` that points to structured metadata. This operation is narrower than a
generic type cast because it starts from a literal and cannot relabel an existing
computed quantity.

#### Semantic transformations

Alignment, subject reassignment, allocation, per-capita conversion, and calendar
construction use named primitives with explicit preconditions and result rules. Their
evidence names the relation or legal interpretation. They are not generic physical-unit
conversions.

#### Last-resort type assertion

`assert_value_type(value, expected=..., assertion=...)` may supply unresolved axes or
refine a broader nominal domain only when the standard type language cannot express a
valid policy interpretation. It returns the runtime value unchanged. It MUST NOT
contradict a known physical unit, period signature or convention, semantic kind,
subject, index, local axis, concrete currency, or nullability. A known conflict requires
a numerical conversion, named semantic transformation, boundary decoder, formula repair,
or whole-producer exemption; it cannot be erased by assertion.

Every assertion record contains:

```python
TypeAssertion(
    id="GEP10-A012",
    reason="Why the inferred and asserted types differ",
    reference="Statute, design document, or derivation",
    owner="team-or-person",
    issue="tracking issue or permanent-decision record",
    expires="2027-06-30",  # or permanent=True with justification
)
```

The assertion applies to the smallest expression that requires it. It cannot be used to
repair a known false declaration, such as relabeling wealth as monthly income, or to
turn a family total into a person allocation. The checker records the unresolved or
broad inferred type, the asserted refinement, and every affected consumer.

#### Whole-body exemption

A body exemption has the form:

```python
ValidationExemption(
    id="GEP10-E004",
    reason="Unsupported external primitive",
    unsupported_construct="library.function",
    owner="team-or-person",
    issue="https://...",
    expires="2027-03-31",
)
```

An exempt function still declares a complete output `ValueSpec`, which consumers use as
an interface contract. Its evidence status is `DECLARED_ONLY_EXEMPTION`. Missing
metadata, an expired record, or an exemption not present in the policy package's
reviewed manifest is a release error.

The default CI policy rejects an increase in assertions or exemptions unless the change
updates an approved manifest and its review record. A permanent exemption must name a
stable external contract and explain why a typed primitive signature is not feasible.

`verify_units=False` and unstructured casts are nonconforming.

(gep-10-boundary)=

### Input-boundary validation

For fully typed input, every leaf has a source `ValueSpec`. Validation checks:

- semantic kind and nominal domains;
- physical-unit and period-specification compatibility;
- subject and index compatibility;
- representation, uniqueness, key, and local-axis requirements;
- extensity;
- calendar kind and axis;
- currency denomination and provenance;
- nullability; and
- optional dtype, range, uniqueness, and finiteness contracts.

Only registered physical, period, and currency conversions change magnitudes.
Semantic-kind, subject, key-domain, category-domain, and calendar-kind mismatches are
errors.

Semantic kinds may imply value constraints that are not purely static. Fully typed
boundaries MUST check boolean representation, identifier and primary-key validity,
category-domain membership, integer-valued counts, declared count nonnegativity,
probability range, and calendar-ordinal ranges. Other share or rate ranges are checked
when their declaration supplies a constraint. Computed values receive
`RUNTIME_RANGE_CHECKED` only when an enabled runtime validator actually checks them; a
static `BODY_VERIFIED` status alone does not prove ranges.

For untyped input, the policy node supplies the expected `ValueSpec`; `data_currency`
supplies a monetary-denomination assumption. The evidence uses `INPUT_TYPE_ASSUMED`. The
system may still perform GEP 9 dtype checks, key uniqueness checks, and configured
value-range checks.

Typed output contains the fully resolved result type. A requested raw parameter retains
its own statutory type and is not relabeled as a computed output in data currency.

(gep-10-failures)=

### Failure policy and diagnostic requirements

Validation is fail-closed. An unknown operation, missing type axis, incompatible
relation, or uncovered date interval is an error unless a valid structured exemption
applies.

Diagnostics must identify:

- the node and date interval;
- source location and expression;
- the complete left and right or expected and actual value types;
- the specific axis that failed;
- any relation, key, or aggregation involved;
- the derivation path for generated fields; and
- the assertion or exemption that would be required, without suggesting a generic cast
  as the default repair.

For branch failures, diagnostics identify the syntactic branch and both arm types. For
scalar and vectorized variants, equivalent source expressions should produce equivalent
diagnostics.

A failure in one interval does not suppress analysis of other intervals when the checker
can continue safely; the final report may aggregate failures. A package cannot claim
conformance until all blocking failures are resolved.

(gep-10-conformance)=

## Conformance and acceptance requirements

An implementation conforms to this GEP only if all mandatory requirements below are met.
Green project tests without these cases are not sufficient evidence.

### Core type-model requirements

1. The canonical leaf type separates physical unit, period signature and convention,
   semantic kind, subject, relational index, local tensor axes, extensity, calendar
   semantics, currency provenance, and nullability; compound values use structural
   `TypeSpec` variants.
1. Pint is used only for physical-unit algebra and conversion. Entity domains and
   semantic kinds are not Pint dimensions.
1. Dimensionless values are not accepted without a semantic kind.
1. Identifiers and categories use nominal domains.
1. Currency denomination and provenance are checked separately from physical currency
   dimension.
1. The complete resolved type is serializable canonically and hashable for graph
   validation and evidence.
1. Type vocabularies, period systems, and primitive registries are immutable and
   environment-local; construction, import order, threads, and concurrent validation do
   not change another environment's accepted vocabulary or rules.

### Expression-language requirements

The conformance suite must include at least the following mutation tests.

| Case                                                                                                                                        | Required result                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| use currency, wealth, count, ID, or category in Python `if`, `and`, `or`, `not`, `bool()`, or `assert`                                      | reject as nonboolean truth context                                                   |
| use a boolean array directly in Python `if`, `and`, `or`, `not`, `bool()`, or `assert`                                                      | reject as nonscalar truth context                                                    |
| use any `while` loop in the initial language                                                                                                | reject as `UNSUPPORTED_BODY`; never validate it through placeholder truth evaluation |
| use `for`, a comprehension, `match`, a closure with unresolved captures, reflection, mutation, or exception-driven control flow             | reject deterministically as `UNSUPPORTED_BODY` until a sound rule is registered      |
| call an unregistered `numpy`, `xnp`, helper, or dynamically resolved function                                                               | reject; never execute a metadata-dropping fallback                                   |
| branch on array shape, row count, or another runtime value through unsupported Python control flow                                          | reject rather than certify one observed path                                         |
| use the same nonboolean values as `xnp.where` condition                                                                                     | reject with the same kind rule                                                       |
| use aligned boolean array as `xnp.where` condition with matching arms                                                                       | accept                                                                               |
| use nullable boolean as condition without a missing-condition policy                                                                        | reject                                                                               |
| fill nullable boolean explicitly and use it as condition                                                                                    | accept as nonnullable boolean                                                        |
| replace a scalar conditional with its equivalent vectorized conditional                                                                     | same resolved type or same failure                                                   |
| compare monthly and annual income with equality                                                                                             | reject unless an explicit generated period conversion aligns them                    |
| compare `Id[HH]` with `Id[BG]`                                                                                                              | reject                                                                               |
| compare optional `Id[HH]` with `MISSING_ID[HH]`                                                                                             | accept as nonnullable `is_missing` test                                              |
| combine nullable arithmetic operands                                                                                                        | result nullability is the union of operand nullability                               |
| compare `Id[HH]` with literal `-1`                                                                                                          | reject inside policy code                                                            |
| add `COUNT[PERSON]` to `COUNT[PERSON]` at the same subject and index                                                                        | accept as `COUNT[PERSON]`                                                            |
| add `COUNT[PERSON]` to `COUNT[HH]` or to an unrestricted number                                                                             | reject                                                                               |
| add wealth stock to monthly income                                                                                                          | reject                                                                               |
| return wealth from a function declared as monthly income                                                                                    | reject                                                                               |
| multiply a monthly income by a correctly typed month-per-currency coefficient under the same period and currency conventions                | accept with dimensionless result                                                     |
| use an inverse-currency coefficient in a different denomination without conversion                                                          | reject before currency factors cancel                                                |
| declare the coefficient dimensionless                                                                                                       | reject the formula                                                                   |
| apply a fixed annualized conversion to an actual-day statutory amount                                                                       | reject; require the named date-aware rule                                            |
| use nonzero bare threshold against dimensioned amount                                                                                       | reject                                                                               |
| use typed zero against dimensioned amount                                                                                                   | accept and record its contextual type                                                |
| use `1 - probability` or `share <= 1`                                                                                                       | accept through the contextual one rule                                               |
| use one as count, ID, calendar point, or dimensioned amount                                                                                 | reject                                                                               |
| use zero as ID or calendar point                                                                                                            | reject                                                                               |
| apply `log` to a share, count, or identifier                                                                                                | reject unless a specialized primitive is registered                                  |
| call a schedule with the wrong arity, axis kind, calendar axis, category domain, or fallback type                                           | reject at the call site                                                              |
| mutate a schedule wrapper so that it drops a coordinate, interpolation rule, extrapolation rule, or fallback                                | fail registry parity or argument-mutation tests                                      |
| evaluate a polynomial whose order-`j` coefficient lacks type `Y / X^j`                                                                      | reject the coefficient or evaluation                                                 |
| access an absent or untyped structured field                                                                                                | reject; do not return an opaque placeholder type                                     |
| swap two differently typed structured fields while keeping container shape                                                                  | reject from field lineage or return validation                                       |
| mutate a generated period conversion so that it changes subject, index, local axes, extensity, calendar semantics, currency, or nullability | reject the derived node                                                              |
| use `assert_value_type` to relabel wealth stock as monthly income                                                                           | reject the assertion as contradicting a known type                                   |

Every scalar, vectorized, and generated alias in the public operation inventory must be
covered by registry-generated parity and independent-argument mutation tests. A boolean
condition, reduction axis, fallback, key, relation, or option omitted by a wrapper must
cause a test failure.

### Reference-period requirements

The conformance suite must show that:

- standard monthly and annual flows convert through a named exact annualized rule and
  round-trip under the exact arithmetic reference implementation;
- inverse and higher-power period coefficients use the exponent-aware factor;
- source and target conventions appear in the resolved type and conversion evidence;
- an actual-day, leap-year, 30/360, or statute-specific amount is not converted by the
  standard fixed-ratio rule;
- a date-aware proration primitive receives the complete required calendar context and
  publishes its rule identifier; and
- two independent `PeriodSystem` instances cannot leak conventions or factors into one
  another.

### Relation and aggregation requirements

The conformance suite must show that the implementation:

- rejects a join whose foreign and primary key domains differ;
- rejects a monetary value, rate, or category used as a key;
- checks primary-key uniqueness and declared cardinality;
- rejects a join result declared nonnullable when the foreign key or missing policy can
  produce `MISSING`;
- rejects a fallback whose type differs from the target;
- rejects a join, lookup, reduction, or aggregation whose possible missing values lack
  an explicit policy;
- distinguishes missing source values from an empty target group and rejects a reducer
  without a valid empty-group policy;
- preserves target semantics and records the new row index after a gather;
- rejects summing a group value repeated on person rows without deduplication;
- derives a group sum as extensive at the target subject;
- derives a mean as intensive at the target subject while preserving the physical unit;
- derives numeric `MIN`, `MAX`, and policy-defined `FIRST` as `STATISTIC` at the target
  subject;
- rejects a weighted mean with misaligned, negative under the standard rule,
  dimensioned, or undeclared-normalization weights and checks its zero-weight policy;
- keeps `mean_per_member()` at target subject even when broadcast to source rows;
- derives `allocate_equal()` at source subject and verifies its declared conservation
  and zero-count policy;
- rejects a declaration that substitutes one of those meanings for the other;
- derives boolean sum as a typed count of the source entity;
- rejects a count whose counted entity is unspecified;
- checks local axes, row axes, `where`, weights, `keepdims`, and row metadata for
  in-body reductions;
- distinguishes reduction over a local choice axis from aggregation over person rows;
  and
- rejects a reduction over an untyped axis;
- preserves a household row grain idempotently under valid pointwise multiplication
  instead of multiplying or cancelling a fictitious group dimension; and
- handles zero-length sources and empty target groups according to the declared
  identity, missing, or error policy.

### Calendar requirements

The conformance suite must show that:

- year point minus year point returns a year duration;
- year point plus year duration returns a year point;
- year point plus year point is rejected;
- quarter, month, and day ordinals reject fractional and out-of-range representations;
- a complete date rejects an invalid day, including February 29 in a non-leap year;
- month of year plus month duration is rejected;
- a year-month point plus month duration wraps through years under an explicit
  convention;
- a date point plus month duration requires a defined end-of-month rule;
- a calendar point cannot be compared with a duration; and
- policy flow-period conversion is not dispatched through calendar arithmetic.

### Currency requirements

The conformance suite must include:

- at least two statutory denominations and a changeover date;
- parameters and inverse- and squared-currency coefficients declared in each regime's
  concrete denomination;
- exponent-aware conversion of ordinary amounts, inverse-currency coefficients, and
  integer higher powers, plus rejection of a noninteger currency exponent at the
  standard boundary;
- typed input in one denomination converted to another computation denomination;
- statutory rounding before output conversion and a presentation view explicitly labeled
  as nonstatutory in the target currency;
- a carried-value case whose origin denomination differs from the current policy
  denomination;
- rejection of a carried value that is silently relabeled;
- nullable monetary input with its missing mask preserved;
- integer monetary input that would truncate under conversion;
- finite floating input whose exact conversion would overflow, which must fail rather
  than become infinity silently;
- zero-length, largest-finite, subnormal, positive- and negative-zero, NaN, and infinity
  cases under the declared dtype and data-validity policy;
- object-dtype rejection or a registered converter;
- the same exact rate, exponent, and operation order in NumPy and JAX front ends; and
- two independent `UnitSystem` instances whose registrations do not interfere.

### Date-regime requirements

The conformance suite must construct and validate a maximal partition with independent
boundaries from:

- a function start or end;
- a parameter value change;
- a parameter physical-unit, period-signature, or period-convention change with no
  function boundary;
- a parameter leaf-set, index, local-axis, or schedule-axis change;
- a statutory-currency change;
- a period-conversion rule or convention change;
- a rounding-rule change; and
- a relation or aggregation-schema change.

For every inclusive start and end declaration used by the test fixture, the suite
validates the exact start, the exact end, and the successor of the end when it lies in
the supported domain. A mutation that inserts a wrong type only at a parameter-only date
must fail. The evidence report must list the interval containing the mutation and the
parameter boundary that created it.

### Evidence and exception requirements

The conformance suite must verify that:

- every active node and interval has one primary evidence status;
- a body exemption never counts as body verified;
- `verify_units=False`, an unstructured full-type cast, and an unmanifested opt-out are
  rejected;
- a type assertion records inferred and asserted types;
- an expired or unmanifested assertion or exemption fails the release gate;
- unsupported syntax fails closed;
- crossing a checker resource limit is visible and nonverified;
- bare input is reported as assumed, while fully typed input is reported separately;
- the four public claim levels are computed from evidence and cannot be selected
  manually; and
- coverage percentages cannot hide assertions, exemptions, unsupported bodies, trusted
  external primitives, or untested date intervals.

### Worked-example acceptance

The bundled worked example must meet all of the following.

1. Every active node, parameter leaf, local and schedule axis, rounding rule, join,
   aggregation, compound field, and result has a complete resolved `TypeSpec` in every
   maximal date interval.
1. All ordinary body-bearing functions are `BODY_VERIFIED`; the worked example contains
   no `DECLARED_ONLY_EXEMPTION` node.
1. No function relabels a stock as a flow, a group total or group mean as a person
   allocation, or an ID as a number.
1. Parameter-only, period-convention-only, local-axis-only, currency-only, and
   rounding-only date regimes are included.
1. Every assertion and semantic reassignment appears in a reviewed manifest.
1. The adversarial tests above pass for both supported NumPy and JAX execution front
   ends.
1. Typed and untyped boundaries return numerically identical values after expected
   conversion, while their evidence correctly differs.

## Related work

- {ref}`GEP 1 <gep-1>` defines policy-node naming conventions and generated
  reference-period conversions.
- {ref}`GEP 2 <gep-2>` defines grouping and identifier concepts.
- {ref}`GEP 4 <gep-4>` defines the DAG and generated aggregation architecture.
- {ref}`GEP 5 <gep-5>` defines rounding specifications.
- {ref}`GEP 9 <gep-9>` defines runtime type checking and the user/canonical type split.
- [Pint](https://pint.readthedocs.io/) supplies physical-unit parsing, equivalence, and
  conversion.
- Nominal ID and category domains follow the same principle as newtypes or branded types
  in static type systems: equal representation does not imply substitutability.
- The syntax-directed checker follows ordinary abstract-interpretation and typed-IR
  practice: it is conservative over a specified language rather than an execution-based
  test of arbitrary Python behavior.

## Implementation

The implementation is divided into ordered phases. A later phase must not claim
conformance while a required earlier phase remains a permissive placeholder.

### Phase 1: canonical type core

- Implement immutable `ValueSpec`, `StructSpec`, `MappingSpec`, `PhysicalUnit`,
  `PeriodSpec`, `PeriodSignature`, `PeriodConvention`, `SemanticKind`, `SubjectSpec`,
  `IndexSpec`, `AxisSpec`, `Extensity`, `CalendarSpec`, `CurrencySpec`, and nullability.
- Keep Pint behind the `PhysicalUnit` boundary.
- Implement canonical serialization, equality, hashing, diagnostics, and structured YAML
  parsing.
- Replace process-global registration with immutable `UnitSystem` instances.
- Implement complete constructors under `Q` and a legacy migration adapter that cannot
  claim full verification.

### Phase 2: declarations and graph resolution

- Migrate decorators, policy inputs, parameters, structured fields, schedules, rounding
  rules, and typed columns to `value_type` declarations.
- Resolve every canonical axis before graph validation.
- Add nominal key and category domains.
- Represent generated period conversions with named conventions, relations, joins,
  broadcasts, allocations, and aggregations as typed graph nodes.
- Implement suffix consistency checks without using suffixes as the only type source.

### Phase 3: typed expression interpreter

- Lower the supported Python subset to a typed IR.
- Implement syntax-directed branch analysis and return checking.
- Create one primitive registry for scalar, vectorized, and generated operations.
- Implement boolean truth-context checks, typed equality, typed zero and missing
  literals, conditionals, schedules, structured access, and full operation diagnostics.
- Reject unsupported syntax and unregistered primitives.

### Phase 4: relations, axes, and aggregation

- Implement `RelationSpec`, key-domain checks, uniqueness, cardinality, and missing
  policies.
- Implement typed gather, broadcast, subject reassignment, target-level per-member
  statistics, equal and weighted allocation, and count scaling.
- Implement aggregation and local-array axis semantics, including repeated-value
  protection.
- Require every reduction wrapper to forward all type-relevant arguments.

### Phase 5: calendar and currency

- Implement distinct calendar points, durations, and ordinals, plus date-aware statutory
  period conversions that cannot be confused with standard annualized conversion.
- Correct the types of policy and evaluation date components.
- Implement environment-local currency families, statutory histories, provenance,
  carried-value rules, typed coefficients, and boundary conversion ordering.
- Implement dtype-safe numerical conversion and typed rounding regimes.

### Phase 6: date partition and evidence

- Implement the maximal date-partition algorithm.
- Validate every interval and publish boundary provenance.
- Implement evidence statuses, qualifiers, source digests, derivations, coverage,
  assertion and exemption manifests, and the default release gate.

### Phase 7: worked example and GETTSIM rollout

- Migrate METTSIM without proof-erasing stock-to-flow, group-to-person, or coefficient
  casts.
- Run the complete conformance and adversarial suite across every date interval.
- Migrate GETTSIM policy declarations and historical currency regimes.
- Retain untyped input compatibility while distinguishing assumed from verified boundary
  types.

### Existing pull requests

The following pull requests are prototypes for parts of the original GEP and are not, by
their current existence alone, implementations of this revised specification.

- [TTSIM #138](https://github.com/ttsim-dev/ttsim/pull/138) must replace the
  compositional group-dimension model, permissive placeholder behavior, and
  process-global vocabulary with the canonical value type, typed IR, relation rules,
  evidence, and local registries above. It must in particular validate every truth
  context, `where` condition, join argument, fallback, cardinality, reduction axis, and
  date regime.
- [TTSIM #141](https://github.com/ttsim-dev/ttsim/pull/141) must migrate the worked
  example to the revised declarations, remove stock-as-monthly-flow annotations, fully
  type coefficients and group operations, and validate the maximal date partition
  including parameter-only changes.
- [GETTSIM #1193](https://github.com/ttsim-dev/gettsim/pull/1193) contains the GEP
  discussion and is the target for this text.
- The GETTSIM rollout must not claim completion until the TTSIM infrastructure and
  worked example pass the conformance requirements in this document.

A PR may land in phases, but the public feature remains experimental until the complete
required stack is present. Documentation and evidence must identify partial
implementations precisely.

(gep-10-alternatives)=

## Alternatives

### Encode grouping levels as Pint dimensions

Rejected. A subject or row grain is not a physical denominator. Pointwise multiplication
of two household-indexed values would incorrectly square a household dimension, while
division would cancel it even though the result remains household-indexed. Means,
minima, maxima, joins, and broadcast representations also cannot be represented
faithfully by this algebra.

### Treat all nonphysical values as dimensionless

Rejected. Booleans, IDs, categories, shares, probabilities, rates, and counts support
different operations and nominal domains. A dimensionless catch-all permits nonsense
such as adding an ID to a tax rate or using wealth as a condition.

### Use one implied person level and group denominators

Rejected. This still conflates physical algebra with relational ownership and storage
layout. It cannot represent a household value repeated on person rows without either
losing the household subject or inviting double counting.

### Infer meaning from node names and suffixes

Rejected as the primary type source. Suffixes are valuable redundant checks but do not
encode semantic kind, extensity, key domain, nullability, representation, join
cardinality, calendar kind, coefficient units, or currency provenance.

### Execute functions on placeholder quantities and call the result verified

Rejected as the specification model. Placeholder execution can be a useful
implementation aid, but path choices, hand-written stand-ins, Python truth semantics,
unsupported operations, and bounded exploration make it unsuitable as the assurance
contract. The adopted design specifies a syntax-directed typed interpreter and publishes
unsupported code explicitly.

### Leave equality unchecked

Rejected. The legacy missing-ID use case is handled by typed optional identifiers and
missing sentinels. Blanket equality exemption would allow monthly and annual amounts or
unrelated ID domains to compare silently.

### Let `where`, joins, and reductions preserve the result-arm or target unit

Rejected. Conditions, keys, domains, cardinality, fallbacks, axes, uniqueness, and
extensity are part of the operation's correctness. Ignoring them creates ordinary false
negatives.

### Use generic casts and whole-body opt-outs

Rejected as the normal workflow. Typed literals, relation-mediated alignment, subject
reassignment, allocation, calendar construction, and registered primitives cover
distinct valid cases. A last-resort assertion or exemption remains available but carries
structured evidence and never counts as verified.

### Convert every statutory parameter into the caller's data currency

Rejected. Legally rounded changeover values and currency-dependent coefficients must
retain their statutory numerical representation. The adopted design computes in the
statutory denomination, while requiring complete units for coefficients and explicit
conversion at data boundaries.

### Omit units for coefficients not printed with units in statutes

Rejected. Mathematical dimensionality follows from the formula, not typography. An
inverse-income coefficient must declare the inverse unit and period required to make the
formula well typed.

### Pass Pint quantities through the compiled DAG

Rejected. Static `ValueSpec` metadata and boundary conversion provide the intended
validation without placing Pint objects inside JAX traces or changing runtime array
representation.

### Treat month of year and day of month as affine points

Rejected. They are cyclic or contextual ordinals. Valid affine arithmetic requires a
year-month or complete date point and an explicit wrap or end-of-month convention.

### Validate only dates where functions start or stop

Rejected. Parameters, leaf schemas, currencies, rounding, schedules, and relations can
change while the same functions remain active. The maximal partition is required.

### Report a single annotation-coverage percentage

Rejected. Declaration coverage, body verification, generated-rule derivation,
assertions, exemptions, assumed inputs, unsupported bodies, and date coverage convey
different evidence and must remain separate.

## Discussion

- [GETTSIM #1193: GEP 10 discussion](https://github.com/ttsim-dev/gettsim/pull/1193)
- [TTSIM #138: original infrastructure prototype](https://github.com/ttsim-dev/ttsim/pull/138)
- [TTSIM #141: original METTSIM worked-example prototype](https://github.com/ttsim-dev/ttsim/pull/141)

## References and footnotes

- [Pint documentation](https://pint.readthedocs.io/)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119)
- [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)
- [NEP 18: NumPy array-function protocol](https://numpy.org/neps/nep-0018-array-function-protocol.html)

## Copyright

This document has been placed in the public domain.
