(gep-1)=

# GEP 1 — Naming Conventions

```{list-table}
- * Author
  * [Maximilian Blömer](https://github.com/mjbloemer),
    [Hans-Martin von Gaudecker](https://github.com/hmgaudecker),
    [Eric Sommer](https://github.com/Eric-Sommer)
- * Status
  * Provisional
- * Type
  * Standards Track
- * Created
  * 2019-11-04
- * Updated
  * 2025-07-23
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2001)
```

## Abstract

This GEP pins down naming conventions for GETTSIM — i.e., general rules for how data
columns, parameters, Python identifiers (functions, variables), etc. should be named. In
a nutshell and without explanations, these conventions are:

1. Names follow standard Python conventions (`lowercase_with_underscores`).

1. The language should generally be English in all coding efforts and documentation.
   German should be used for all institutional features and directly corresponding
   names.

1. The hierarchical naming convention (see {ref}`GEP 6 <gep-6>`) means that
   abbreviations should be used only very sparingly.

   An abbreviation is always followed by an underscore (unless it is the last word).
   Underscores must not be used to separate German words that are pulled together.

1. German identifiers use correct spelling even if it is non-ASCII (this mostly concerns
   the letters ä, ö, ü, ß).

We explain the background for these choices below.

## Motivation and Scope

Naming conventions are important in order to build and maintain GETTSIM as a coherent
library. Since many people with different backgrounds and tastes work on it, it is
particularly important to clearly document our rules for naming things.

There are three basic building blocks of the code:

1. The input and output data, including any values stored intermediately.
1. The parameters of the tax transfer system, as detailed in the YAML files.
1. Python identifiers, that is, variables and functions.

The general rules and considerations apply in the same way to similar concepts, e.g.,
groups of parameters of filenames.

## General considerations

Even though the working language of GETTSIM is English, all of 1. (column names) and 2.
(parameters of the taxes and transfers system) should be specified in German. Any
translation of detailed rules---e.g., distinguishing between Arbeitslosengeld 2 and
Sozialhilfe; or between Erziehungsgeld, Elterngeld, and Elterngeld Plus---is likely to
lead to more confusion than clarity. The main issue here is that often economic concepts
behind the different programmes are the same (in the examples, social assistance and
parental leave benefits, respectively), but often the names of laws change upon major
policy updates. Non-German speakers would need to look things up, anyhow.

Since Python natively supports UTF-8 characters, we use correct spelling everywhere and
do not make efforts to restrict ourselves to ASCII characters. This choice is made for
readability and uniqueness; e.g., it is not obvious whether an "ö" becomes "oe" or "o"
in English. For column names, we always allow a pure ASCII option, see the next point.

(gep-1-column-names)=

## Column / Policy Function names (a.k.a. "variables" in Stata)

The hierarchical naming convention (see {ref}`GEP 6 <gep-6>`) means that the
highest-level identifier is the type of the programme (e.g., `einkommensteuer` or
`kindergeld`). Very few variables live in the global namespace (e.g., the person
identifier `p_id` or `alter`). A special case is the namespace `familie`, which lives in
the global namespace.

If a column has a reference to a time unit (i.e., any flow variable like earnings or
transfers), a column is indicated by an underscore plus one of {`y`, `q`, `m`, `w`,
`d`}.

The default unit a column refers to is an individual. In case of groupings of
individuals, an underscore plus one of {`sn`, `hh`, `fg`, `bg`, `eg`, `ehe`} will
indicate the level of aggregation.

GETTSIM knows about the following units:

- `p_id`: person identifier
- `hh_id`: Haushalt, individuals living together in a household in the Wohngeld sense
  (§5 WoGG).
- `wohngeld__wthh_id`: Wohngeldrechtlicher Teilhaushalt, i.e. members of a household for
  whom the priority check for Wohngeld/ALG2 yields the same result ∈ {True, False}. This
  unit is based on the priority check via
  `vorrangprüfungen__wohngeld_vorrang_vor_arbeitslosengeld_2_bg` and
  `vorrangprüfungen__wohngeld_und_kinderzuschlag_vorrang_vor_arbeitslosengeld_2_bg`.
- `arbeitslosengeld_2__fg_id`: Familiengemeinschaft. Maximum of two generations, the
  relevant unit for Bürgergeld / Arbeitslosengeld 2. Another way to think about this is
  the potential Bedarfsgemeinschaft before making checks for whether children have
  enough income fend for themselves. Subset of `hh`.
- `arbeitslosengeld_2__bg_id`: Bedarfsgemeinschaft, i.e., Familiengemeinschaft excluding
  children who have enough income to fend for themselves (they will form separate
  `bg`s). Subset of `arbeitslosengeld_2__fg_id`.
- `arbeitslosengeld_2__eg_id`: Einstandsgemeinschaft, a couple whose members are deemed
  to be responsible for each other. This includes couples that live together and may or
  may not be married or in a civil union.
- `familie__ehe_id`: Ehegemeinschaft, i.e. couples that are married or in a civil union.
- `einkommensteuer__sn_id`: Steuernummer (same for spouses filing taxes jointly, not the
  same as the Germany-wide Steuer-ID)

Note that households do not include flat shares etc.. Such broader definition are
currently not relevant in GETTSIM but may be added in the future (e.g., capping rules
for costs of dwelling in SGB II depend on this).

Time unit identifiers always appear before unit identifiers (e.g.,
`arbeitslosengeld_2__betrag_m_bg`).

## Parameters of the taxes and transfers system

The structure of these parameters are laid out in \<GEP-3 `gep-3`>; we just note some
general naming considerations here.

- There is a hierarchical structure to these parameters in that each of them is
  associated with a group (e.g., `arbeitslosengeld`, `kinderzuschlag`). These groups or
  abbreviations thereof do not re-appear in the name of the parameter.
- Parameter names should generally be aligned with relevant column names.

## Other Python identifiers

Python identifiers should generally be in English, unless they refer to a specific law
or set of laws, which is where the same reasoning applies as above.

The length of an identifier name tends to be proportional to its scope. In a list
comprehension or a short loop, `i` might be an acceptable name for the running variable.
A function that is used in many different places should have a descriptive name.

The name of variables should reflect the content or meaning of the variable and not the
type (i.e., float, int, dict, list, df, array ...).

## Alternatives

- We worked with abbreviations before, but this hit limits and it led to never-ending
  discussions (see `GEP-6 <gep-6>` for some history).
- We considered using more English identifiers, but opted against it because of the lack
  of precision and uniqueness (see the example above: How to distinguish between
  Erziehungsgeld, Elterngeld, and Elterngeld Plus in English?).

## A final note

No styleguide in the world can be complete or always be applicable. Python's
[PEP-8](https://www.python.org/dev/peps/pep-0008/) has the wonderful section called
[A Foolish Consistency is the Hobgoblin of Little Minds](https://www.python.org/dev/peps/pep-0008/#a-foolish-consistency-is-the-hobgoblin-of-little-minds)
for that. Quoting from there:

> A style guide is about consistency. Consistency with this style guide is important.
> Consistency within a project is more important. Consistency within one module or
> function is the most important.
>
> However, know when to be inconsistent -- sometimes style guide recommendations just
> aren't applicable. When in doubt, use your best judgment. Look at other examples and
> decide what looks best. And don't hesitate to ask!
>
> In particular: do not break backwards compatibility just to comply with this PEP!
>
> Some other good reasons to ignore a particular guideline:
>
> > 1. When applying the guideline would make the code less readable, even for someone
> >    who is used to reading code that follows this PEP.
> > 1. To be consistent with surrounding code that also breaks it (maybe for historic
> >    reasons) -- although this is also an opportunity to clean up someone else's mess
> >    (in true XP style).
> > 1. Because the code in question predates the introduction of the guideline and there
> >    is no other reason to be modifying that code.
> > 1. When the code needs to remain compatible with older versions of Python that don't
> >    support the feature recommended by the style guide.

## Discussion

The below refers to older versions of the GEP; it has been updated because
`GEP-6 <gep-6>` made much of the original content obsolete.

- GitHub PR: <https://github.com/iza-institute-of-labor-economics/gettsim/pull/60>
- Discussion on provisional acceptance:
  <https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2001/near/189539859>
- GitHub PR for first update (character limits, time and unit identifiers, DAG
  adjustments): <https://github.com/iza-institute-of-labor-economics/gettsim/pull/312>
- GitHub PR for second update (concatenated column names, dealing with conflicting
  objectives, names for columns vs parameters):
  <https://github.com/iza-institute-of-labor-economics/gettsim/pull/342>
- GitHub PR for third update (changes because of `GEP-6 <gep-6>`):
  <https://github.com/iza-institute-of-labor-economics/gettsim/pull/855>

## Copyright

This document has been placed in the public domain.
