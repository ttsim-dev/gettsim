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
    "[-inf, 20)":
      intercept: 0
    "[20, 30)":
      intercept: 384
    "[30, 40)":
      intercept: 620
    # ... more intervals ...
    "[100, inf]":
      intercept: 2840
```

### Piecewise Linear Example

```yaml
parameter_solidaritätszuschlag:
  type: piecewise_linear
  2021-01-01:
    "[-inf, 16956)":
      intercept: 0
      slope: 0
    "[16956, 31528)":
      intercept: 0      # at lower bound
      slope: 0.119
    "[31528, inf]":
      intercept: 1734   # at lower bound (continuation)
      slope: 0.055
```

### Benefits

1. **Self-documenting**: The interval `[20, 30)` immediately shows the range and
   boundary conditions
1. **No manual numbering**: Intervals are keyed by their range, not arbitrary indices
1. **Explicit boundaries**: `[` means closed (inclusive), `(` means open (exclusive)
1. **Validation**: The portion library can validate that intervals cover the domain
   without gaps or overlaps

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
  `[-inf, ...)` and `[..., inf]` for clarity

### Parameter Structure

For `piecewise_constant`:

```yaml
"[a, b)":
  intercept: <number>
```

For `piecewise_linear`:

```yaml
"[a, b)":
  intercept: <number>  # value at lower bound
  slope: <number>
```

For higher-order polynomials (`piecewise_quadratic`, `piecewise_cubic`):

```yaml
"[a, b)":
  coefficients: [c0, c1, c2, ...]  # polynomial: c0 + c1*x + c2*x^2 + ...
```

### Internal Representation

The `PiecewisePolynomialParamValue` will store intervals using the portion library's
`IntervalDict`:

```python
import portion

# Example: disability allowance
params = portion.IntervalDict(
    {
        portion.closedopen(-portion.inf, 20): {"intercept": 0},
        portion.closedopen(20, 30): {"intercept": 384},
        portion.closedopen(30, 40): {"intercept": 620},
        # ...
        portion.closed(100, portion.inf): {"intercept": 2840},
    }
)

# Query
params[25]  # Returns {"intercept": 384}
```

### Validation

At parameter load time, the system will validate:

1. **Coverage**: Intervals must cover `(-inf, inf)` without gaps
1. **No overlaps**: Intervals must not overlap (portion handles this automatically)
1. **Continuity** (optional, for linear+): At boundaries, the polynomial values should
   match (can be a warning rather than error)

## Related Work

- **[portion](https://pypi.org/project/portion/)**: Python library for interval
  arithmetic, provides the `IntervalDict` data structure
- **[pylcm grid specification](https://github.com/OpenSourceEconomics/pylcm/pull/211)**:
  Uses similar interval notation for `PiecewiseLinSpacedGrid`
- **Mathematical notation**: Standard interval notation from real analysis

## Implementation

1. **Add portion dependency** to ttsim-backend
1. **Create interval parser**: Parse strings like `"[20, 30)"` into portion intervals
1. **Update parameter loading**: Convert YAML to `IntervalDict`-based representation
1. **Update `piecewise_polynomial()`**: Query `IntervalDict` instead of searching arrays
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

### Alternative 3: Use portion Syntax Without the Library

Parse interval strings manually without depending on portion.

Pros: No new dependency Cons: Reinventing the wheel; portion is well-tested and
maintained

## Discussion

- [pylcm #210](https://github.com/OpenSourceEconomics/pylcm/issues/210): Discussion on
  interval specification for grids
- [pylcm #211](https://github.com/OpenSourceEconomics/pylcm/pull/211): Implementation of
  `PiecewiseLinSpacedGrid` using portion

## References and Footnotes

## Copyright

This document has been placed in the public domain.
