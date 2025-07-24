(gep-3)=

# GEP 3 — Parameters of the taxes and transfers system

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
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2003)
```

## Abstract

This GEP describes the structure of the parameters of the taxes and transfers system.
This includes the format of the yaml files (initial input) and storage of the processed
parameters.

## Motivation and Scope

The parameters of the taxes and transfers system are among the core elements of GETTSIM.
Along with the functions operating on them and the input data, they determine all
quantities of interest. Sensibly structuring and cleanly documenting the meaning and
sources of these parameters requires particular care.

## Usage and Impact

GETTSIM developers should closely look at the Section {ref}`gep-3-structure-yaml-files`
before adding new parameters. Some validation happens via the pre-commit hooks, but that
cannot catch all inconsistencies.

(gep-3-structure-yaml-files)=

## Structure of the YAML files

Each YAML file contains a number of parameters at the outermost level of indentation.
Each of these parameters is a dictionary with at least 6 keys: `name`, `description`,
`unit`, `reference_period`, `type` and the `YYYY-MM-DD`-formatted date on which it first
took effect.

Values usually change over time; each time a value is changed, another `YYYY-MM-DD`
entry is added. Beyond that, no additional keys are allowed.

1. The `name` key has two sub-keys `de` and `en`, which are

   - short names without re-stating the realm of the parameter (e.g. "Arbeitslosengeld
     II" or "Kinderzuschlag");
   - not sentences;
   - correctly capitalised.

   Example (from `kindergeld`):

   ```yaml
   altersgrenze:
     name:
       de: Alter, ab dem Kindergeld nicht mehr gezahlt wird.
       en: Age at which child benefit is no longer paid.
   ```

1. The `description` key has two sub-keys `de` and `en`, which

   - are exhaustive explanations of the parameter;

   - show the § and Gesetzbuch of that parameter (including its entire history if the
     location has changed);

   - mention bigger amendments / Neufassungen and be as helpful as possible to make
     sense of that parameter.

     Example:

     ```yaml
     altersgrenze:
       description:
         de: >-
           § 32 Art. 2-4 EStG.
           Für minderjährige Kinder besteht ohne Bedingungen ein Anspruch auf Kindergeld.
           Auch für erwachsene Kinder kann bis zu einer Altersgrenze unter bestimmten
           Bedingungen ein Anspruch auf Kindergeld bestehen.
         en: >-
           § 32 Art. 2-4 EStG.
           Underage children are entitled to child benefit without any conditions. Also adult
           children up to a specified age are entitled to child benefit under certain
           conditions.
     ```

1. The `unit` key informs on the unit of the values (Euro or DM if monetary, share of
   some other value, ...).

   - In some cases (e.g., factor for the calculation of the marginal employment
     threshold), there is no unit.

   - It should be capitalised.

   - Possible values:

     - `Euros`,
     - `DM`,
     - `Share`,
     - `Percent`,
     - `Years`,
     - `Months`,
     - `Hours`,
     - `Square Meters`,
     - `Euros / Square Meter`,
     - *None*.

   Example:

   ```yaml
   altersgrenze:
     name:
       de: Alter, ab dem Kindergeld nicht mehr gezahlt wird.
     unit: Euro
   ```

1. The `type` key signals to GETTSIM how the parameter is to be interpreted. It must be
   specified as one of:

   - `scalar`,
   - `dict`,
   - `piecewise_constant`,
   - `piecewise_linear`,
   - `piecewise_quadratic`,
   - `piecewise_cubic`,
   - `birth_month_based_phase_inout`
   - `birth_year_based_phase_inout`,
   - `require_converter`,

   `scalar` is self-explanatory; `dict` must be a homogeneous dictionary with string or
   integer keys and scalar values (int, float, bool).

   `piecewise_constant`, `piecewise_linear`, `piecewise_quadratic`, `piecewise_cubic`
   will be converted automatically to be used with the `piecewise_polynomial` function.

   `birth_month_based_phase_inout` and `birth_year_based_phase_inout` are used to phase
   in or out a parameter based on the birth year of the individual. They are
   automatically converted to be used as `ConsecutiveIntLookupTableParamValue` objects.

   `require_converter` can be anything. However there must be a converter function in
   the codebase.

1. The `reference_period` key informs on the reference period of the values, if
   applicable. Possible values:

   - `Year`,
   - `Quarter`,
   - `Month`,
   - `Week`,
   - `Day`,
   - `Hour`,
   - *None*

1. The optional `add_jahresanfang` can be used to make the parameter that is relevant at
   the start of the year (relative to the date for which the policy environment is set
   up) available to GETTSIM functions.

   If specified, two parameters will be available:

   ```
   ("path", "to", "parameter")
   ("path", "to", "parameter_jahresanfang")
   ```

   Example from `sozialversicherung` / `arbeitslosen` / `beitragssatz.yaml`:

   ```yaml
   beitragssatz:
     name:
       de: Beitragssatz zur Arbeitslosenversicherung
     unit: Share
     reference_period: null
     type: scalar
     add_jahresanfang: true
   ```

1. The YYYY-MM-DD key(s)

   - hold all historical values for a specific parameter or set of parameters in
     dictionaries
   - contain a precise reference to the law in the `reference` subkey;
   - may add additional descriptions in the `note` key;
   - is present with a note or reference only if a parameter ceases to exist starting on
     a particular date;
   - in case of a `scalar` type, the key of the scalar is `value`.

   The remainder of this section explains this element in much more detail.

### The `reference` key of [YYYY-MM-DD]

- cites the law (Gesetz "G. v."), decree (Verordnung "V. v.") or proclamation
  (Bekanntmachung "B. v.") that changes the law
- uses German language
- follows the style
  - `Artikel [n] [G./V./B.] v. [DD.MM.YYYY] BGBl. I S. [SSSS].` for references published
    until 2022 (the page should be the first page of the law/decree/proclamation, not
    the exact page of the parameter)
  - `Artikel [n] [G./V./B.] v. [DD.MM.YYYY] BGBl. [YYYY] I Nr. [NNN].` for references
    from 2023 on
- does not add information "geändert durch" (it is always a change) or the date the law
  comes into force (this would just repeat the date key one level above)

Example:

```yaml
beitragssatz:
  name:
    de: Beitragssatz zur Arbeitslosenversicherung
  2019-01-01:
    value: 0.0125
    reference: V. v. 21.12.2018 BGBl. I S. 2663
```

### The `note` key of [YYYY-MM-DD]

This optional key may contain a free-form note holding any information that may be
relevant for the interpretation of the parameter, the implementer, user, ...

```yaml
beitragssatz:
  name:
    de: Beitragssatz zur Arbeitslosenversicherung
  2019-01-01:
    value: 0.0125
    reference: V. v. 21.12.2018 BGBl. I S. 2663
    note: >-
      Set to 0.013 in Art. 2 Nr. 15 G. v. 18.12.2018 BGBl. I S. 2651. Temporarily
      reduced to 0.0125 in BeiSaV 2019.
```

### The `updates_previous` key of [YYYY-MM-DD]

Often laws change only part of a parameter. To avoid error-prone code duplication, we
allow for such cases via `updates_previous` key.

This must not be used with a scalar parameter type. Furthermore, it cannot be used in
the first period a parameter is defined.

Example from `sozialversicherung` / `minijob.yaml`:

```yaml
minijobgrenze_ost_west_unterschied
  name:
    de: Minijobgrenze
  unit: Euros
  reference_period: Month
  type: dict
  1997-01-01:
    west: 312
    ost: 266
  1998-01-01:
    updates_previous: true
    west: 317
```

### The values of [YYYY-MM-DD]

The general idea is to make the replication of the laws very obvious. If the law
includes a table, we will have a dictionary with keys 0, 1, 2, .... If the law includes
a formula, the formula should be included and its parameters referenced. Etc..

The following walks through several cases.

- The simplest case is a single parameter, which should be specified as:

  ```yaml
  minijobgrenze:
    name:
      de: Minijobgrenze
      en: Thresholds for marginal employment (minijobs)
    description:
      de: Minijob § 8 (1) Nr. 1 SGB IV
      en: Minijob § 8 (1) Nr. 1 SGB IV
    unit: Euros
    reference_period: Month
    type: scalar
    1984-01-01:
      value: 199
    1985-01-01:
      value: 205
    1986-01-01:
      value: 210
    1987-01-01:
      value: 220
    1988-01-01:
      value: 225
    1989-01-01:
      value: 230
    1990-01-01:
      note: >-
        Minijobgrenze differs between West and East Germany. See
        ``parameter_minijobgrenze_ost_west_unterschied``.
    2000-01-01:
      value: 322
    2002-01-01:
      value: 325
    2003-04-01:
      value: 400
    2013-01-01:
      value: 450
    2022-10-01:
      note: Minijob thresholds now calculated based on statutory minimum wage
      reference: Art. 7 G. v. 28.06.2022 BGBl. I S. 969
  ```

  Note that there are different "active periods" for this parameter. The first one lasts
  from 1984-01-01 to 1989-12-31, after which there were different values in East and
  West Germany. from 2000-01-01 until 2022-10-01, the parameter is active again. After
  that, it is superseded by a formula based on the statutory minimum wage.

- There could be a dictionary, which has to be homogenous in the keys (integers or
  strings) and values (scalar floating point numbers, integers, or Booleans):

  ```yaml
  minijobgrenze_ost_west_unterschied:
    name:
      de: Minijobgrenze, unterschiedlich in Ost und West
      en: Thresholds for marginal employment (minijobs), different in East and West
    description:
      de: Minijob § 8 (1) Nr. 1 SGB IV
      en: Minijob § 8 (1) Nr. 1 SGB IV
    unit: Euros
    reference_period: Month
    type: dict
    1990-01-01:
      west: 240
      ost: 102
    1991-01-01:
      west: 245
      ost: 120
    1992-01-01:
      west: 256
      ost: 153
    1993-01-01:
      west: 271
      ost: 199
    1994-01-01:
      west: 286
      ost: 225
    1995-01-01:
      west: 297
      ost: 240
    1996-01-01:
      west: 302
      ost: 256
    1997-01-01:
      west: 312
      ost: 266
    1998-01-01:
      updates_previous: true
      west: 317
    1999-01-01:
      west: 322
      ost: 271
    2000-01-01:
      note: >-
        Minijob thresholds do not differ between West and East Germany. See
        `minijobgrenze_m`.
  ```

- In some cases, a dictionary with numbered keys makes sense. It is important to use
  these, not lists! The reason is that we always allow for the `note` and `reference`
  keys to be present.

  ```yaml
  satz_gestaffelt:
    name:
      de: Kindergeld pro Kind, Betrag je nach Reihenfolge der Kinder.
      en: Child benefit amount, depending on succession of children.
    description:
      de: >-
        § 66 (1) EStG. Identische Werte in §6 (1) BKGG, diese sind aber nur für beschränkt
        Steuerpflichtige relevant (d.h. Ausländer mit Erwerbstätigkeit in Deutschland).
        Für Werte vor 2002, siehe 'BMF - Datensammlung zur Steuerpolitik'
      en: null
    unit: Euros
    reference_period: Month
    type: dict
    2002-01-01:
      1: 154
      2: 154
      3: 154
      4: 179
    2009-01-01:
      reference: Art. 1 G. v. 22.12.2008 BGBl. I S. 2955
      1: 164
      2: 164
      3: 170
      4: 195
  ```

- Another example would be referring to the parameters of a piecewise linear function:

  ```yaml
  parameter_solidaritätszuschlag:
    name:
      de: Solidaritätszuschlag
      en: null
    description:
      de: >-
        Ab 1995, der upper threshold im Intervall 1 ist nach der Formel
        transition_threshold in soli_st.py berechnet.
      en: null
    unit: Euros
    reference_period: Year
    type: piecewise_linear
    1991-01-01:
      reference: Artikel 1 G. v. 24.06.1991 BGBl. I S. 1318.
      0:
        lower_threshold: -inf
        rate_linear: 0
        intercept_at_lower_threshold: 0
        upper_threshold: 0
      1:
        lower_threshold: 0
        rate_linear: 0.0375
        upper_threshold: inf
  ```

- Phase-in or phase-out of age thresholds based on the birth year of the individual
  (e.g. increasing statutory retirement age thresholds) should be specified as type
  `birth_year_based_phase_inout`. The parameter specification is converted to a lookup
  table that maps a birth year to the age threshold. The conversion requires the
  following stucture after the `YYYY-MM-DD` key:

  - `first_birthyear_to_consider`: The birth year at which the lookup table starts (just
    choose some birthyear that is far enough in the past).
  - `last_birthyear_to_consider`: The birth year at which the lookup table ends (just
    choose some birthyear that is far enough in the future).
  - `YYYY` entries with the following structure:
    - `years`: The age threshold in years.
    - `months`: The age threshold in months.

  Example from `sozialversicherung` / `rente` / `altersrente` / `regelaltersrente` /
  `altersgrenze.yaml`:

  ```yaml
  altersgrenze_gestaffelt:
  name:
    de: Gestaffeltes Eintrittsalter für Regelaltersrente nach Geburtsjahr
    en: Staggered normal retirement age (NRA) for Regelaltersrente by birth year
  description:
    de: >-
      § 35 Satz 2 SGB VI
      Regelaltersgrenze ab der Renteneintritt möglich ist. Wenn früher oder später in
      Rente gegangen wird, wird der Zugangsfaktor und damit der Rentenanspruch höher
      oder niedriger, sofern keine Sonderregelungen gelten.
    en: >-
      § 35 Satz 2 SGB VI
      Normal retirement age from which pension can be received. If retirement benefits
      are claimed earlier or later, the Zugangsfaktor and thus the pension entitlement
      is higher or lower unless special regulations apply.
  unit: Years
  reference_period: null
  type: birth_year_based_phase_inout
  2007-04-20:
    reference: RV-Altersgrenzenanpassungsgesetz 20.04.2007. BGBl. I S. 554
    note: >-
      Increase of the early retirement age from 65 to 67 for birth cohort 1947-1964.
      Vertrauensschutz (Art. 56) applies for birth cohorts before 1955 who were in
      Altersteilzeit before January 1st, 2007 or received "Anpassungsgeld für
      entlassene Arbeitnehmer des Bergbaus".
    first_birthyear_to_consider: 1900
    last_birthyear_to_consider: 2031
    1946:
      years: 65
      months: 0
    1947:
      years: 65
      months: 1
    1948:
      years: 65
      months: 2
    1949:
      years: 65
      months: 3
    1950:
      years: 65
      months: 4
    1951:
      years: 65
      months: 5
    1952:
      years: 65
      months: 6
    1953:
      years: 65
      months: 7
    1954:
      years: 65
      months: 8
    1955:
      years: 65
      months: 9
    1956:
      years: 65
      months: 10
    1957:
      years: 65
      months: 11
    1958:
      years: 66
      months: 0
    1959:
      years: 66
      months: 2
    1960:
      years: 66
      months: 4
    1961:
      years: 66
      months: 6
    1962:
      years: 66
      months: 8
    1963:
      years: 66
      months: 10
    1964:
      years: 67
      months: 0
  ```

- Phase-in or phase-out of age thresholds based on the birth month of the individual
  should be specified as type `birth_month_based_phase_inout`. The parameter
  specification is the same as for `birth_year_based_phase_inout`, except that the
  `YYYY` entries are followed by `MM` keys. The `MM` keys a have the following
  structure:

  - `first_birthmonth_to_consider`: The birth month at which the lookup table starts
    (just choose some birthmonth that is far enough in the past).
  - `last_birthmonth_to_consider`: The birth month at which the lookup table ends (just
    choose some birthmonth that is far enough in the future).
  - `years`: The age threshold in years.
  - `months`: The age threshold in months.

  Excerpt from `sozialversicherung` / `rente` / `altersrente` / `langjährig` /
  `altersgrenze.yaml`:

  ```yaml
  ...
    1989-12-18:
    reference: Rentenreformgesetz 1992. BGBl. I S. 2261 1989 § 41
    note: Increase of full retirement age from 63 to 65 for birth cohort 1938-1943.
    first_birthyear_to_consider: 1900
    last_birthyear_to_consider: 2100
    1937:
      12:
        years: 63
        months: 0
    1938:
      1:
        years: 63
        months: 1
    ...
  ```

- Finally, there are parameters that have a more complex structure, which is not as
  common as `piecewise_linear` etc. These need to be specified as `require_converter`.

  Example from `arbeitslosengeld_2` / `bedarfe.yaml`:

  ```yaml
  parameter_regelsatz_nach_regelbedarfsstufen:
    name:
      de: Regelsatz mit direkter Angabe für Regelbedarfsstufen
      en: Standard rate with direct specification of "Regelbedarfsstufen"
    description:
      de: >-
        § 20 V SGB II.  Neufassung SGB II § 20 (1a) und (2) durch
        Artikel 6 G. v. 22.12.2016 BGBl. I S. 3159.
        Regelbedafstufen:
        1: Alleinstehender Erwachsener
        2: Erwachsene in Partnerschaft
        3: Erwachsene unter 25 im Haushalt der Eltern
        4: Jugendliche
        5: Ältere Kinder
        6: Jüngste Kinder
      en: >-
        Regelbedarfsstufen:
        1: Single Adult
        2: Adults in a partner relationship
        3: Adults under 25 in the household of their parents
        4: Adolescents
        5: Older children
        6: Youngest children
    unit: Euros
    reference_period: Month
    type: require_converter
    2011-01-01:
      1: 364
      2: 328
      3: 291
      4:
        min_alter: 14
        max_alter: 17
        betrag: 287
      5:
        min_alter: 6
        max_alter: 13
        betrag: 251
      6:
        min_alter: 0
        max_alter: 5
        betrag: 215
      reference: Artikel 1 G. v. 24.03.2011 BGBl. I S. 453.
  ```

- In general, a parameter should appear for the first time that it is mentioned in a
  law, becomes relevant, etc..

  Do not set parameters to some value if they are not relevant yet.

- If a parameter ceases to be relevant, is superseded by something else, etc., there
  must be a `YYYY-MM-DD` key with a `note` and/or `reference` key. There must not be
  other entries except for these two.

  Example:

  ```yaml
  parameter_regelsatz_anteilsbasiert:
    name:
      de: Berechnungsgrundlagen für den Regelsatz
    2011-01-01:
      note: Calculation method changed, see regelsatz_nach_regelbedarfsstufen.
  ```

(gep-3-handling-of-parameters-in-the-codebase)=

## Handling of parameters in the codebase

The contents of the YAML files are processed and are a pytree-like structure, similar to
the functions. That is, they can be used directly in their namespace (=path to the yaml
file excluding the file name) and accessed by absolute paths otherwise.

In this tree, they are specialised to the relevant policy date. Depending on the type of
the parameter (see the previous section), the following types are possible:

- `scalar` parameters are just floats / ints / Booleans; i.e., simply the `value` key of
  the yaml file.
- `dict` parameters are homogenous dictionaries with all contents of the `YYYY-MM-DD`
  entries except for the `note` and `reference` keys.
- `piecewise_constant` / `piecewise_linear` / `piecewise_quadratic` / `piecewise_cubic`
  parameters are converted to `PiecewisePolynomialParameter` objects.
- `birth_month_based_phase_inout` and `birth_year_based_phase_inout` are converted to
  `ConsecutiveIntLookupTableParamValue` objects.
- `require_converter` must have a `params_function` that converts the `YYYY-MM-DD`
  entries to a clear type.

## Discussion

- <https://github.com/iza-institute-of-labor-economics/gettsim/pull/148>
- <https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2003>
- GitHub PR for update (changes because of `GEP-6 <gep-6>`):
  <https://github.com/iza-institute-of-labor-economics/gettsim/pull/855>

## Copyright

This document has been placed in the public domain.

## Appendix: json-schema for the yaml files

```{literalinclude} ../../src/ttsim/params-schema.json
```
