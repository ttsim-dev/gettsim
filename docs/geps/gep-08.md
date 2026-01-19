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
  * 2025-01-16
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

**Scope**: This GEP covers the YAML parameter format and the internal representation
used by `piecewise_polynomial()`. It does not change the mathematical evaluation logic.

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

Note: The domain starts at 0 rather than `-inf` since disability percentages (Grad der
Behinderung) are non-negative. Values outside the defined domain return NaN.

### Piecewise Linear Example

```yaml
parameter_solidaritätszuschlag:
  type: piecewise_linear
  2021-01-01:
    - interval: "[0, 16956)"
      intercept: 0
      slope: 0
    - interval: "[16956, 31528)"
      intercept: 0      # at lower bound
      slope: 0.119
    - interval: "[31528, inf)"
      intercept: 1734   # at lower bound (continuation)
      slope: 0.055
```

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
1. A migration script will be provided to automate this

The Python API (`piecewise_polynomial()`) will remain unchanged—only the internal
`PiecewisePolynomialParamValue` representation changes.

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
- Infinity bounds are always open in standard mathematical convention, but we write
  `[-inf, ...)` and `[..., inf)` for clarity (the closing bracket/parenthesis at
  infinity is purely syntactic)

### Parameter Structure

For `piecewise_constant`:

```yaml
- interval: "[a, b)"
  intercept: <number>
```

For `piecewise_linear`:

```yaml
- interval: "[a, b)"
  intercept: <number>  # value at lower bound
  slope: <number>
```

For `piecewise_quadratic`:

```yaml
- interval: "[a, b)"
  intercept: <number>   # value at lower bound
  slope: <number>       # first derivative at lower bound
  curvature: <number>   # half of second derivative (coefficient of x²)
```

For `piecewise_cubic`:

```yaml
- interval: "[a, b)"
  intercept: <number>
  slope: <number>
  curvature: <number>
  cubic: <number>       # coefficient of x³
```

#### Rationale for Coefficient Naming

The descriptive names (`intercept`, `slope`, `curvature`, `cubic`) were chosen over
generic notation like `p0`, `p1`, `p2`, `p3` or `coefficients: [...]` for several
reasons:

1. **Reduces order-confusion errors**: A primary motivation for refactoring piecewise
   polynomials (see
   [issue #901](https://github.com/iza-institute-of-labor-economics/gettsim/issues/901))
   was that the previous format led to mistakes in specifying coefficients. Descriptive
   names make the meaning unambiguous.

1. **Mathematical validity**: "Curvature" is mathematically justified—for a polynomial
   f(x) = c₀ + c₁x + c₂x², the second derivative f''(x) = 2c₂, so `curvature` directly
   relates to the mathematical concept.

1. **Self-documenting YAML**: When reading parameter files, `slope: 0.119` immediately
   conveys meaning, whereas `p1: 0.119` requires looking up the convention.

### Internal Representation

The YAML list is converted to portion's `IntervalDict` at load time:

```python
import portion

# YAML input:
# - interval: "[0, 20)"
#   intercept: 0
# - interval: "[20, 30)"
#   intercept: 384
# ...

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

# Query within domain
params[25]  # Returns {"intercept": 384}

# Query outside domain
params[-5]  # Returns None (converted to NaN at evaluation time)
```

### Behavior Outside Defined Domain

When `piecewise_polynomial()` is called with a value outside the defined intervals, it
returns `NaN`. This design choice reflects several considerations:

1. **JAX compatibility**: JAX's JIT compilation model does not support raising
   exceptions during traced computation. Returning NaN is the standard approach for
   signaling undefined results in array computations.

1. **NaN propagation**: NaN values propagate through subsequent calculations, making it
   easy to identify affected outputs without silent failures.

1. **Debugging**: Users can check for NaN in results to identify data outside expected
   ranges, which often indicates data quality issues.

1. **Natural domains**: Many policy parameters have natural domains (e.g., income ≥ 0, 0
   ≤ percentage ≤ 100). Forcing specification of behavior outside these domains adds
   noise to the parameter files without reflecting actual policy.

### Validation

At parameter load time, the system will validate:

1. **Contiguity**: Intervals must be contiguous (no gaps within the defined domain)
1. **No overlaps**: Intervals must not overlap (portion handles this automatically)
1. **Ordering**: Intervals must be specified in ascending order in the YAML file; the
   parser will raise an error if intervals are out of order
1. **Continuity** (optional, for linear+): At boundaries, the polynomial values should
   match (can be a warning rather than error)

Note that full coverage of `(-inf, inf)` is **not** required. The defined domain is
simply the union of all specified intervals.

## Related Work

- **[portion](https://pypi.org/project/portion/)**: Python library for interval
  arithmetic, provides the `IntervalDict` data structure
- **[pylcm grid specification](https://github.com/OpenSourceEconomics/pylcm/pull/211)**:
  Uses similar interval notation for `PiecewiseLinSpacedGrid`
- **Mathematical notation**: Standard interval notation from real analysis

### Note on portion Library

Users who programmatically modify `PiecewisePolynomialParamValue` objects will interact
with the portion library's `IntervalDict` API. While this introduces a learning curve,
the trade-off is worthwhile:

- **Validation guarantees**: portion automatically prevents overlapping intervals and
  provides type-safe interval operations
- **Limited exposure**: Most users only write YAML parameter files and never interact
  with portion directly—it remains an implementation detail
- **Well-maintained**: portion is a mature library with comprehensive documentation

## Implementation

1. **Add portion dependency** to ttsim-backend
1. **Create interval parser**: Parse strings like `"[20, 30)"` into portion intervals
1. **Update parameter loading**: Convert YAML to `IntervalDict`-based representation
1. **Update `piecewise_polynomial()`**: Query `IntervalDict` instead of searching
   arrays; return NaN for queries outside defined domain
1. **Write migration script**: Convert existing YAML files to new format
1. **Update documentation**: GEP 3 (parameters) and user guides

## Alternatives

### Alternative 1: Keep Current Format with Better Documentation

Pros: No breaking change Cons: Doesn't solve the fundamental usability issues

### Alternative 2: Threshold-Based Format

```yaml
thresholds: [20, 30, 40, 50, ...]
intercepts: [0, 384, 620, 860, ...]
```

Pros: Compact Cons: Still doesn't clarify boundary conditions; easy to misalign
thresholds and intercepts

### Alternative 3: Interval Strings as Dictionary Keys

```yaml
2021-01-01:
  "[0, 20)":
    intercept: 0
  "[20, 30)":
    intercept: 384
  "[30, 40)":
    intercept: 620
```

Pros: More compact (no `interval:` key); direct correspondence to portion's
`IntervalDict` API. Cons: Less readable—having the interval information as a key on the
left makes it harder to visually scan the file compared to having it as a value on the
right.

### Alternative 4: Use portion Syntax Without the Library

Parse interval strings manually without depending on portion.

Pros: No new dependency Cons: Reinventing the wheel; portion is well-tested and
maintained

### Alternative 5: Require Full Real Line Coverage

Require intervals to cover `(-inf, inf)` without gaps, raising validation errors
otherwise.

Pros: Guarantees a defined value for any input; no NaN surprises in output. Cons: Forces
specification of behavior for domains that don't reflect actual policy (e.g., negative
income); adds verbosity; arbitrary default values for out-of-range inputs could mask
data errors.

## Discussion

- [gettsim #901](https://github.com/iza-institute-of-labor-economics/gettsim/issues/901):
  Original issue documenting errors in piecewise polynomial specifications that
  motivated this refactor
- [pylcm #210](https://github.com/OpenSourceEconomics/pylcm/issues/210): Discussion on
  interval specification for grids
- [pylcm #211](https://github.com/OpenSourceEconomics/pylcm/pull/211): Implementation of
  `PiecewiseLinSpacedGrid` using portion

## References and Footnotes

## Copyright

This document has been placed in the public domain.
