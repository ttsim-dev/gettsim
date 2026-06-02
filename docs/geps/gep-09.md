(gep-9)=

# GEP 9 — Runtime Type Checking and the User/Canonical Type Split

```{list-table}
- * Author
  * [Hans-Martin von Gaudecker](https://github.com/hmgaudecker)
- * Status
  * Accepted
- * Type
  * Standards Track
- * Created
  * 2026-05-23
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/channel/309998-GEPs/topic/GEP.2009/with/599362373)
```

## Abstract

- GETTSIM today has limited runtime type checking. Mismatched user inputs surface as
  cryptic `TypeError`s from deep inside the DAG — or worse, as silent numerical bugs
  ([TTSIM #97](https://github.com/ttsim-dev/ttsim/issues/97)).
- This GEP adopts [beartype](https://beartype.readthedocs.io) as a runtime type checker
  that automatically verifies every annotated function in `ttsim`, `gettsim`, and
  `gettsim-personas` against its declared signature. Users get curated errors at the
  boundary they wrote, not at an internal helper six frames deep.
- GETTSIM/TTSIM become explicit about the types they expect and about how user inputs (a
  wide vocabulary, e.g. `pd.Series` or Python scalars) are canonicalised into a single
  internal vocabulary (`numpy` / `jax` arrays).
- The convention "every `@policy_function` carries full type annotations" — already
  universally followed in `gettsim` — is promoted to a decoration-time check, so any
  future omission is caught at the function's definition site with a clear
  `PolicyFunctionDefinitionError`.

### Terminology

- **claw** — `beartype`'s import-hook mechanism: a single `beartype_package()` call
  installs an AST rewriter that automatically applies `@beartype` to every annotated
  function in the package. No per-file decorator, no opt-in list.
- **runtime check** — a guard that runs at function call time and validates the argument
  values against the function's declared type annotations.
- **boundary** — a function the user calls directly: `main()`,
  `InputData.df_and_mapper`, the `@policy_function` decorator, and similar entry points.

## Motivation and Scope

The TTSIM DAG accepts a wide range of objects as inputs — pandas Series, numpy arrays,
Python scalars, JAX arrays — and converts them internally into a narrower,
performance-oriented representation: jaxtyping-shaped JAX or numpy arrays for columns
and Python or numpy scalars for parameters. Today this distinction is implicit.
`typing.py` exposes a single `Array`-based vocabulary, the canonical internal types are
not named separately from their user-friendly supersets, and no runtime check guarantees
compliance. Four problems follow:

1. **Silent type drift.** A policy function annotated `int` that is invoked with a
   `jax.Array` runs silently today; the mismatch only surfaces if a downstream
   JAX-specific operation fails on the unexpected dtype, often far from the offending
   input. Annotations are documentation, not specification.

1. **Scattered canonicalisation.** Every code path that takes user input re-implements
   the cast from `pd.Series` or Python scalar or numpy scalar to a canonical numpy / JAX
   form. The conversions are scattered, and nothing enforces that they agree.

1. **Indistinguishable bug classes.** When a TT DAG raises `TypeError`, the user cannot
   tell whether they passed bad data, mis-declared a policy function, or hit an internal
   TTSIM bug. There is no exception vocabulary that maps to architectural layers.

1. **Past silent bugs.** Missing or imprecise type checks have caused real,
   hard-to-diagnose bugs (e.g.
   [TTSIM #97](https://github.com/ttsim-dev/ttsim/issues/97)).

These cost real time during model development and during workshop teaching.

**Scope.** The GEP covers `ttsim`, `gettsim`, and `gettsim-personas`. The
`@policy_function` dual-mode contract (scalar default vs. column-direct via
`vectorization_strategy="not_required"`) is touched here only insofar as the claw makes
it enforceable; the full contract is specified in a separate update to
{ref}`GEP 4 <gep-4>`.

## Usage and Impact

### Users see the same API, with sharper errors

A miss-typed input still raises a `TTSIMError` subclass, but now with the beartype
violation message attached. Calling `main()` with `policy_date_str` set to a
`datetime.date` instead of a string raises `EntryPointError` at the boundary, not
`AttributeError` six frames deep. Passing a pandas Series with object dtype where a
`FloatColumn` is expected raises `InputDataError`. Writing

```python
@policy_function(start_date="2025-01-01")
def betrag_m(anzahl: int, satz: float) -> float:
    return anzahl * satz
```

and accidentally calling it with `vectorization_strategy="not_required"` raises
`PolicyFunctionDefinitionError` at decoration time — the scalar annotations are
incompatible with column-direct execution.

### Wider boundary types, narrower internal types

- A broad set of input types is accepted at the boundary. Their collective name is
  `UserX`, where `X` is `FloatColumn`, `IntColumn`, `BoolColumn`, etc.
- Each `UserX` is converted by an explicit `_canonicalize_*` function into a single
  internal representation (e.g., a `pd.Series` of unsigned ints becomes a numpy `int64`
  array). The internal type collection is named `X`.
- This formalises how types are reasoned about inside TTSIM and pins the conversion to
  one named function per boundary. The public API does not change in shape: users still
  pass the wide forms.

### Same runtime, more discoverable failures

The claw adds an O(n) container check on entry to every clawed function, but TTSIM's
entry points are called rarely (per-run, not per-row), so the cost is invisible at the
boundary.

## Backward Compatibility

Existing user code keeps working unchanged in shape. Three narrowed claims:

- With the claw on by default for everyone (Option A; see Discussion), a user reform or
  pipeline that previously relied on an implicit type coercion beartype rejects now
  raises at the boundary where the mismatched value enters, instead of running silently.
  This did not occur in our own test suite during the default-on trial. A user who needs
  the pre-GEP behaviour while triaging can opt out with `GETTSIM_BEARTYPE_CLAW=0` (or
  the `TTSIM_BEARTYPE_CLAW` analogue).

- Code that caught `TypeError` or `ValueError` from inside TTSIM should broaden to
  `TTSIMError` (or the relevant subclass). Code that catches `Exception` is unaffected.
  Two pre-existing exception types are hoisted into the hierarchy without changing their
  definition site: `ConflictingActivePeriodsError` and `TranslateToVectorizableError`.
  Both keep their original import path.

- Every `@*_function` decorator now requires a type annotation on every parameter and on
  the return value. This is the convention every existing `gettsim` policy function
  already follows. Pre-GEP, missing annotations were tolerated unevenly:
  `@policy_function` silently fell back to a wide default union via `dags`, while
  `@policy_input` raised a `KeyError` at decoration time. Post-GEP, all five
  `@*_function` decorators raise their matching `*DefinitionError` at decoration time,
  so the convention is enforced uniformly.

Internal code that passes wide types into narrow-typed functions surfaces as
`BeartypeCallHintViolation` from the package-wide claw. These are pre-existing TTSIM
bugs to fix at the call site, not user-facing changes.

## Detailed Description

### The type vocabulary

`ttsim.typing` exposes three layers:

```python
# Narrow canonical column aliases — what flows on the TT DAG.
FloatColumn: TypeAlias = Float[Array | np.ndarray, " n_obs"]
IntColumn: TypeAlias = Int[Array | np.ndarray, " n_obs"]
BoolColumn: TypeAlias = Bool[Array | np.ndarray, " n_obs"]

# Narrow canonical scalar aliases — what flows out of param processing.
ScalarFloat: TypeAlias = float | np.floating
ScalarInt: TypeAlias = int | np.integer
ScalarBool: TypeAlias = bool | np.bool_

# Wide user-boundary aliases — what `main()` and friends accept.
UserFloatColumn: TypeAlias = FloatColumn | pd.Series
UserIntColumn: TypeAlias = IntColumn | pd.Series
UserBoolColumn: TypeAlias = BoolColumn | pd.Series
UserScalarFloat: TypeAlias = float | int | np.floating | np.integer
UserScalarInt: TypeAlias = int | np.integer
UserScalarBool: TypeAlias = bool | np.bool_
```

The column aliases use the `Array | np.ndarray` union so the same vocabulary covers both
backends. This is the single source of truth for column shapes; callers do not branch on
the backend.

The aliases live at module top level, not under `if TYPE_CHECKING`. The claw needs them
at runtime to rewrite call sites.

The wide forms are restricted to the user boundary. Inside TTSIM, the narrow forms are
the rule. Conversions are funnelled through explicit `_canonicalize_*` helpers — one per
boundary — typed `UserX → X`. Outside these helpers, no code converts pandas Series to
JAX arrays or numeric promotes Python scalars to numpy scalars on the fly.

### The exception hierarchy

`ttsim.exceptions` defines a single root and one subclass per architectural boundary:

```python
class TTSIMError(Exception): ...


class EntryPointError(TTSIMError): ...


class InputDataError(TTSIMError): ...


class TTTargetsError(TTSIMError): ...


class PolicyFunctionDefinitionError(TTSIMError): ...


class PolicyInputDefinitionError(TTSIMError): ...


class ParamFunctionDefinitionError(TTSIMError): ...


class AggregationDefinitionError(TTSIMError): ...


class GroupCreationDefinitionError(TTSIMError): ...


class RoundingSpecError(TTSIMError): ...
```

`gettsim` reuses the hierarchy without adding a `GETTSIMError` of its own.
`gettsim-personas` adds one class, `PersonaDefinitionError(TTSIMError)`, for
persona-construction validation.

### Per-component beartype configurations

`ttsim._beartype_conf` builds one `BeartypeConf` per exception class. The
`violation_param_type` argument is the beartype hook that maps type-check failures to
the documented project exception:

```python
from beartype import BeartypeConf, BeartypeStrategy

from ttsim.exceptions import (
    AggregationDefinitionError,
    EntryPointError,
    GroupCreationDefinitionError,
    InputDataError,
    ParamFunctionDefinitionError,
    PolicyFunctionDefinitionError,
    PolicyInputDefinitionError,
    RoundingSpecError,
    TTSIMError,
    TTTargetsError,
)


def _conf(exc: type[TTSIMError]) -> BeartypeConf:
    return BeartypeConf(
        violation_param_type=exc,
        strategy=BeartypeStrategy.On,
        is_pep484_tower=True,
    )


ENTRY_POINT_CONF = _conf(EntryPointError)
INPUT_DATA_CONF = _conf(InputDataError)
TT_TARGETS_CONF = _conf(TTTargetsError)
POLICY_FUNCTION_CONF = _conf(PolicyFunctionDefinitionError)
POLICY_INPUT_CONF = _conf(PolicyInputDefinitionError)
PARAM_FUNCTION_CONF = _conf(ParamFunctionDefinitionError)
AGGREGATION_CONF = _conf(AggregationDefinitionError)
GROUP_CREATION_CONF = _conf(GroupCreationDefinitionError)
ROUNDING_SPEC_CONF = _conf(RoundingSpecError)

INTERNAL_CONF = BeartypeConf(
    strategy=BeartypeStrategy.On,
    is_pep484_tower=True,
)
```

The `On` strategy validates every entry of every container so a bad row inside a
dict-of-columns is reported rather than sampled past. `is_pep484_tower=True` keeps the
PEP 484 numeric tower active so that an `int` argument satisfies a `float` parameter —
the same implicit promotion that Python and ruff's `PYI041` both assume.

`INTERNAL_CONF` is the default for the package-wide claw. Its violations surface as
beartype's own `BeartypeCallHintViolation`, marking them as internal bugs.

### The package-wide claw

Each package's `__init__.py` registers the claw before any submodule loads:

```python
# src/ttsim/__init__.py — top of file, before any ttsim.* import
from beartype.claw import beartype_package

from ttsim._beartype_conf import INTERNAL_CONF

beartype_package("ttsim", conf=INTERNAL_CONF)

# ...remaining imports
```

`beartype_package` installs an AST rewriter against the package's import hook. Every
subsequent `import ttsim.*` produces a module whose annotated callables wrap themselves
in a beartype check on load. There is no per-file decorator, no opt-in list, and no way
to forget a function. `gettsim` and `gettsim-personas` do the same with their own root
packages and their own `INTERNAL_CONF`.

### Explicit decorators at user boundaries

The package claw catches every internal mistake. User-facing entry points and decorator
factories stack an explicit `@beartype(conf=<COMPONENT_CONF>)` on top so violations
there surface as the documented project exception, not as `BeartypeCallHintViolation`.
The explicit decorator wins at its call site.

The user boundaries covered are:

- `ttsim.main()` — `ENTRY_POINT_CONF`
- `InputData.df_and_mapper`, `InputData.tree`, and any sibling factories —
  `INPUT_DATA_CONF`
- `TTTargets.tree`, `TTTargets.qnames`, and siblings — `TT_TARGETS_CONF`
- `@policy_function` (the decorator factory; checks meta-arguments such as `start_date`,
  `end_date`, `vectorization_strategy`) — `POLICY_FUNCTION_CONF`
- `@policy_input`, `@param_function`, `@agg_by_group_function`, `@agg_by_p_id_function`,
  `@group_creation_function` — their matching confs
- `RoundingSpec` dataclass — `ROUNDING_SPEC_CONF`

The five `@*_function` decorators (`@policy_function`, `@param_function`,
`@agg_by_p_id_function`, `@agg_by_group_function`, `@group_creation_function`)
additionally require the wrapped function to carry an annotation on every parameter and
on the return — missing annotations raise `PolicyFunctionDefinitionError` (or the
decorator's matching analogue) at decoration time, so the stack trace points at the
function's definition site rather than at an internal DAG-build helper.

### The auto-vectorized-wrapper annotation problem

Scalar policy functions are wrapped at DAG-build time by `ttsim.tt.vectorization` and
`ttsim.tt.rounding`. The wrapper closes over the user function but is itself called on
columns. If the wrapper inherits the user function's scalar annotations via
`functools.wraps`, the claw checks column inputs against scalar annotations and rejects
every legitimate call.

The fix uses two layers. The **inner** runtime executor — `numpy.vectorize`, the
AST-rewrite output, or the rounding callable — wraps the user function with
`functools.wraps(func, assigned=...)` that *omits* `__annotations__` and `__annotate__`
(the PEP 649 deferred alias). This layer carries no annotations and is never
beartype-decorated; its only job is to apply the auto-vectorisation or rounding logic.

```python
import functools

# Module-level so other wrappers can re-use it.
_WRAPPER_ASSIGNMENTS_NO_ANNOTATIONS = tuple(
    a for a in functools.WRAPPER_ASSIGNMENTS
    if a not in ("__annotations__", "__annotate__")
)


@functools.wraps(func, assigned=_WRAPPER_ASSIGNMENTS_NO_ANNOTATIONS)
def wrapper(...): ...
```

The **outer** layer is a real-parameter forwarder synthesised at DAG-build time. It
mirrors the wrapped function's parameter list verbatim (same names, same order) and
forwards every argument positionally. Two channels of annotation live on it:

- `__signature__` carries the **narrow** per-kind column-type strings (`FloatColumn`,
  `IntColumn`, `BoolColumn`). `dags`' annotation-consistency check reads these and
  distinguishes a producer typed `IntColumn` from a consumer expecting `BoolColumn`.
- `__annotations__` carries the **wide** numeric-or-scalar union —
  `FloatColumn | IntColumn | BoolColumn | ScalarFloat | ScalarInt | ScalarBool | 0-d-array`.
  beartype compiles its runtime check against this wider type so the boundary catches
  structural misuse (a string / mapping / `None` reaching a numeric node) without
  enforcing exact array dtype.

The forwarder is defined with its `__module__` pointed at `ttsim.typing`, so beartype
resolves the column-type strings against the module where the aliases live (rather than
the user-function module where they are not importable). It is then decorated with
`@beartype(conf=INTERNAL_CONF)`. The result is what the DAG sees and consumers call:
beartype catches structural misuse at this boundary, and `dags` sees concrete column
types for the consistency check.

Both `vectorize_function` and `RoundingSpec.apply_rounding` build this outer forwarder
through a shared helper (`build_beartype_checkable_wrapper`) so the synthesis pattern
stays single-source.

### Forward references, `from __future__ import annotations`, and recursive aliases

`from __future__ import annotations` defers all annotations to strings and breaks the
claw's runtime resolution. While Python 3.14's PEP 649 deferred evaluation makes the
pragma unnecessary, at the time of writing we still support 3.11–3.13, so the pragma
stays. The trade is local: only the specific names beartype must resolve at decoration
time are lifted out of `TYPE_CHECKING` blocks and into runtime scope — column aliases,
scalar aliases, `User*` aliases, `DashedISOString`, `Callable`, `Any`, `ModuleType`,
`datetime`, and the few `NestedX` families that decorated boundaries reference directly.
Everything else stays in `TYPE_CHECKING` to avoid import-cycle costs. A future bump to
`requires-python = ">=3.14"` will let the pragma go and the hoists with it.

Two annotation shapes resist the strip even after hoisting:

1. **Recursive aliases.** `NestedData = Mapping[str, "FloatColumn | ... | NestedData"]`
   and its siblings (`NestedTargetDict`, `NestedLookupDict`, `NestedStrings`,
   `PolicyEnvironment`, `FlatPolicyEnvironment`) contain stringified inner references
   that beartype's runtime forward-ref resolver cannot evaluate. The two-definition
   pattern resolves them:

   ```python
   if TYPE_CHECKING:
       NestedData = Mapping[str, "FloatColumn | IntColumn | BoolColumn | NestedData"]
   else:
       NestedData = Mapping[str, object]
   ```

   ty and IDE tooling see the narrow recursive form; beartype sees a coarse runtime form
   that always accepts the shape. The runtime check on these specific aliases degrades
   to "is a mapping with string keys" — weaker than the static type but consistent with
   the wider claw's intent to surface structural rather than per-leaf violations on
   nested trees.

1. **PEP 612 `ParamSpec`.**
   `def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:` is unresolvable under
   stringified annotations + the claw. The affected
   methods—`InterfaceFunction.__call__`/`ColumnFunction.__call__`/`ParamFunction.__call__`—
   are decorated `@no_type_check` until the migration to PEP 695 generic syntax (which
   allows the typing machinery to live without the `from __future__` pragma).

### Limitations

- **Callable-instance binding under normal `import`.** `@policy_function` and similar
  decorators return a callable dataclass instance (`PolicyFunction`) that wraps the raw
  function. The claw rebinds module-level names that point at such callable instances:
  under normal `import`, the module-level name becomes a bound method of `__call__`, so
  `isinstance(x, PolicyFunction)` fails. The standard policy-module loader
  (`orig_policy_objects.py` → `importlib.util.spec_from_file_location`) bypasses the
  claw, so policy modules loaded via
  `main(orig_policy_objects=OrigPolicyObjects(root=...))` are unaffected. The binding
  only bites users who `from my_pkg.policy_module import my_fn` and then perform
  `isinstance` checks on the imported name. See `beartype.md` ("The claw binds
  decorator-produced callable instances") for the workaround (use the claw-free loader,
  or read `.function` off the bound method).

## Related Work

- [pylcm PR #355](https://github.com/OpenSourceEconomics/pylcm/pull/355): Adopts the
  beartype framework in another project. This GEP follows its layering decisions
  verbatim (package claw + per-component decorators + project exceptions) and its naming
  (`_beartype_conf.py`, `INTERNAL_CONF`, `<COMPONENT>_CONF`).
- [beartype documentation](https://beartype.readthedocs.io/en/latest/): the
  `beartype.claw.beartype_package` API used here, the `violation_param_type` hook, the
  `On` strategy.
- [jaxtyping](https://docs.kidger.site/jaxtyping/): shape-aware array types consumed by
  beartype.
- [GEP 4](gep-4): defines policy functions, the scalar default, and the
  `vectorization_strategy` field that the per-decoration check uses.

## Implementation

The pattern — package-wide beartype claw, `TTSIMError` exception hierarchy, wide `UserX`
types at user boundaries narrowing to canonical `X` types internally — is implemented
across `ttsim`, `gettsim`, `gettsim-personas`, and `pylcm`. Each package's `__init__.py`
calls `beartype_package(...)` behind an env-var gate (`TTSIM_BEARTYPE_CLAW` and
`GETTSIM_BEARTYPE_CLAW`; `gettsim-personas` reuses `GETTSIM_BEARTYPE_CLAW` rather than a
separate switch). Following acceptance of this GEP (Option A), the gate defaults to on:
every `import` installs the claw, so a user writing a reform, a custom
`@policy_function`, or a pipeline on top of GETTSIM gets the runtime check without doing
anything. The env var stays in place as an opt-out (`GETTSIM_BEARTYPE_CLAW=0` disables
the claw for one process or environment) so anyone who hits a false positive — or who
wants the pre-GEP behaviour for their own code — can unblock themselves while the
rejection is triaged. Every pixi test environment continues to set the env var
explicitly, so CI exercises the claw on every run regardless of the default. See the
Discussion section for the resolution.

`.ai-instructions/modules/beartype.md` documents the conventions contributors follow:
when to use `UserX` vs `X`, how to add a new boundary decorator, the wrapper-annotation
rule, the claw-and-callable-instance gotcha, and the diagnostic workflow when a beartype
violation surfaces. The module is included in the `tier-a` profile by default so every
agent picks it up.

## Alternatives

### Module-level `@beartype` decorators instead of a package claw

Decorating each module's functions individually keeps the registration explicit but
leaves it possible to forget. The package claw makes coverage a property of import, not
of discipline. Pylcm tried the per-module approach first and migrated to the claw.

### A single `TTSIMError` with `code=` attribute

A flat exception with a discriminator is shorter to write but harder to catch
selectively, harder to grep for, and harder to document on a per-call site basis. The
named hierarchy maps one-to-one onto user-facing decorators and is the convention pylcm
chose.

### Keep scalar annotations on auto-vectorized wrappers, suppress the claw on them

Possible via a per-function opt-out (`@beartype(conf=BeartypeConf(...))` with
`claw_skip_mandatory_conf=True`). Rejected because the wrappers are the exact site at
which precise column-typed annotations *can* be synthesised at DAG-build time; an
opt-out would have left the boundary unchecked even when the synthesis is mechanical.
The layered inner-strip / outer-synthesised-forwarder pattern keeps the boundary
beartype-checkable.

### Validate `vectorization_strategy` consistency at TT-DAG-build time

Possible, but later in the lifecycle than at `@policy_function` decoration time.
Validation at decoration gives the user a stack trace pointing at their function
definition, not at an internal DAG-build helper. The full contract specification lives
in the GEP 4 update.

### Custom per-function type checks instead of runtime checking

The pre-GEP approach — `_fail_if_*` helpers in `fail_if.py` per validated input —
remains valid but does not scale. Adding a check requires editing a separate file and
remembering to wire it in. The claw eliminates the wiring step; the cost is exactly one
mandatory annotation per parameter, which the codebase already carries.

### Leave annotations on user-written functions optional

Possible: `_fail_if_missing_annotations` could downgrade to a warning, and beartype
would silently skip un-annotated parameters. Rejected because the goal — "every function
in the package is checked" — degrades into "some functions are checked, some are not",
with no in-band signal to the reader that the missing check is deliberate vs.
accidental. Since every existing `gettsim` policy function already carries full
annotations, the strict policy enforces an existing convention, not a new requirement.

## Discussion

Resolved 2026-06-02 in favour of **Option A** — runtime checking on by default for
everyone — with an explicit env-var opt-out retained.

A genuinely open question at the point of asking for feedback on this GEP was the
default for *user-written* code: reforms, custom `@policy_function`s, and microsim
pipelines built on top of GETTSIM. Our own packages (`ttsim`, `gettsim`, and
`gettsim-personas`) are already checked on every commit because the claw is on in every
test environment; the decision was what `import gettsim` should do in a user's own
process.

- **Option A — on by default for everyone (accepted).** Dropping the opt-in means every
  `import gettsim` / `import ttsim` / `import gettsim_personas` installs the claw
  automatically, so a type error is surfaced loudly at the boundary the user wrote,
  without them doing anything. This matters most for AI-assisted development: agents
  writing reforms see type violations immediately, at the boundary, with a message they
  can iterate on — rather than producing code that runs silently with the wrong types
  and surfaces the bug far from its cause. In a world where most new GETTSIM code is
  written with AI assistance, the users least likely to set an opt-in flag are exactly
  the ones whose code most needs the check.
- **Option B — opt-in for user code (rejected).** Keeping the switch off by default
  removes all risk of a user pipeline breaking, but leaves enforcement conditional on
  the user remembering to set an env var. "Your inputs are checked unless someone forgot
  to set an env var" is not the guarantee the GEP promises, and it withholds the safety
  net from precisely the AI-assisted workflows that benefit most.
- **Opt-out caveat (Christian Pugnaghi Zimpelmann).** "Remove the switch" was narrowed
  to "flip the default and keep the switch as a fallback": the env var stays as an
  opt-out, so `GETTSIM_BEARTYPE_CLAW=0` (and the `TTSIM_BEARTYPE_CLAW` analogue)
  disables the claw for one process or environment. Anyone who hits a false positive —
  or who wants the pre-GEP behaviour for their own code — can unblock themselves while
  the rejection is triaged.

## References and Footnotes

- [GEP 09 thread on Zulip](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2009)
- [pylcm PR #355 for the originating precedent](https://github.com/OpenSourceEconomics/pylcm/pull/355)
- [beartype](https://beartype.readthedocs.io)
- [jaxtyping](https://docs.kidger.site/jaxtyping/)
- [PEP 484 numeric tower](https://peps.python.org/pep-0484/#the-numeric-tower)
- [PEP 649 (deferred annotation evaluation)](https://peps.python.org/pep-0649/)

## Copyright

This document has been placed in the public domain.
