(gep-11)=

# GEP 11 — Legal References

```{list-table}
- * Author
  * [Marvin Immesberger](https://github.com/MImmesberger)
- * Status
  * Draft
- * Type
  * Standards Track
- * Created
  * 2026-11-26
- * Resolution
  * One of [Accepted | Rejected |
    Withdrawn](<https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2011>)
    once resolution has been found
```

## Abstract

This GEP makes references to the law a required and machine-readable part of all policy
functions and parameters of the taxes and transfers system that are shipped with
GETTSIM. A reference consists of a provision and the act published in the
Bundesgesetzblatt (BGBl) by which the provision received the cited wording, e.g.:

```
§ 66 Abs. 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230
```

For policy functions, references are written in a `Reference:` section of the docstring.
For parameters, they are written in the `reference` key of each date entry (see
{ref}`GEP 3 <gep-3>`). Based on this, users can look up the policy functions and
parameters that implement a given provision at a given date.

Because public APIs for (historical) versions of German federal law are still
experimental and incomplete, we cannot synchronise federal law and GETTSIM completely.
Checking whether a given reference truly exists or whether certain gaps in GETTSIM's
coverage of the law exist remains up to the users. Tools like the
[legal information portal of the federal government](https://docs.rechtsinformationen.bund.de/)
might help in the future.

## Motivation and Scope

So far, the connection between GETTSIM's policy functions and parameters on the one hand
and the law on the other hand has been an implicit one. References are given in
docstrings, in the `reference` key of parameters, or in `note` keys. They are written as
free text and in varying styles; e.g., the same provision may appear as `§66 (1) EStG`
or as `§ 66 Abs. 1 EStG`. Many policy functions do not cite any law at all, and
malformed references go unnoticed (e.g., `§ 32 Art. 2-4 EStG` instead of
`§ 32 Abs. 2-4 EStG`).

This GEP has two goals.

1. **Reverse lookup.** Researchers and developers should be able to find the parts of
   GETTSIM that implement a provision, e.g., `§ 66 EStG` on 2025-01-01, without
   searching the code base for "Kindergeld". Given the date of a policy environment, a
   reference then serves as a second identifier of a policy function or parameter next
   to its path.

1. **Correct and uniform references.** A single format that is checked automatically
   makes it easier for reviewers to compare code and law and keeps references consistent
   across the code base.

Citing the provision alone is not sufficient for these purposes. Laws are amended
frequently, and paragraphs or Absätze are renumbered in the process. For example,
`§ 30 SGB II` refers to different rules in 2008 and in 2025. The publication in the
BGBl, on the other hand, never changes. We therefore always combine the provision with
the act that gave it its wording ("in der Fassung", abbreviated `idF`). Such a reference
remains valid after later renumberings, and its first part still allows for a lookup by
paragraph.

The requirements of this GEP only apply to the policy functions and parameters GETTSIM
ships with, i.e., those in `gettsim.germany`. Users who write their own policy functions
or parameters do not need to add references.

The following is out of scope:

- Verifying that a policy function implements the cited provision correctly.
- Verifying references against the texts of the law. We are not aware of a source that
  covers historical versions of German federal law in machine-readable form (see
  {ref}`gep-11-alternatives`).
- A list of provisions that are not implemented in GETTSIM. It would require historical
  versions of the law at the level of Absätze and is deferred until such data are
  available.

## Usage and Impact

### Writing references

All policy functions, all date entries of parameters, and all `RoundingSpec`s shipped
with GETTSIM must carry a reference. A reference cites the provision and the act that
gave the provision its wording:

```
§ 66 Abs. 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230
```

The paragraph and the law are required; Absatz, Satz, and lower levels are optional. The
act is cited with its date and its page in the BGBl until 2022 and with its number from
2023 on. Laws are cited by their official abbreviation, e.g., `SGB II`.

In policy functions, references are listed in a `Reference:` section at the end of the
docstring:

```python
def betrag_ohne_staffelung_m(anzahl_ansprüche: int, satz_m: float) -> float:
    """Sum of Kindergeld for eligible children.

    Reference:
        - § 66 Abs. 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230
    """
    return satz_m * anzahl_ansprüche
```

In parameter files, the reference goes into the `reference` key of each date entry:

```yaml
2023-01-01:
  value: 250
  reference: § 66 Abs. 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230
  note: Inflationsausgleichsgesetz
```

In a `RoundingSpec`, it goes into the `reference` argument.

If there is no provision to cite, the reference is replaced by `none (<reason>)`, e.g.,
`Reference: none (technical helper)`. Several references are given as a list. The format
and the remaining rules are specified in {ref}`gep-11-format` and the following
sections; the test suite fails if a reference is missing or malformed (see
{ref}`gep-11-enforcement`).

(gep-11-lookup)=

### Looking up policy functions and parameters by provision

```python
from gettsim import MainTarget, main

main(
    main_target=MainTarget.legal_references.by_query,
    legal_references_query="§ 66 EStG",
    policy_date_str="2025-01-01",
)
```

The main target returns the paths of all policy functions and parameters in the policy
environment at that date whose references match the query, together with the matching
references. A query matches all references to the provision itself and to its parts,
i.e., `§ 66 EStG` matches `§ 66 Abs. 1 Satz 2 EStG`. The `idF` part of a reference is
only taken into account if it is part of the query. A query that consists of an act only
returns everything that cites this act.

`legal_references_query` also accepts a tuple of queries, e.g.,
`("§ 66 EStG", "§ 6 BKGG")`. In this case, the main target maps each query to its
result.

We allow for some flexibility in the query. `§66 Estg`, `§ 66 EStG`,
`§ 66 Absatz 1 EStG`, and `§ 66 (1) EStG` all yield the same result. If a query cannot
be interpreted, the error message lists the closest abbreviations of laws.

The policy date is required because paths only have a meaning within a policy
environment.

A second main target, `MainTarget.legal_references.by_path`, maps each path in the
policy environment to its references. Both main targets are part of the interface DAG
(see {ref}`GEP 7 <gep-7>`); there is no separate function for the lookup.

### Documentation

The documentation contains a page that lists all paths together with their references
and can be searched by provision. The page is generated when the documentation is built.
Plots of the DAG show the references of each node.

## Backward compatibility

The user interface does not change; the main targets and the `legal_references_query`
argument of `main` are additions.

For developers, the style of the `reference` key in the parameter files changes (see
{ref}`gep-11-parameters`). This requires rewriting all existing `reference` entries.
Docstrings of policy functions gain a `Reference:` section. In order to avoid a single
large pull request, existing gaps are recorded in a baseline file (see
{ref}`gep-11-enforcement`).

## Detailed description

(gep-11-format)=

### Format of a reference

A reference consists of a provision and the act that gave the provision its wording:

```
reference = <provision> idF <act>

provision = § <n>[a-z] [Abs. <n>] [Satz <n> | S. <n>] [Nr. <n>] [Buchst. <x>] <law>
act       = [Art. <n> [Nr. <n>]] G.|V.|B. v. DD.MM.YYYY BGBl. I S. <page>      (until 2022)
          | [Art. <n> [Nr. <n>]] G.|V.|B. v. DD.MM.YYYY BGBl. YYYY I Nr. <n>   (from 2023 on)
```

The following rules apply:

- The paragraph (`§`) is required. Absatz, Satz, and lower levels are optional, but
  should be given wherever they add precision. Whether a paragraph has Absätze cannot be
  determined without the text of the law, hence the depth of a reference is not checked.
- Within the provision, both `Satz` and `S.` denote a sentence. Within the act, `S.`
  denotes the page of the BGBl. The position relative to `idF` resolves the ambiguity.
- Articles are abbreviated as `Art.`. For acts that do not consist of articles, `Art.`
  is left out.
- `G.`, `V.`, and `B.` stand for Gesetz, Verordnung, and Bekanntmachung, as in
  {ref}`GEP 3 <gep-3>`.
- For acts published until 2022, the page is the first page of the act, not the page of
  the provision.
- `<law>` is the official abbreviation of the law as used on gesetze-im-internet.de,
  e.g., `EStG` or `SGB II` (not `SGB 2`). The abbreviations we accept are listed in
  `laws.yaml`.

Examples:

```
§ 66 Abs. 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230
§ 32a Abs. 1 EStG idF Art. 1 G. v. 23.12.2024 BGBl. 2024 I Nr. 449
```

### Policy functions

References of policy functions are written in a `Reference:` section at the end of the
docstring. Each reference is an indented list item starting with `-`. The rest of the
docstring is not affected and should still describe what the function does.

```python
@policy_function(
    start_date="2023-01-01", leaf_name="betrag_m", unit=TTSIMUnit.CURRENCY.PER_MONTH
)
def betrag_ohne_staffelung_m(
    anzahl_ansprüche: int,
    satz_m: float,
) -> float:
    """Sum of Kindergeld for eligible children.

    Kindergeld claim is the same for each child, i.e. increases linearly with the number
    of children.

    Reference:
        - § 66 Abs. 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230
    """
    return satz_m * anzahl_ansprüche
```

A policy function cites the provisions it implements. If it implements several
provisions, it lists all of them. Policy functions should not be split up only because
the law distributes a rule over several provisions; as before, the boundaries of
functions are determined by readability.

Some policy functions do not have a counterpart in the law, e.g., some of the functions
in the `familie` namespace. They state this explicitly:

```python
@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
def ist_kind_bis_2_in_familiengemeinschaft(
    alter: int, ist_kind_in_familiengemeinschaft: bool
) -> bool:
    """Child under the age of 3 in Familiengemeinschaft.

    Reference: none (technical helper)
    """
    return ist_kind_in_familiengemeinschaft and (
        alter <= cast_ttsim_unit(2, unit=TTSIMUnit.YEARS)
    )
```

The reason in parentheses is required. There is no way to exclude entire namespaces;
each exception is visible in the policy function it applies to.

### References over time

A reference refers to the version of a provision that is in force at the `start_date` of
the policy function. Because the `idF` part determines the version, the reference
remains valid if the paragraph is renumbered later.

If a provision is moved while the policy function remains the same, both references are
listed. The list items do not carry dates; the period during which a policy function is
active is determined by `start_date` and `end_date` only. In the following example, the
article numbers serve as an illustration only.

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def anrechnungsfreies_einkommen_m(bruttolohn_m: float) -> float:
    """Freibetrag for income from employment.

    Reference:
        - § 30 SGB II idF Art. 1 G. v. 24.12.2003 BGBl. I S. 2954
        - § 11b Abs. 3 SGB II idF Art. 2 G. v. 24.03.2011 BGBl. I S. 453
    """
```

A policy function matches a query if any of its references matches. Hence, a query for
`§ 30 SGB II` at a date after the renumbering also returns this policy function. Since
the result contains the matching reference including its `idF` part, it is clear which
version of the provision was matched.

Renumberings are not detected automatically. Whoever implements the amending act adds
the new reference.

### Rounding rules

The `reference` argument of a `RoundingSpec` (see {ref}`GEP 5 <gep-5>`) follows the same
rules as the references of policy functions. If a policy function has a `rounding_spec`,
its `reference` is required, has to follow the format of this GEP, and may be replaced
by `none (<reason>)`.

```python
RoundingSpec(
    base=0.01,
    direction="down",
    reference="§ 123 Abs. 1 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261",
)
```

(gep-11-parameters)=

### Parameters

For parameters, the `reference` key of each date entry holds a reference in the format
described above. This replaces the style of the `reference` key specified in
{ref}`GEP 3 <gep-3>`.

```yaml
satz_m:
  name:
    de: Kindergeld pro Kind, identisch für alle Kinder.
    en: Child benefit amount, identical for all children.
  description:
    de: >-
      § 66 Abs. 1 EStG. Identische Werte in § 6 Abs. 1 BKGG, diese sind aber nur für
      beschränkt Steuerpflichtige relevant (d.h. Ausländer mit Erwerbstätigkeit in
      Deutschland). Für Werte vor 2002, siehe 'BMF - Datensammlung zur Steuerpolitik'
    en: null
  unit: EUR_PER_MONTH
  type: scalar
  2023-01-01:
    value: 250
    reference: § 66 Abs. 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230
    note: Inflationsausgleichsgesetz
  2025-01-01:
    value: 255
    reference: § 66 Abs. 1 EStG idF Art. 1 G. v. 23.12.2024 BGBl. 2024 I Nr. 449
    note: Steuerfortentwicklungsgesetz (SteFeG)
```

Every date entry requires a reference. This includes date entries that mark the end of a
parameter. In this case, the reference typically cites the provision that replaces the
parameter or its calculation method. If there is nothing to cite, the date entry states
the reason:

```yaml
  2011-01-01:
    note: Calculation method changed, see regelbedarfsstufen.
    reference: none (Regelbedarfe are no longer set as shares of a base amount)
```

If the values of a date entry follow from several provisions, the `reference` key holds
a list of references, as in the `Reference:` section of policy functions.

The `note` key continues to hold any additional information. The name of an act (e.g.,
"Steuerfortentwicklungsgesetz") belongs there and not in the reference.

### Scope

| Object                                                    | Reference                                 |
| --------------------------------------------------------- | ----------------------------------------- |
| Policy functions                                          | required, or `Reference: none (<reason>)` |
| `reference` of a `RoundingSpec`                           | required, or `none (<reason>)`            |
| Date entries of parameters, including the end of a period | required, or `reference: none (<reason>)` |
| Parameter functions                                       | optional                                  |
| Aggregation functions, group creation functions, inputs   | not checked                               |
| Policy functions and parameters written by users          | not checked                               |

### TTSIM and GETTSIM

TTSIM does not contain any country-specific knowledge. Hence, it knows where references
are stored, but not how to interpret them.

TTSIM

- extracts the `Reference:` section from the docstrings of policy functions and the
  `reference` key from the date entries of parameters;
- stores them as an attribute of each policy object, either as a list of strings or as
  the reason why there is no reference;
- accepts a parser for references that is supplied by the country package, in the same
  way as the unit system. The parser turns a reference or a query into a structured
  representation and decides whether a reference matches a query;
- adds the `legal_references_query` argument to `main`, which takes a query or a tuple
  of queries;
- provides the main targets `legal_references.by_path`, which maps each path in the
  policy environment to its parsed references, and `legal_references.by_query`, which
  keeps the paths whose references match the query; and
- shows references in plots of the DAG.

GETTSIM

- supplies the parser for German references. It consists of a thin wrapper around the
  [bundesrecht](https://pypi.org/project/bundesrecht/) package for the provision, a
  small grammar for the act (bundesrecht does not parse references to the BGBl), and the
  list of accepted laws in `laws.yaml` (bundesrecht accepts, e.g.,
  `§ 32 Art. 2-4 EStG`). The parser is lenient for queries (see {ref}`gep-11-lookup`),
  but strict for references in the code;
- passes the parser to TTSIM in `gettsim.main`; and
- checks the requirements of this GEP in its test suite.

(gep-11-enforcement)=

### Enforcement

A test in GETTSIM loads all policy objects in `gettsim.germany` for all dates. The test
fails if

- a policy function has neither a `Reference:` section nor a reason for not having one;
- a date entry of a parameter has neither a reference nor a reason for not having one;
- a `RoundingSpec` has neither a reference nor a reason for not having one;
- a reference does not follow the format of this GEP; or
- a reference cites a law that is not listed in `laws.yaml`.

When the test is introduced, all policy objects that fail it are recorded in a baseline
file. The test skips these objects and fails if the baseline file grows. Thus, new code
has to follow this GEP from the start, while existing code can be converted one area at
a time. The baseline file is removed once it is empty.

The test does not check whether the cited provision exists or existed in the cited
version, whether the act is cited with the correct date, article, and page, or whether
the code implements the provision. References are not checked when a policy environment
is set up, so users are never affected by a missing or malformed reference.

## Related Work

- [OpenFisca](https://openfisca.org/doc/) and
  [PolicyEngine](https://policyengine.github.io/policyengine-core/usage/parameters.html)
  store references to the law as optional metadata of variables and parameters.
- [Catala](https://catala-lang.org/) takes a different approach and writes the code
  alongside the text of the law.
- [bundesrecht](https://pypi.org/project/bundesrecht/) parses references to German
  federal law and resolves them against the current version of the law.
- The
  [legal information portal of the federal government](https://docs.rechtsinformationen.bund.de/)
  provides an open API. Laws are identified by the European Legislation Identifier
  (ELI), which is based on the publication in the BGBl (e.g.,
  `eli/bund/bgbl-1/2008/s1856` for the WoGG). The act part of a reference in this GEP
  corresponds to such an identifier.

## Implementation

1. TTSIM: Extract references from docstrings and parameter files, store them in the
   policy objects, accept a parser from the country package, and add the
   `legal_references_query` argument and the main targets.
1. GETTSIM: Add `laws.yaml`, the parser, and the test including the baseline file.
1. GETTSIM: Convert the `reference` keys in all parameter files and the references of
   all `RoundingSpec`s.
1. GETTSIM: Add `Reference:` sections to policy functions, one area at a time.
1. GETTSIM: Pass the parser to TTSIM in `gettsim.main`, add the generated page with all
   references, and add a how-to guide on finding the code for a provision.
1. TTSIM: Show references in plots of the DAG.
1. Update the contributor guide.

Steps 3 to 5 require steps 1 and 2. Step 6 only requires step 1.

(gep-11-alternatives)=

## Alternatives

Regarding the place of references, we considered an argument of the decorators (e.g.,
`legal_basis="§ 66 Abs. 1 EStG"`). This would have required changing the decorators in
TTSIM and separated the reference from the description of the function. Marking
references anywhere in the text of the docstring would make it hard to distinguish
provisions that a function implements from provisions it merely mentions. For the
parameter files, a separate key for the provision, with the `reference` key holding only
the act, would avoid repeating the provision whenever the value changes. However, two
keys would have to be kept consistent.

Regarding the format, citing only the provision is not stable over time, and resolving
it would require historical versions of the law. Citing only the act in the BGBl is
stable, but does not allow for a lookup by paragraph. A manually maintained list of
amending acts, to which references would point, cannot be kept up to date without an API
that lists all publications in the BGBl.

Regarding renumberings, we considered adding dates to the references of a policy
function (e.g., `since 2011-01-01: § 11b Abs. 3 SGB II …`). This would make the lookup
exact for every date, but it would specify the validity of a policy function in a second
place next to `start_date` and `end_date`. Splitting a policy function whenever a cited
provision moves would lead to duplicate code that does not change any calculation.

Regarding checks, we would like to verify references against the texts of the law.
bundesrecht only covers the current version of the law and would reject correct
references to earlier versions. As of November 2026, the legal information portal of the
federal government only contains versions that are currently in force, with historical
versions announced for 2028. It contains neither the EStG, SGB IV, SGB V, SGB VI, SGB
XI, and AO, nor any amending acts. We will reconsider this question once historical
versions are available, together with a list of provisions that do not have a
counterpart in GETTSIM. A test that the same act is always cited with the same date and
article would catch some typos in the `idF` part, but we do not think it is worth the
additional complexity.

Regarding the introduction, converting all policy objects before introducing the test
would require one very large pull request. Raising an error when the policy environment
is set up would confront users with problems that only concern developers. Requiring
references for parameter functions would mostly lead to exceptions, since most of them
only convert or combine parameters.

For the lookup, we considered a separate function `find_node_by_legal_reference`. It
would have to set up the policy environment itself and accept the same arguments as
`main` for this purpose (e.g., a modified policy environment). As a main target, the
lookup reuses this logic and works on any policy environment that `main` can produce.

## Discussion

- Discussion on Zulip: to be added.

## Copyright

This document has been placed in the public domain.
