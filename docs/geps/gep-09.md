(gep-9)=

# GEP 9 — Runtime Type Checking and the User/Canonical Type Split

```{list-table}
- * Author
  * [Hans-Martin von Gaudecker](https://github.com/hmgaudecker)
- * Status
  * Draft
- * Type
  * Standards Track
- * Created
  * 2026-05-17
- * Resolution
  * Pending — see [#GEPs](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2009)
```

## Abstract

This GEP introduces runtime type checking across `ttsim`, `gettsim`, and
`gettsim-personas` via [beartype](https://beartype.readthedocs.io)'s package claw, and
formalises the two-tier type vocabulary that the claw makes enforceable: a wide `UserX`
family at the user boundary and a narrow canonical `X` family inside the package. Each
user-facing entry point and decorator is wrapped with an explicit beartype configuration
that re-raises type-violations as a documented subclass of `TTSIMError`. Auto-vectorized
policy-function wrappers have their inherited scalar annotations stripped so that the
claw checks the wrapper against its true (column) signature.

## Motivation and Scope

The ttsim DAG accepts a wide range of objects at its outer boundary — pandas Series,
numpy arrays, Python scalars, JAX arrays — and converts them internally into a narrower,
performance-oriented representation: jaxtyping-shaped JAX arrays for columns and Python
or numpy scalars for parameters. Today this distinction is implicit. `typing.py` exposes
a single `Array`-based vocabulary, the canonical internal types are not named separately
from their user-friendly supersets, and nothing enforces either contract at runtime.
Three problems follow:

1. **Silent contract drift.** A policy function annotated `int` that is invoked with a
   `jax.Array` works today, fails tomorrow on a backend swap, and has no guard at the
   boundary that would surface the mismatch with a useful error. Annotations are
   documentation, not specification.

1. **No single boundary for canonicalisation.** Every code path that takes user input
   re-implements the cast from "pandas Series or Python float or numpy scalar" to "JAX
   float column / numpy float scalar". The conversion is scattered, inconsistent, and
   impossible to type-check.

1. **Indistinguishable bug classes.** When a TT DAG raises `TypeError`, the user cannot
   tell whether they passed bad data, mis-declared a policy function, or hit an internal
   ttsim bug. There is no exception vocabulary that maps to architectural layers.

These cost real time during model development and during workshop teaching. The
[pylcm beartype rollout](https://github.com/OpenSourceEconomics/pylcm/pull/355)
addressed the same three problems for the life-cycle-model framework with a package-wide
AST-rewriting claw, layered project exceptions, and a formal boundary-vs-canonical type
split. This GEP adopts the same pattern for the ttsim ecosystem.

**Scope.** The GEP covers `ttsim`, `gettsim`, and `gettsim-personas`. `soep-preparation`
is excluded — it ingests survey microdata with idiosyncratic shape contracts that the
claw does not buy us much on. The `@policy_function` dual-mode contract (scalar default
vs. column-direct via `vectorization_strategy="not_required"`) is touched here only
insofar as the claw makes it enforceable; the full contract is specified in a separate
update to {ref}`GEP 4 <gep-4>`.

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

Code that takes user input declares its parameters with `UserX` aliases. The same code's
internal callees declare narrow canonical aliases (`X`). A small set of
`_canonicalize_*` functions sits at the boundary and is the only place that returns the
canonical form from the wide form. Once past canonicalisation, no internal function ever
sees a `pd.Series` or a bare Python `float` where a column is expected.

### Same runtime, more discoverable failures

The claw adds an O(n) container check on entry to every clawed function, but ttsim's
entry points are called rarely (per-run, not per-row), so the cost is invisible at the
boundary. Hot inner loops are JIT-compiled and beartype's AST-rewritten checks live
outside the JIT region.

## Backward Compatibility

User-facing public API is unchanged. Anyone whose code raised `TypeError`, `ValueError`,
or a bare `Exception` from inside ttsim will now see a `TTSIMError` subclass instead.
Code that catches `Exception` keeps working; code that catches narrow built-in
exceptions will have to broaden to `TTSIMError` (or the relevant subclass). Two
pre-existing exception types are hoisted into the hierarchy without changing their
definition site: `ConflictingActivePeriodsError` and `TranslateToVectorizableError`.
Both keep their original import path.

Internal callers that relied on the wide-form types (passing a `pd.Series` into a
function with column-typed parameters) will surface as `BeartypeCallHintViolation` from
the internal claw. These are by definition ttsim bugs, not user-facing changes; the fix
is to canonicalise at the boundary instead of pushing wide types deeper.

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

The wide forms are restricted to the user boundary. Inside ttsim, the narrow forms are
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

### The auto-vectorized-wrapper annotation problem

Scalar policy functions are wrapped at DAG-build time by `ttsim.tt.vectorization` and
`ttsim.tt.rounding`. The wrapper closes over the user function but is itself called on
columns. If the wrapper inherits the user function's scalar annotations via
`functools.wraps`, the claw checks column inputs against scalar annotations and rejects
every legitimate call.

Wrappers therefore copy everything from the wrapped function *except* annotations:

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

Both `__annotations__` (eager) and `__annotate__` (PEP 649 deferred, Python 3.14+) are
excluded.

This is the right fix for today: the wrapper's signature is generically typed and the
claw stops mistakenly enforcing the user's scalar contract on column inputs. It is also
a stop-gap. The wrapper's *true* signature — column types for every input that was
scalar in the user function — is knowable at DAG-build time. A follow-up will synthesise
precise column-typed annotations on each wrapper as it is constructed, so the claw can
again check the boundary. The annotation strip stays until that follow-up lands; it is
local, explicit, and trivially reversible.

### Forward references, `from __future__ import annotations`, and recursive aliases

`from __future__ import annotations` defers all annotations to strings and breaks the
claw's runtime resolution. Python 3.14's PEP 649 deferred evaluation makes the pragma
unnecessary; the AI coding standards in this repo already prohibit it for 3.14+
projects.

`ttsim`, `gettsim`, and `gettsim-personas` all keep `requires-python = ">=3.11"`. PEP
649 is unavailable on 3.11–3.13, so the pragma stays. The trade is local: only the
specific names beartype must resolve at decoration time are lifted out of
`TYPE_CHECKING` blocks and into runtime scope — column aliases, scalar aliases, `User*`
aliases, `DashedISOString`, `Callable`, `Any`, `ModuleType`, `datetime`, and the few
`NestedX` families that decorated boundaries reference directly. Everything else stays
in `TYPE_CHECKING` to avoid import-cycle costs. A future bump to
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
   stringified annotations + the claw. The affected methods —
   `InterfaceFunction.__call__`/`ColumnFunction.__call__`/`ParamFunction.__call__` — are
   decorated `@no_type_check` until the migration to PEP 695 generic syntax (which
   allows the typing machinery to live without the `from __future__` pragma).

## Related Work

- [pylcm PR #355](https://github.com/OpenSourceEconomics/pylcm/pull/355): Adopts
  beartype across the life-cycle-model framework. This GEP follows its layering
  decisions verbatim (package claw + per-component decorators + project exceptions) and
  its naming (`_beartype_conf.py`, `INTERNAL_CONF`, `<COMPONENT>_CONF`).
- [beartype documentation](https://beartype.readthedocs.io/en/latest/): the
  `beartype.claw.beartype_package` API used here, the `violation_param_type` hook, the
  `On` strategy.
- [jaxtyping](https://docs.kidger.site/jaxtyping/): shape-aware array types consumed by
  beartype.
- [GEP 4](gep-4): defines policy functions, the scalar default, and the
  `vectorization_strategy` field that the per-decoration check uses.

## Implementation

The rollout proceeds as three coordinated pull requests — one per package — merged
together so no intermediate state has a partially-installed claw. Each PR follows the
same shape:

1. **Add the exception hierarchy.** `<package>/exceptions.py` with `<Package>Error` (or,
   for `gettsim`, the re-exported `TTSIMError`) and the boundary subclasses. Hoist any
   pre-existing exception types into the hierarchy by widening their base class; keep
   the definition site so existing imports keep working; re-export from `exceptions.py`
   for discoverability.

1. **Add the conf factory.** `<package>/_beartype_conf.py` exposing `INTERNAL_CONF` and
   one named conf per boundary exception.

1. **Lift typing aliases out of `TYPE_CHECKING` and widen them.** The column aliases
   move to module top level and switch to `Array | np.ndarray`. Add the `UserX` family.
   Add the narrow `ScalarX` family. Keep `from __future__ import annotations` while
   `requires-python` includes 3.11–3.13; lift only the specific names that decorated
   boundaries need to resolve at runtime. Apply the two-definition pattern to recursive
   aliases (see Detailed Description).

1. **Add `_canonicalize_*` boundary helpers** for every entry point that today
   implicitly converts user inputs. Typed `UserX → X`. Push the per-call casts out of
   internal helpers.

1. **Register the claw** at the top of `<package>/__init__.py`, before any submodule
   import. During the rollout PR, guard with
   `if os.environ.get("<PACKAGE>_BEARTYPE_CLAW", "0") != "0":` so reviewers can run with
   and without. The env-var gate is removed in a follow-up immediately after merge.

1. **Stack `@beartype(conf=<COMPONENT_CONF>)`** on every user-facing entry point and
   decorator listed in the Detailed Description.

1. **Strip annotations on auto-vectorized wrappers** in `ttsim.tt.vectorization` and
   `ttsim.tt.rounding` via `_WRAPPER_ASSIGNMENTS_NO_ANNOTATIONS`.

1. **Pin dependencies** in `pyproject.toml`: `beartype >= 0.18` (for
   `violation_param_type`), `jaxtyping >= 0.2`. Re-lock with `pixi lock` in the same
   commit.

CI runs with `<PACKAGE>_BEARTYPE_CLAW=1` for the rollout PR. Once merged, the env-var
gate is removed and the claw runs in every pixi environment by default — `py314`,
`py314-jax`, `py314-cuda`, `py314-metal`, `type-checking`, `type-checking-jax`. CI
failure on a missing or mistaken annotation is a build break, not a warning.

`.ai-instructions/modules/beartype.md` documents the conventions for contributors: when
to use `UserX` vs `X`, how to add a new boundary decorator, the wrapper-annotation rule,
and the diagnostic workflow when a beartype violation surfaces. The module is included
in the `tier-a` profile by default so every agent picks it up.

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
which a precise column-typed annotation will eventually be synthesised; an opt-out now
would have to be undone then. The annotation strip is a smaller, more local change.

### Validate `vectorization_strategy` consistency at TT-DAG-build time

Possible, but later in the lifecycle than at `@policy_function` decoration time.
Validation at decoration gives the user a stack trace pointing at their function
definition, not at an internal DAG-build helper. The full contract specification lives
in the GEP 4 update.

## Discussion

- `[#GEPs]` thread on Zulip for GEP 9 (to be linked once opened).
- pylcm PR #355 for the originating precedent.

## References and Footnotes

- pylcm beartype rollout — <https://github.com/OpenSourceEconomics/pylcm/pull/355>
- beartype — <https://beartype.readthedocs.io>
- jaxtyping — <https://docs.kidger.site/jaxtyping/>
- PEP 484 numeric tower — <https://peps.python.org/pep-0484/#the-numeric-tower>
- PEP 649 (deferred annotation evaluation) — <https://peps.python.org/pep-0649/>

## Copyright

This document has been placed in the public domain.
