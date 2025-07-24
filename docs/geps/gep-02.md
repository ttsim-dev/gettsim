(gep-2)=

# GEP 2 — Internal Representation of Data on Individuals

```{list-table}
- * Author
  * [Hans-Martin von Gaudecker](https://github.com/hmgaudecker)
- * Status
  * Provisional
- * Type
  * Standards Track
- * Created
  * 2022-03-28
- * Updated
  * 2025-07-23
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2002)
```

## Abstract

This GEP lays out how GETTSIM stores user-provided data (be it from the SOEP, EVS,
example individuals, ...) and passes it around to the functions calculating taxes and
transfers.

Data will be stored as a collection of 1-d arrays, each of which corresponds to a column
in the data provided by the user (if it comes in the form of a DataFrame) or calculated
by GETTSIM. All these arrays have the same length. This length corresponds to the number
of individuals. Functions operate on a single row of data.

Arrays are stored in a nested dictionary (a pytree). One level of the dictionary is
called a *namespace*. Its innermost level is called a *leaf name*. The data columns are
called *leaves*.

If a leaf name is `[x]_id` with `id` {math}`\in \{` `hh`, `bg`, `fg`, `ehe`, `eg`, `sn`,
`wthh` {math}`\}`, it will be the same for all households, Bedarfsgemeinschaften, or any
other grouping of individuals specified in {ref}`GEP 1 <gep-1-column-names>`.

Any leaf name `p_id_[y]` indicates a link to a different individual (e.g., child-parent
are specified via `(familie, p_id_elternteil_1)`, `(familie, p_id_elternteil_2)`; the
recipient of child benefits would be `(kindergeld, p_id_empfänger)`).

## Motivation and Scope

Taxes and transfers are calculated at different levels of aggregation: Individuals,
couples, families, households. Sometimes, relations between individuals are important:
parents and children, payors/recipients of alimony payments, which parent receives
Kindergeld payments, etc..

Potentially, there are many ways of storing these data: Long form, wide form,
collections of tables adhering to
[database normal forms](https://en.wikipedia.org/wiki/Database_normalization),
N-dimensional arrays, etc.. As usual, everything involves trade-offs, for example:

- Normal forms require many merge / join operations, which the tools we are using are
  not optimised for.

- One N-dimensional array is not possible because groups are not necessarily nested

- Almost all functions are much easier to implement when working with a single row. This
  is most important for the typical user and increasing the number of developers.

- Modern tools for vectorization (e.g., JAX) scale best when working with single rows of
  data.

  Aggregation to groups of individuals (households, Bedarfsgemeinschaften,...) or
  referencing data from other rows (parents, receiver of child benefits) is not trivial
  with these tools.

## Usage and Impact

This is primarily internal, i.e., only relevant for developers as the highest-level
interface can be easily adjusted. The default way to receive data will be one Pandas
DataFrame.

Users are affected only via the interface of lower-level functions. Functions will
always work on single rows of data. Many alternatives would require users to write
vectorised code, making filtering operations more cumbersome. For aggregation or
referencing other individuals' data, GETTSIM will provide functions that allow
abstracting from implementation details, see {ref}`below <gep-2-aggregation-functions>`.

## Detailed description

The following discussion assumes that data is passed in as a Pandas DataFrame. It will
be possible to pass data directly in the form that GETTSIM requires it internally. In
that case, only the relevant steps apply.

- GETTSIM may make a check that all identifiers pointing to other individuals (e.g.,
  `(kindergeld, p_id_empfänger)`) are valid.

- GETTSIM may make a check that there is no variation within a group of individuals if
  the column name indicates that there must not be (e.g., all members sharing the same
  `hh_id` must have the same `anzahl_personen_hh` in case the variable is provided as an
  input column).

- Because groups of individuals are not necessarily nested (e.g., joint taxation during
  separation phase but living in different households), they cannot be sorted in
  general.

- The core of GETTSIM works with a collection of 1-d arrays, all of which have the same
  length as the number of individuals.

  These arrays form the nodes of its DAG computation engine (see {ref}`GEP 4 <gep-4>`).

- GETTSIM returns an object of the same type and with the same row identifiers that was
  passed by the user.

(gep-2-aggregation-functions)=

### Grouped values and aggregation functions

Often columns refer to groups of individuals. Such columns have a suffix indicating the
group (see {ref}`GEP 1 <gep-1-column-names>`). These columns' values will be repeated
for all individuals who form part of a group.

By default, GETTSIM will check consistency on input columns in this respect. Users will
be able to turn this check off.

Aggregation functions will be provided by GETTSIM.

- Aggregation will always start from the individual level. If aggregation at the, say,
  Bedarfsgemeinschaft-level to the household-level is required (and possible), users
  will first need to provide an appropriate individual-level column (e.g., by dividing
  some Bedarfsgemeinschaft-level aggregate by the number of indviduals within the same
  Bedarfsgemeinschaft)

- As outlined in {ref}`GEP 4 <gep-4-aggregation-by-group-functions>` users will need to
  specify:

  - The name of the aggregated variable. This **must** end with a feasible unit of
    aggregation, e.g., `_hh` or `_ehe`.
  - The type of aggregation {math}`\in \{` `count`, `sum`, `mean`, `max`, `min`, `any`,
    `all`, {math}`\}`
  - The name of the original variable (not relevant for `count`)

  Note that as per {ref}`GEP 4 <gep-4-aggregation-by-group-functions>`, sums will be
  calculated implicitly if the graph contains a column `my_col` and an aggregate such as
  `my_col_hh` is requested somewhere.

## Alternatives

Versions 0.3 -- 0.4 of GETTSIM used a collection of pandas Series. This proved to be
cumbersome because case distinctions had to be made in vectorized code (e.g., picking
different values from the parameter database depending on a child's age).

Adhering to normal forms (e.g., reducing the length of arrays to the number of
households like
\[here\](<https://www.tensorflow.org/api_docs/python/tf/math/segment_sum>) would have
led to many merge-like operations in user functions.

Versions 0.5 -- 0.7 of GETTSIM used flat collections of pandas Series. As the scope and
detail of GETTSIM grew, maintaining uniqueness of column names across different areas of
taxes and transfers became too difficult.

## Discussion

- Some
  [discussion on Zulip](https://gettsim.zulipchat.com/#narrow/stream/224837-High-Level-Architecture/topic/Update.20Data.20Structures/near/180917151)
  re data structures.
- Zulip stream for
  [GEP 2](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2001/near/189539859).
- GitHub PR for update (changes because of `GEP-6 <gep-6>`):
  <https://github.com/iza-institute-of-labor-economics/gettsim/pull/855>

## Copyright

This document has been placed in the public domain.
