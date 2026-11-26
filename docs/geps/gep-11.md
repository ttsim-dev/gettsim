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
Bundesgesetzblatt (BGBl) that gave the provision the wording we cite, e.g.:

```
§ 66 Abs. 1 EStG idF Art. 6 G. v. 08.12.2022 BGBl. I S. 2230
```

For policy functions, references are written in a `Reference:` section of the docstring.
For parameters, they are written in the `reference` key of each date entry (see
{ref}`GEP 3 <gep-3>`). TTSIM collects the references, GETTSIM parses them and checks
them in its test suite. Based on this, users can look up the policy functions and
parameters that implement a given provision at a given date.

The GEP standardises the format of references and makes sure that they are present and
well-formed. It does not establish that a reference is correct, i.e., that the cited
provision exists or that the code implements it correctly. This remains the task of
tests and code review.

## Motivation and Scope

So far, the connection between GETTSIM's policy functions and parameters on the one hand
and the law on the other hand has been an implicit one. References are given in
docstrings, in the `description` of parameters, or in `note` keys. They are written as
free text and in varying styles; e.g., the same provision may appear as `§66 (1) EStG`
or as `§ 66 Abs. 1 EStG`. Many policy functions do not cite any law at all, and
malformed references go unnoticed (e.g., `§ 32 Art. 2-4 EStG` instead of
`§ 32 Abs. 2-4 EStG`).

We aim for two things:

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

The requirements of this GEP only apply to the policy functions and parameters in
`gettsim.germany`. Users who write their own policy functions or parameters do not need
to add references.

The following is out of scope:

- Verifying that a policy function implements the cited provision correctly.
- Verifying references against the texts of the law. We are not aware of a source that
  covers historical versions of German federal law in machine-readable form (see
  {ref}`gep-11-alternatives`).
- A list of provisions that are not implemented in GETTSIM. It would require historical
  versions of the law at the level of Absätze and is deferred until such data are
  available.

## Usage and Impact

### Looking up policy functions and parameters by provision

```python
from gettsim import find_node_by_legal_reference

find_node_by_legal_reference("§ 66 EStG", policy_date_str="2025-01-01")
```

The function returns the paths of all policy functions and parameters in the policy
environment at that date whose references match the query, together with the matching
references. A query matches all references to the provision itself and to its parts,
i.e., `§ 66 EStG` matches `§ 66 Abs. 1 Satz 2 EStG`. The `idF` part of a reference is
only taken into account if it is part of the query. A query that consists of an act only
returns everything that cites this act.

Queries do not need to follow the format of this GEP. `§66 Estg`, `§ 66 EStG`,
`§ 66 Absatz 1 EStG`, and `§ 66 (1) EStG` all yield the same result. If a query cannot
be interpreted, the error message lists the closest abbreviations of laws.

The policy date is required because paths only have a meaning within a policy
environment.

The same information is available via the `main` function (see {ref}`GEP 7 <gep-7>`) as
a main target, which maps each path in the policy environment to its references.

### Documentation

The documentation contains a page that lists all paths together with their references
and can be searched by provision. The page is generated when the documentation is built.
Plots of the DAG show the references of each node.

### Impact on users

Users who write their own policy functions or parameters are not affected. The checks
described below only cover the contents of `gettsim.germany`.

## Backward compatibility

The user interface does not change; `find_node_by_legal_reference` and the main target
are additions.

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
§ 66 Abs. 1 EStG idF Art. 6 G. v. 08.12.2022 BGBl. I S. 2230
§ 32a Abs. 1 EStG idF Art. 1 G. v. 30.12.2024 BGBl. 2024 I Nr. 449
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
        - § 66 Abs. 1 EStG idF Art. 6 G. v. 08.12.2022 BGBl. I S. 2230
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
the policy function. Because the `idF` part pins down the version, the reference remains
valid if the paragraph is renumbered later.

If a provision is moved while the policy function remains the same, both references are
listed. The list items do not carry dates; the period during which a policy function is
active is determined by `start_date` and `end_date` only.

```python
@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def anrechnungsfreies_einkommen_m(bruttolohn_m: float) -> float:
    """Freibetrag for income from employment.

    Reference:
        - § 30 SGB II idF Art. 1 G. v. 24.12.2003 BGBl. I S. 2954
        - § 11b Abs. 3 SGB II idF Art. 2 G. v. 24.03.2011 BGBl. I S. 453
    """
```

(The article numbers in this example are for illustration only.)

A policy function matches a query if any of its references matches. Hence, a query for
`§ 30 SGB II` at a date after the renumbering also returns this policy function. Since
the result contains the matching reference including its `idF` part, it is clear which
version of the provision was matched.

Renumberings are not detected automatically. Whoever implements the amending act adds
the new reference.

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
      Identische Werte in § 6 Abs. 1 BKGG, diese sind aber nur für beschränkt
      Steuerpflichtige relevant.
    en: null
  unit: EUR_PER_MONTH
  type: scalar
  2023-01-01:
    value: 250
    reference: § 66 Abs. 1 EStG idF Art. 6 G. v. 08.12.2022 BGBl. I S. 2230
    note: Inflationsausgleichsgesetz
  2025-01-01:
    value: 255
    reference: § 66 Abs. 1 EStG idF Art. 5 G. v. 30.12.2024 BGBl. 2024 I Nr. 449
    note: Steuerfortentwicklungsgesetz
```

Every date entry requires a reference. This includes date entries that mark the end of a
parameter. In this case, the reference typically cites the provision that replaces the
parameter or its calculation method. If there is nothing to cite, the date entry states
the reason:

```yaml
  2011-01-01:
    note: Calculation method changed, see regelbedarfsstufen.
    reference: none (calculation method changed in GETTSIM)
```

The `note` key continues to hold any additional information. The name of an act (e.g.,
"Steuerfortentwicklungsgesetz") belongs there and not in the reference.

### Scope

| Object                                                    | Reference                                 |
| --------------------------------------------------------- | ----------------------------------------- |
| Policy functions                                          | required, or `Reference: none (<reason>)` |
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
- accepts a parser for references that is supplied by the country package;
- provides the main target that maps each path in the policy environment to its parsed
  references; and
- shows references in plots of the DAG.

GETTSIM

- supplies the parser for German references. It consists of a thin wrapper around the
  [bundesrecht](https://pypi.org/project/bundesrecht/) package for the provision, a
  small grammar for the act (bundesrecht does not parse references to the BGBl), and the
  list of accepted laws in `laws.yaml` (bundesrecht accepts, e.g.,
  `§ 32 Art. 2-4 EStG`);
- provides `find_node_by_legal_reference`, which interprets the query and filters the
  output of the main target; and
- checks the requirements of this GEP in its test suite.

(gep-11-enforcement)=

### Enforcement

A test in GETTSIM loads all policy objects in `gettsim.germany` for all dates. The test
fails if

- a policy function has neither a `Reference:` section nor a reason for not having one;
- a date entry of a parameter has neither a reference nor a reason for not having one;
- a reference does not follow the format of this GEP; or
- a reference cites a law that is not listed in `laws.yaml`.

When the test is introduced, all policy objects that fail it are recorded in a baseline
file. The test skips these objects and fails if the baseline file grows. Thus, new code
has to follow this GEP from the start, while existing code can be converted one area at
a time. The baseline file is removed once it is empty.

References are not checked when a policy environment is set up. Users will therefore
never encounter an error caused by a reference.

### What is not checked

- Whether the cited provision exists or existed in the cited version.
- Whether the act in the `idF` part is cited with the correct date, article, and page.
  Only its format is checked.
- Whether the code implements the cited provision.

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
   policy objects, accept a parser from the country package, and add the main target.
1. GETTSIM: Add `laws.yaml`, the parser, and the test including the baseline file.
1. GETTSIM: Convert the `reference` keys in all parameter files.
1. GETTSIM: Add `Reference:` sections to policy functions, one area at a time.
1. GETTSIM: Add `find_node_by_legal_reference`, the generated page with all references,
   and a how-to guide on finding the code for a provision.
1. TTSIM: Show references in plots of the DAG.
1. Update the contributor guide.

Steps 3 to 5 require steps 1 and 2. Step 6 only requires step 1.

(gep-11-alternatives)=

## Alternatives

We considered the following alternatives.

**References as an argument of the decorator** (e.g., `legal_basis="§ 66 Abs. 1 EStG"`).
This would have changed the decorators of TTSIM and separated the reference from the
description of the function in the docstring.

**Citing only the provision.** Such a reference is not stable over time. Resolving it
would require historical versions of the law, using the `start_date` of the policy
function.

**Citing only the act in the BGBl.** This is stable, but does not allow for a lookup by
paragraph.

**Marking references within the text of the docstring.** This makes it hard to
distinguish provisions that a function implements from provisions it only mentions.

**A separate key for the provision in the parameter files**, with the `reference` key
holding only the act. This avoids repeating the provision with every change of the
value, but introduces two keys that have to be kept consistent.

**Dates for references within a policy function** (e.g.,
`since 2011-01-01: § 11b Abs. 3 SGB II …`). This would make the lookup exact for every
date. However, it introduces a second place in which the validity of a policy function
over time is specified, in addition to `start_date` and `end_date`.

**Splitting a policy function whenever a cited provision is moved.** This leads to
duplicate code without any change in the calculation.

**A manually maintained list of amending acts**, which references would point to. In the
absence of an API that lists all publications in the BGBl, we do not see how such a list
could be kept up to date.

**Checking references against the texts of the law.** bundesrecht only covers the
current version of the law and would therefore reject correct references to earlier
versions. As of November 2026, the legal information portal of the federal government
only contains versions that are currently in force (historical versions are announced
for 2028). It does not contain the EStG, SGB IV, SGB V, SGB VI, SGB XI, and AO, nor the
amending acts. We will reconsider this once historical versions are available, together
with a list of provisions that do not have a counterpart in GETTSIM.

**Checking that an act is always cited with the same date and article.** This would
detect some typos in the `idF` part, but we do not think it is worth the additional
complexity.

**Converting all policy objects before introducing the test.** This would require one
very large pull request.

**Raising an error when the policy environment is set up.** Users would be confronted
with problems that only concern developers.

**Requiring references for parameter functions.** Most parameter functions convert or
combine parameters and would need to state a reason for not having a reference.

## Discussion

- Discussion on Zulip: to be added.

## Copyright

This document has been placed in the public domain.
