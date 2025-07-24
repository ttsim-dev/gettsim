(gep-5)=

# GEP 5 — Optional Rounding of Variables

```{list-table}
- * Author
  * [Janos Gabler](https://github.com/janosg), [Christian Zimpelmann](https://github.com/ChristianZimpelmann)
- * Status
  * Provisional
- * Type
  * Standards Track
- * Created
  * 2022-02-02
- * Updated
  * 2025-07-23
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2005/near/270427530)
```

## Abstract

This GEP describes the implementation of optional rounding of variables in GETTSIM.

## Motivation and Scope

For several taxes and transfers, German law specifies that these be rounded in specific
ways. This leads to different use cases for GETTSIM.

1. Some applications require the exact, rounded, amount as specified in the law. This is
   also helpful for creating test cases.
1. Other applications benefit if functions are mostly smooth and the non-rounding error
   relative to the law does not matter much.

GETTSIM's default will be 1. This document describes how we support both use cases.

(gep-5-rounding-spec-yaml)=

## Implementation

GETTSIM allows for optional rounding of functions' results. Rounding specications are
defined in the `policy_function` decorators. The following goes through the details
using an example from the basic pension allowance (Grundrente).

The law on the public pension insurance specifies that the maximum possible
Grundrentenzuschlag `sozialversicherung__rente__grundrente__höchstbetrag_m` be rounded
to the nearest fourth decimal point (§76g SGB VI: Zuschlag an Entgeltpunkten für
langjährige Versicherung). The example below contains GETTSIM's encoding of this fact.

The snippet is taken from `sozialversicherung/rente/grundrente/grundrente.py`, which
contains the following code:

```python
from ttsim import policy_function, RoundingSpec, RoundingDirection


@policy_function(
    rounding_spec=RoundingSpec(
        base=0.0001,
        direction="nearest",
        reference="§76g SGB VI Abs. 4 Nr. 4",
    ),
    start_date="2021-01-01",
)
def höchstbetrag_m(
    grundrentenzeiten_monate: int,
    berücksichtigte_wartezeit_monate: dict[str, int],
    höchstwert_der_entgeltpunkte: dict[str, float],
) -> float: ...
```

The specification of the rounding parameters is defined via the `RoundingSpec` class.
`RoundingSpec` takes the following inputs:

- The `base` determines the base to which the variables is rounded. It has to be a
  floating point number.
- The `direction` has to be one of `up`, `down`, or `nearest`.
- The `reference` provides the legal reference for the rounding rule. This is optional.
- Additionally, via the `to_add_after_rounding` input, users can specify some amount
  that should be added after the rounding is done (this was relevant for the income tax
  before 2004).

Note that GETTSIM only allows for optional rounding of functions' results. In case one
is tempted to write a function requiring an intermediate variable to be rounded, the
function should be split up so that another function returns the quantity to be rounded.

## Advantages of this implementation

This implementation was chosen over alternatives (e.g., specifying rounding rules in the
parameter files) for the following reason:

- Rounding rules are not a parameter, but a function property that we want to turn off
  and on. Hence, it makes sense to define it at the function level.
- Rounding parameters might change over time. In this case, the rounding parameters for
  each period can be specified using the `start_date`, `end_date` keywords in the
  `policy_function` decorator.
- Optional rounding can be easily specified for user-written functions.
- At the definition of a function, it is clearly visible whether and how it is
  optionally rounded (initially we included the rounding parameters in the yaml files,
  which led to an unclear structure there and one always had to look in two places).

## Discussion

- Zulip: <https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs>
- PR: <https://github.com/iza-institute-of-labor-economics/gettsim/pull/324>
- PR Implementation:
  <https://github.com/iza-institute-of-labor-economics/gettsim/pull/316>
- GitHub PR for update (changes because of `GEP-6 <gep-6>`):
  <https://github.com/iza-institute-of-labor-economics/gettsim/pull/855>
- Github PR changing to a RoundingSpec class rather than parameters specified in the
  yaml files: <https://github.com/iza-institute-of-labor-economics/gettsim/pull/854>

## Copyright

This document has been placed in the public domain.
