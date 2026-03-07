(gep-08)=

# GEP 8 — Refactor Piecewise Polynomials

```{list-table}
- * Author
  * [Hans-Martin von Gaudecker](https://github.com/hmgaudecker)
- * Status
  * Draft
- * Type
  * Standards Track
- * Created
  * 2025-01-20
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/channel/309998-GEPs/topic/GEP.2008/near/573021794)
```

## Abstract

This GEP proposes refactoring the piecewise polynomial specification format to use
interval notation inspired by the [portion](https://pypi.org/project/portion/) library.
The new format will be more intuitive, eliminate the confusing "k intervals with k-1
cutoffs" pattern, and make boundary conditions (open/closed) explicit.

## Motivation and Scope

The current piecewise polynomial parameter format has several usability problems:

1. **Confusing interval/cutoff relationship**: Users must specify k numbered intervals
   (0, 1, 2, ...) with k-1 internal thresholds, plus explicit `lower_threshold: -inf`
   and `upper_threshold: inf` on the boundary intervals. This mental model is
   error-prone.

1. **Implicit boundary conditions**: It's unclear whether thresholds are inclusive or
   exclusive. For example, if interval 0 has `upper_threshold: 100` and interval 1
   starts at `lower_threshold: 100`, which interval does exactly 100 belong to?

1. **Verbose specification**: Each interval requires manual numbering and redundant
   threshold specification (the upper threshold of interval k equals the lower threshold
   of interval k+1).

1. **Hard to read and maintain**: The numbered intervals obscure the actual policy
   structure. Compare reading "interval 3 starts at 45" versus "the interval \[45, 55)
   has value X".

1. **Forced coverage of irrelevant domains**: The current format requires specifying
   behavior for the entire real line, even when parameters are only meaningful for a
   subset (e.g., non-negative values for income or age).

1. **Unintuitive internal array shapes**: The underlying implementation uses a `rates`
   array with shape `(n_coefficients, n_intervals)`. This transposed layout is
   counter-intuitive compared to standard linear algebra conventions and makes manual
   inspection or construction of these arrays error-prone (see
   [ttsim#5](https://github.com/ttsim-dev/ttsim/issues/5)).

**Scope**: This GEP covers the YAML parameter format and the internal representation
used by `piecewise_polynomial()`. It implies updating `piecewise_polynomial()` to
support partial domains (returning NaN outside). It **preserves** the existing
mathematical evaluation logic (polynomials evaluated on local coordinates relative to
the interval start).

## Usage and Impact

### Current Format (Before)

```yaml
parameter_behindertenpauschbetrag:
  type: piecewise_constant
  2021-01-01:
    0:
      lower_threshold: -inf
      intercept_at_lower_threshold: 0
    1:
      lower_threshold: 20
      intercept_at_lower_threshold: 384
    2:
      lower_threshold: 30
      intercept_at_lower_threshold: 620
    # ... more intervals ...
    9:
      lower_threshold: 100
      upper_threshold: inf
      intercept_at_lower_threshold: 2840
```

### Proposed Format (After)

```yaml
parameter_behindertenpauschbetrag:
  type: piecewise_constant
  2021-01-01:
    reference: Art. 1 G. v. 09.12.2020 BGBL. I S. 2770.
    intervals:
      - interval: "[0, 20)"
        intercept: 0
      - interval: "[20, 30)"
        intercept: 384
      - interval: "[30, 40)"
        intercept: 620
      # ... more intervals ...
      - interval: "[100, inf)"
        intercept: 2840
```

Note: The domain starts at 0 rather than `(-inf, ...)` since disability percentages
(Grad der Behinderung) are non-negative. Values outside the defined domain return NaN.

### Piecewise Linear Example

```yaml
parameter_solidaritätszuschlag:
  type: piecewise_linear
  2021-01-01:
    reference: Artikel 1 G. v. 10.12.2019 BGBl. I S. 2115.
    intervals:
      - interval: "[0, 16956)"
        intercept: 0
        slope: 0
      - interval: "[16956, 31528)"
        # intercept is optional if continuous from previous interval
        slope: 0.119
      - interval: "[31528, inf)"
        # intercept is optional if continuous from previous interval
        slope: 0.055
```

### `updates_previous` Example

When only some coefficients change between dates, `updates_previous` avoids restating
the entire definition. Each interval listed in the update must have bounds that exactly
match one of the base entry's intervals. Only the specified coefficients are replaced;
all other coefficients and any intervals not listed in the update are carried over
unchanged. The interval structure (bounds and ordering) is never modified by an update.

```yaml
parameter_solidaritätszuschlag:
  type: piecewise_linear
  2021-01-01:
    reference: Artikel 1 G. v. 10.12.2019 BGBl. I S. 2115.
    intervals:
      - interval: "[0, 16956)"
        intercept: 0
        slope: 0
      - interval: "[16956, 31528)"
        slope: 0.119
      - interval: "[31528, inf)"
        slope: 0.055
  2023-01-01:
    updates_previous: true
    reference: Art. 4 G. v. 08.12.2022 BGBl. I S. 2230.
    intervals:
      - interval: "[16956, 31528)"
        slope: 0.11
```

Here, only the second interval's `slope` changes from 0.119 to 0.11. The interval bounds
`[16956, 31528)` exactly match the base entry. The first and third intervals are carried
over unchanged, yielding a resolved entry with the same three intervals and the same
bounds as before. An error is raised if an update interval's bounds do not match any
base interval.

### Benefits

1. **Self-documenting**: The interval `[20, 30)` immediately shows the range and
   boundary conditions
1. **No manual numbering**: Intervals are keyed by their range, not arbitrary indices
1. **Explicit boundaries**: `[` means closed (inclusive), `(` means open (exclusive)
1. **Natural domains**: Parameters only need to cover their meaningful range; queries
   outside return NaN
1. **Validation**: The portion library can validate that intervals are contiguous
   without gaps or overlaps within the defined domain

## Backward Compatibility

This is a breaking change for parameter files. Migration requires:

1. Converting existing YAML files to the new format
1. If intercepts are omitted in the new format, they will be calculated automatically to
   ensure continuity, preserving the behavior of the current implementation.

The Python API (`piecewise_polynomial()`) will remain unchanged in signature, but its
behavior will change to return NaN for out-of-domain inputs.

## Detailed Description

### Interval Syntax

The interval syntax follows mathematical convention:

| Syntax   | Meaning                    |
| -------- | -------------------------- |
| `[a, b]` | Closed interval: a ≤ x ≤ b |
| `(a, b)` | Open interval: a < x < b   |
| `[a, b)` | Closed-open: a ≤ x < b     |
| `(a, b]` | Open-closed: a < x ≤ b     |

Special values:

- `-inf` for negative infinity
- `inf` for positive infinity
- Infinity bounds must always be open, following standard mathematical convention (e.g.,
  `(-inf, 0)` or `[100, inf)`). Writing `[-inf` or `inf]` will result in a validation
  error.

### Parameter Structure and Mathematical Evaluation

The polynomials are evaluated using **local coordinates** relative to the lower bound of
the interval. For an input $x$ falling into an interval $[a, b)$, the value is
calculated as:

$$ f(x) = c_0 + c_1 (x-a) + c_2 (x-a)^2 + c_3 (x-a)^3 $$

Where the coefficients correspond to the YAML keys as follows:

| YAML Key    | Symbol | Meaning                                            |
| ----------- | ------ | -------------------------------------------------- |
| `intercept` | $c_0$  | Value at lower bound ($f(a)$)                      |
| `slope`     | $c_1$  | First derivative at lower bound ($f'(a)$)          |
| `quadratic` | $c_2$  | Coefficient of $x^2$ (equals $\frac{1}{2}f''(a)$)  |
| `cubic`     | $c_3$  | Coefficient of $x^3$ (equals $\frac{1}{6}f'''(a)$) |

**Note on Intervals starting at -Infinity**: For intervals of the form `(-inf, b)`, the
lower bound $a$ is undefined. In this case, the implementation treats the coordinate
term $(x-a)$ as $0$. Consequently, such intervals **must be constant** (only `intercept`
is used; `slope`, `quadratic`, etc. have no effect). This matches the existing behavior.

#### Parameter Examples

Each list item under `intervals` has a required `interval` key and optional coefficient
keys. Metadata (`reference`, `note`) belongs on the date entry mapping, not on
individual interval items (see {ref}`GEP 3 <gep-3-structure-yaml-files>`).

For `piecewise_constant`:

```yaml
intervals:
  - interval: "[a, b)"
    intercept: <number>
```

For `piecewise_linear`:

```yaml
intervals:
  - interval: "[a, b)"
    intercept: <number>  # c_0
    slope: <number>      # c_1
```

For `piecewise_quadratic`:

```yaml
intervals:
  - interval: "[a, b)"
    intercept: <number>   # c_0
    slope: <number>       # c_1
    quadratic: <number>   # c_2
```

For `piecewise_cubic`:

```yaml
intervals:
  - interval: "[a, b)"
    intercept: <number>
    slope: <number>
    quadratic: <number>
    cubic: <number>       # c_3
```

### Internal Representation

At load time, the `intervals` list from the YAML is converted to portion's
`IntervalDict`:

```python
import portion

# YAML input:
# intervals:
#   - interval: "[0, 20)"
#     intercept: 0
#   - interval: "[20, 30)"
#     intercept: 384
#   ...

# Converted to:
params = portion.IntervalDict(
    {
        portion.closedopen(0, 20): {"intercept": 0},
        portion.closedopen(20, 30): {"intercept": 384},
        portion.closedopen(30, 40): {"intercept": 620},
        # ...
        portion.closedopen(100, portion.inf): {"intercept": 2840},
    }
)
```

### Internal Array Representation

For vectorized execution (e.g., in JAX), the `IntervalDict` is compiled into dense
arrays. To address the usability issues identified in
[TTSIM #5](https://github.com/ttsim-dev/ttsim/issues/5), the array with coefficients
will be standardized to shape `(n_intervals, n_coefficients)`.

For example, a piecewise linear function with 3 intervals will have a coefficient array
of shape `(3, 2)`:

```python
# [
#     [intercept_0, slope_0],
#     [intercept_1, slope_1],
#     [intercept_2, slope_2],
# ]
coefficients = np.array(
    [
        [0.0, 0.0],
        [0.0, 0.119],
        [0.0, 0.055],
    ]
)
```

This layout intuitively maps each row to a specific interval, improving readability and
aligning with standard data conventions.

### Named Access to Coefficients

The `PiecewisePolynomialParamValue` object supports accessing individual intervals and
their coefficients by name. For example, given a parameter with three intervals:

```python
# Access the slope of the first interval:
parameter_solidaritätszuschlag[0].slope

# Access the intercept of the second interval:
parameter_solidaritätszuschlag[1].intercept
```

This is useful in policy functions that need to reference specific coefficients
directly, without calling `piecewise_polynomial()`.

### Behavior Outside Defined Domain

When `piecewise_polynomial()` is called with a value outside the defined intervals, it
returns `NaN`. This design choice reflects several considerations:

1. **JAX compatibility**: JAX's JIT compilation model does not support raising
   exceptions during traced computation.
1. **NaN propagation**: NaN values propagate, making it as easy as possible to identify
   affected outputs.
1. **Debugging**: If the column that `piecewise_polynomial` operates on is provided as
   input, we can easily identify data outside expected ranges (see
   [#402](https://github.com/ttsim-dev/gettsim/issues/402)).
1. **Natural domains**: Allows specifying parameters only for their meaningful range
   (e.g., income ≥ 0).

### Validation

At parameter load time, the system will validate:

1. **Contiguity**: Intervals must be contiguous (no gaps within the defined domain)
1. **No overlaps**: Intervals must not overlap (portion handles this automatically)
1. **Ordering**: Intervals must be specified in ascending order in the YAML file
1. **Continuity** (optional, for linear+): At boundaries, the polynomial values should
   match (can be a warning rather than error)
1. **`updates_previous` compatibility**: Each update interval must exactly match a base
   interval's bounds; only coefficients are replaced

Full coverage of `(-inf, inf)` is **not** required.

## Related Work

- **[portion](https://pypi.org/project/portion/)**: Python library for interval
  arithmetic, provides the `IntervalDict` data structure
- **[pylcm grid specification](https://github.com/OpenSourceEconomics/pylcm/pull/211)**:
  Uses similar interval notation

## Implementation

1. **Add portion dependency** to ttsim-backend
1. **Create interval parser**: Parse strings like `"[20, 30)"` into portion intervals
1. **Update parameter loading**: Convert YAML to `IntervalDict`-based representation
1. **Update `piecewise_polynomial()`**: Query `IntervalDict` instead of searching
   arrays; return NaN for queries outside defined domain. Ensure evaluation logic uses
   local coordinates relative to interval start.
1. **Write migration script**: Convert existing YAML files to new format.
1. **Update documentation**: GEP 3 (parameters) and user guides

## Alternatives

### Alternative 1: Keep Current Format with Better Documentation

Pros: No breaking change. Cons: Doesn't solve usability issues.

### Alternative 2: Generic Coefficient Names (`p0`, `p1`, `p2`, `p3`)

Instead of descriptive names (`intercept`, `slope`, `quadratic`, `cubic`), use generic
notation like `p0`, `p1`, `p2`, `p3` or `coefficients: [...]`.

We chose descriptive names because:

1. **Reduces order-confusion errors**: Descriptive names make the meaning unambiguous.
1. **Consistency**: `slope` (linear), `quadratic`, and `cubic` provide a clear
   progression that aligns with the polynomial terms they represent.
1. **Precision**: `quadratic` unambiguously refers to the coefficient $c_2$, whereas
   terms like "curvature" could be confused with the second derivative ($2 \cdot c_2$).
1. **Self-documenting YAML**: `slope: 0.119` immediately conveys meaning.

## Discussion

- [ttsim #5](https://github.com/ttsim-dev/ttsim/issues/5): Proposal to improve the
  interface for piecewise polynomials (rates shape)
- [gettsim #901](https://github.com/iza-institute-of-labor-economics/gettsim/issues/901):
  Original issue
- [pylcm #210](https://github.com/OpenSourceEconomics/pylcm/issues/210): Discussion on
  interval specification

## Copyright

This document has been placed in the public domain.
