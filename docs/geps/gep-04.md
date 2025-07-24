(gep-4)=

# GEP 4 — A DAG—based Computational Backend

```{list-table}
- * Author
  * [Max Blesch](https://github.com/MaxBlesch),
    [Janos Gabler](https://github.com/janosg),
    [Hans-Martin von Gaudecker](https://github.com/hmgaudecker),
    [Tobias Raabe](https://github.com/tobiasraabe),
    [Christian Zimpelmann](https://github.com/ChristianZimpelmann)
- * Status
  * Provisional
- * Type
  * Standards Track
- * Created
  * 2022-03-28
- * Updated
  * 2025-07-23
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2004)
```

## Abstract

This GEP explains the directed acyclic graph (DAG)-based computational backend for
GETTSIM.

The graph operates on columns of data. Stringified function names and their inputs
correspond to columns in the data, i.e., nodes in the graph.

Unless functions perform aggregations, they are written in terms of scalars and
vectorized during DAG setup.

## Motivation

The implementation choice to use a DAG to represent the taxes and transfers system is
motivated by two main reasons.

1. The taxes and transfers system is constantly evolving in many dimensions, flexibility
   is thus needed internally. Additionally, it is not enough to represent the state of
   the system at any given point in time, but users need to be able to introduce their
   own changes. Being able to change or replace any part of the taxes and transfers
   system is crucial. Put differently, there is no meaningful distinction between parts
   of the system only ever touched by developers and parts that are modifiable by users.
   A DAG implementation allows to eliminate this usual boundary for almost all use
   cases.

1) The DAG allows a user to limit computations to generate a set of target variables,
   which she is ultimately interested in. Doing so allows cutting down on the number of
   input variables, it prevents unnecessary calculations, and it increases computation
   speed.

In addition to these requirements, we are using a hierarchical structure of functions to
allow for a clear separation of concerns.

## Basic idea

Based on the two requirements above we split the taxes and transfers system into a set
of small functions. Each function calculates one clearly defined variable (identical to
the function's stringified name) and returns a 1d-array.

```{note}
The function code itself will typically work on scalars and is vectorized by
GETTSIM; this is irrelevant for the DAG.
```

Function arguments can be of three kinds:

- User-provided input variables (e.g.,
  `(einkommensteuer, einkünfte, aus_nichtselbstständiger_arbeit, bruttolohn_m)`).
- Outputs of other functions in the taxes and transfers system (e.g.,
  `(einkommensteuer, betrag_y_sn)`).
- Parameters of the taxes and transfers system (e.g.,
  `(einkommensteuer, abgeltungssteuer, satz)`).

GETTSIM will calculate the variables a researcher is interested in by starting with the
input variables and calling the required functions in a correct order. This is
accomplished via a DAG (see below).

Splitting complex calculations into smaller pieces has a lot of the usual advantages of
why we use functions when programming: readability, simplicity, lower maintenance costs
(single-responsibility principle). Another advantage is that each function is a
potential entry point for a researcher to change the taxes and transfers system if she
is able to replace this function with her own version.

See the following example for capital income taxes (Abgeltungssteuer). Based on the
location in the file system, the full path is
`(einkommensteuer, abgeltungssteuer, betrag_y_sn)`.

```python
@policy_function(start_date="2009-01-01")
def betrag_y_sn(zu_versteuerndes_kapitaleinkommen_y_sn: float, satz: float) -> float:
    """Abgeltungssteuer on Steuernummer level."""
    return satz * zu_versteuerndes_kapitaleinkommen_y_sn
```

The function `(einkommensteuer, abgeltungssteuer, betrag_y_sn)` requires the variable
`zu_versteuerndes_kapitaleinkommen_y_sn`, which is the amount of taxable capital income
on the Steuernummer-level (the latter is implied by the `_sn` suffix, see {ref}`gep-1`).
`zu_versteuerndes_kapitaleinkommen_y_sn` must be provided by the user as a column of the
input data or it has to be the name of another function (in fact, in the GETTSIM code
base it will be calculated as income from capital minus expenses). `satz` is a parameter
coming out of a yaml file in the same directory.

Another function, say `(solidaritätszuschlag, betrag_y_sn)`,

```python
@policy_function(
    start_date="2009-01-01", leaf_name="betrag_y_sn", vectorization_strategy="loop"
)
def betrag_y_sn_mit_abgelt_st(
    einkommensteuer__betrag_mit_kinderfreibetrag_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    einkommensteuer__abgeltungssteuer__betrag_y_sn: float,
    parameter_solidaritätszuschlag: PiecewisePolynomialParameters,
) -> float:
```

may use `(einkommensteuer, abgeltungssteuer, betrag_y_sn)` as an input argument. Note
that because of a different namespace, we need to specify the full path. In order to
make valid Python identifiers out of paths, we use double underscores. Important for
this GEP is that the DAG ensures that the function
`(einkommensteuer, abgeltungssteuer, betrag_y_sn)` will be executed first.

Note that the type annotations (e.g. `float`) indicate the expected type of each input
and the output of a function, see {ref}`gep-2`.

## Directed Acyclic Graph

The relationship between functions and their input variables is a graph where nodes
represent columns in the data (or parameters of the taxes and transfers system, but
these will be partialled into the functions first). These columns must either be present
in the data supplied to GETTSIM or they are computed by functions. Edges are pointing
from input columns to variables, which require them to be computed.

```{note}
GETTSIM allows to visualize the graph, see this [guide](../how_to_guides/visualizing_the_system.ipynb).
```

The resulting structure is a special kind of graph, called a directed acyclic graph
(DAG). It is directed because there are clearly inputs and outputs, i.e., there is a
sense of direction. Acyclic means that there exist no path along the direction of the
edges, where you start at some node and end up at the same node. Equivalently, a DAG has
a topological ordering which is a sequence of nodes ordered from earlier to later in the
sequence. The topological ordering is what defines the sequence in which the functions
in the taxes and transfers system are evaluated. This ensures that the inputs are
already computed before a function that requires them is called.

In order to calculate a set of taxes and transfers, GETTSIM builds a DAG based on three
inputs provided by the user:

> - Input data.
>
> - A set of functions representing the taxes and transfers system, which consist of the
>   ones pre-implemented in GETTSIM and potentially user-written additional functions.
>
>   Parameters of the taxes and transfers system can be ignored in the following (they
>   amount to collections of constants; in practice they will already be partialled into
>   these functions). These functions need to be written for scalars; they will be
>   vectorised during the set up of the DAG.
>
> - The target columns of interest.

The DAG is then used to call all required functions in the right order and to calculate
the requested targets.

### Level of the DAG

In principle, GETTSIM will import all functions defined in the modules describing the
taxes and transfers system. In principle, these functions refer to all years in
GETTSIM's scope. There has to be some discretion in order to allow for the interface of
functions to change over time, new functions to appear, or old ones to disappear.
Because of this, all functions operating on data to be considered by GETTSIM need to be
decorated as `@policy_function`. For simple cases, the decorator does not require any
arguments, e.g., the high-level functions to calculate the total amount of income:

```python
@policy_function()
def gesamteinkommen_y(
    einkünfte__gesamtbetrag_der_einkünfte_y_sn: float,
    abzüge__betrag_y_sn: float,
) -> float:
    """Gesamteinkommen without Kinderfreibetrag on tax unit level."""
```

When functions change, different values can be specified for different time periods. The
`leaf_name` ensures that they can be used without changes elsewhere in the system,
despite different raw names. For example, the calculation of the Solidaritätszuschlag
changed with the introduction of the Abgeltungssteuer:

```python
@policy_function(end_date="2008-12-31", leaf_name="betrag_y_sn")
def betrag_y_sn_ohne_abgelt_st(
    einkommensteuer__betrag_mit_kinderfreibetrag_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    parameter_solidaritätszuschlag: PiecewisePolynomialParameters,
) -> float:
    """Calculate the Solidarity Surcharge on Steuernummer level."""


@policy_function(start_date="2009-01-01", leaf_name="betrag_y_sn")
def betrag_y_sn_mit_abgelt_st(
    einkommensteuer__betrag_mit_kinderfreibetrag_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    einkommensteuer__abgeltungssteuer__betrag_y_sn: float,
    parameter_solidaritätszuschlag: PiecewisePolynomialParameters,
) -> float:
    """Calculate the Solidarity Surcharge on Steuernummer level."""
```

The above construct ensures that both versions can be accessed as
`solidaritätszuschlag__betrag_y_sn` in other parts of the code. If a policy environment
is created for a point in time before 2009, it will be the first version that is used.
If the policy environment is created for a point in time after 2008, the second version
will be used.

## Additional functionalities

We implemented a small set of additional features that simplify the specification of
certain types of functions of the taxes and transfers system.

(gep-4-aggregation-by-group-functions)=

### Group summation and other aggregation functions

Many taxes or transfers require group-level variables. \<GEP-2 describes
`gep-2-aggregation-functions`> how reductions are handled in terms of the underlying
data. This section describes how to specify them.

For example, we may need the number of adult household members. The following code in
`household_characteristics.py` does this:

```python
from ttsim import AggType, agg_by_group_function


@agg_by_group_function(agg_type=AggType.SUM)
def anzahl_erwachsene_hh(familie__erwachsen: bool, hh_id: int) -> int:
    pass
```

That is, we need to specify the aggregation type (sum), the input column
(`familie__erwachsen`), and the group identifier (`hh_id`). GETTSIM will take care of
the rest.

The most common operation are sums of individual measures. GETTSIM adds the following
syntactic sugar: In case an individual-level column `my_col` exists, the graph will be
augmented with a node including a group sum like `my_col_hh` should that be requested.
Requests can be either inputs in a downstream function or explicit targets of the
calculation.

Automatic summation will only happen in case no column `my_col_hh` is explicitly set.
Using a different reduction function than the sum is as easy as explicitly specifying
`my_col_hh`.

Consider the following example: the function `kindergeld__betrag_m` calculates the
individual-level child benefit payment. `arbeitslosengeld_2__betrag_m_bg` calculates
Arbeitslosengeld 2 on the Bedarfsgemeinschaft (bg) level (as indicated by the suffix).
One necessary input of this function is the sum of all child benefits on the
Bedarfsgemeinschaft level. There is no function or input column
`kindergeld__betrag_m_bg`.

By including `kindergeld__betrag_m_bg` as an argument in the definition of
`arbeitslosengeld_2__betrag_m_bg` as follows:

```python
def arbeitslosengeld_2__betrag_m_bg(kindergeld__betrag_m_bg, other_arguments): ...
```

a node `kindergeld__betrag_m_bg` containing the Bedarfsgemeinschaft-level sum of
`kindergeld__betrag_m` will be automatically added to the graph. Its parents in the
graph will be `kindergeld__betrag_m` and `bg_id`. This is the same as specifying:

```python
from ttsim import AggType, agg_by_group_function


@agg_by_group_function(agg_type=AggType.SUM)
def anzahl_erwachsene_hh(kindergeld__betrag_m: float, bg_id: int) -> float:
    pass
```

(gep-4-aggregation-by-p-id-functions)=

### Aggregation based on person-to-person pointers

For some taxes and transfers, one person may establish a claim for another person. A
parent, for example, has a claim on the basic child allowance (Kindergeld) because their
child is eligible for it. Similarly, parents receive a tax allowance because their child
satisfies the criteria for it. These aggregation operations are based on the `p_id`
column. This section describes how to specify such taxes and transfers.

The implementation is similar to aggregations to the level of groupings: In order to
specify new aggregation functions, scripts with functions of the taxes and transfer
system should define a dictionary `aggregation_specs` at the module level. This
dictionary must specify the aggregated columns as keys and the `AggregateByPIDSpec` data
class as values. The class specifies the `source`, `p_id_to_aggregate_by`, and `agg`. If
`agg` is `count`, `source` is not needed.

The key `source` specifies which column is the source of the aggregation operation. The
key `p_id_to_aggregate_by` specifies the column that indicates to which `p_id` the
values in `source` should be ascribed to. The key `agg` gives the aggregation method.

For example, in the `kindergeld` namespace, we could have:

```python
from ttsim import AggType, agg_by_p_id_function


@agg_by_p_id_function(agg_type=AggType.SUM)
def anzahl_ansprüche(
    grundsätzlich_anspruchsberechtigt: bool, p_id_empfänger: int, p_id: int
) -> int:
    pass
```

This places a target function `kindergeld__anzahl_ansprüche` which gives the amount of
claims that a person has on Kindergeld, based on the
`kindergeld__grundsätzlich_anspruchsberechtigt` function which returns Booleans, which
show whether a child is a reason for a Kindergeld claim. `p_id` and some `p_id_[target]`
are required arguments; they will be processed according to naming conventions.

(gep-4-time-unit-conversion)=

### Conversion between reference periods

Similarly to summations to the group level, GETTSIM will automatically convert values
referring to different reference periods defined in {ref}`gep-1` (years `_y`, quarters
`_q`, months `_m`, weeks `_w`, and days `_d`).

In case a column with annual values `[column]_y` exists, the graph will be augmented
with a node including monthly values like `[column]_m` should that be requested.
Requests can be either inputs in a downstream function or explicit targets of the
calculation. In case the column refers to a different level of aggregation, say
`[column]_hh`, the same applies to `[column]_m_hh`.

Automatic conversion will only happen in case no column `[column]_m` is explicitly set.
Using a different conversion function than the sum is as easy as explicitly specifying
`[column]_m`.

Conversion goes both ways and uses the following formulas:

| time unit | suffix | factor relative to Year |
| --------- | ------ | ----------------------- |
| Year      | `_y`   | 1                       |
| Quarter   | `_q`   | 4                       |
| Month     | `_m`   | 12                      |
| Week      | `_w`   | 365.25 / 7              |
| Day       | `_d`   | 365.25                  |

These values average over leap years. They ensure that conversion is always possible
both ways without changing quantities. In case more complex conversions are needed (for
example to account for irregular days per month, leap years, or the like), explicit
functions for, say, `[column]_w` need to be set.

## Related Work

- The [OpenFisca](https://github.com/openfisca) project uses an internal DAG as well.
- Scheduling computations on data with task graphs is how [Dask](https://docs.dask.org/)
  splits and distributes computations.
- Based on GETTSIM and many other projects, the
  [dags](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2004)
  project combines the core ideas in one spot and has become a dependency of GETTSIM.

## Alternatives

We have not found any alternatives which offer the same amount of flexibility and
computational advantages.

## Discussion

- <https://github.com/iza-institute-of-labor-economics/gettsim/pull/178>
- <https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2004>
- GitHub PR for update (changes because of `GEP-6 <gep-6>`):
  <https://github.com/iza-institute-of-labor-economics/gettsim/pull/855>

## Copyright

This document has been placed in the public domain.
