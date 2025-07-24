# Relevant unit concepts

This document describes the concepts of units and intra-personal relationships that are
present in GETTSIM for the specific taxes and transfers. While some transfers are
calculated on the unit level (e.g. Bürgergeld), others arise from relationships between
individuals (e.g. Kindergeld).

If transfers are calculated on the unit level, the unit is specified under "Aggregation
unit". Under "Pointers", we describe the pointer columns (columns that contain the
`p_id` of another individual) that are used to i) determine endogenous units (like
`arbeitslosengeld_2__bg_id`, `einkommensteuer__sn_id`,...) and/or ii) connect
individuals because their relationship makes them eligible for some transfer (i.e.
parent-child relationships create eligibility for child allowances).

The units are:

| Unit                             | ID                          | Description                                                                                                                                                                     | Endogenous |
| -------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Haushalt                         | hh_id                       | Individuals that live together in one household in the Wohngeld sense (§5 WoGG).                                                                                                | no         |
| wohngeldrechtlicher Teilhaushalt | wohngeld\_\_wthh_id         | The relevant unit for Wohngeld. Encompasses all members of a household for whom the Vorrangprüfung of Wohngeld against ALG2/Kinderzuschlag has the same result ∈ {True, False}. | yes        |
| Familiengemeinschaft             | familie\_\_fg_id            | Maximum of two generations, the relevant base unit for Bürgergeld / Arbeitslosengeld 2, before excluding children who have enough income fend for themselves.                   | yes        |
| Bedarfsgemeinschaft              | arbeitslosengeld_2\_\_bg_id | Familiengemeinschaft except for children who have enough income to fend for themselves. Relevant unit for Bürgergeld / Arbeitslosengeld 2.                                      | yes        |
| Steuernummer                     | einkommensteuer\_\_sn_id    | Spouses filing taxes jointly or individuals.                                                                                                                                    | yes        |
| Ehepartner                       | familie\_\_ehe_id           | Couples that are either married or in a civil union.                                                                                                                            | yes        |
| Einstandsgemeinschaft            | arbeitslosengeld_2\_\_eg_id | A couple whose members are deemed to be responsible for each other.                                                                                                             | yes        |

## Taxes

### Joint taxation

#### Description

- Must be married or in a civil union

#### Aggregation unit

- `einkommensteuer__sn_id` (endogenous)

#### Pointers

- `familie__p_id_ehepartner`

### Kinderfreibeträge

#### Description

- Parents (max 2) and their children
- Don't have to be part of the same household
- Possibly claim on more than one Freibetrag for one child due to
  - no child support payed by other parent
  - other parent not known

#### Pointers

- `einkommensteuer__p_id_kinderfreibetragsempfänger_1` and
  `einkommensteuer__p_id_kinderfreibetragsempfänger_2` (either set by the user or
  calculated endogenously via `familie__p_id_elternteil_1` and
  `familie__p_id_elternteil_2`)

## Kindergeld

#### Description

- Only one parent receives child allowances (specified via `kindergeld__p_id_empfänger`)
- Relevant for alimony payment of the other parent, if separate

#### Pointers

- `kindergeld__p_id_empfänger` (exogenous)

## Kinderzuschlag

#### Description

- Paid out on Bedarfsgemeinschaft level
- Parents outside of Bedarfsgemeinschaft (e.g. not in the same household) are not
  considered (besides of Unterhalts(vorschuss)zahlungen)

#### Aggregation unit

- `arbeitslosengeld_2__bg_id` (endogenous)

#### Pointers

- `arbeitslosengeld_2__p_id_einstandspartner`, `familie__p_id_elternteil_1`,
  `familie__p_id_elternteil_2` (exogenous)

## Elterngeld

#### Description

- Parents and their children
- Number of months parents can claim Elterngeld is capped (both individually and sum
  over parents).

#### Pointers

- `familie__p_id_elternteil_1`, `familie__p_id_elternteil_2` (exogenous)

## Unterhalt / Unterhaltsvorschuss

#### Description

- Parents and their children
- Parents necessarily in different households (different `hh_id`)

#### Pointers

- `kindergeld__p_id_empfänger` (exogenous)

## Pflegeversicherung

#### Description

- Contribution depends on the number of children and their ages (since July 2023)
- Parents and their children
  - Can be in different households
  - No reference to age categories of children

#### Pointers

- `familie__p_id_elternteil_1`, `familie__p_id_elternteil_2` (exogenous)

## Rente

### Grundrente

#### Description

- Couples that are married or in a civil union

#### Aggregation unit

- `familie__ehe_id` (endogenous)

#### Pointers

- `familie__p_id_ehepartner` (exogenous)

### Verwitwetenrente

#### Description

- Couples that were married or in a civil union
- Not implemented yet

#### Aggregation unit

- `familie__ehe_id` (endogenous)

#### Pointers

- `familie__p_id_ehepartner` (exogenous)

## Bürgergeld und Sozialhilfe

### SGB II (Bürgergeld)

#### Description

- Bedarfsgemeinschaft comprised of:
  - Einstandsgemeinschaft (SGB II - max 2 adults, marriage-like relationships)
  - Children under 18/25 whose income does not exceed their own needs. - The
    "Kinderwohngeld" allows children to leave the Bedarfsgemeinschaft if Wohngeld (and
    other sourced of income) is sufficient to cover their needs. Not implemented yet.
- Note: A household may exist of several Bedarfsgemeinschaften
  - e.g. parents and adult children aged above 18/25
  - Income/wealth of related members of the household may be considered
    (Einstandsvermutung)

#### Aggregation unit

- `arbeitslosengeld_2__bg_id` (endogenous)

#### Pointers

- `arbeitslosengeld_2__p_id_einstandspartner`, `familie__p_id_elternteil_1`,
  `familie__p_id_elternteil_2` (exogenous)

### SGB XII (Hilfe zum Lebensunterhalt)

#### Description

Government expenditures: 1.5 Mrd €

- Entitled to benefits: Einstandsgemeinschaft (SGB XII) - §27 SGB XII
  - max 2 adults, marriage-like relationships
  - Their children under 18 living in the same household whose income does not exceed
    their own needs
- For income and wealth checks (§39 SGB XII):
  - Haushaltsgemeinschaft
  - Children with income above some threshold

Regarding the household definition:

> wenn Personen, die zusammen wohnen, auch gemeinsam wirtschaften. Der Begriff der
> Haushaltsgemeinschaft wird gegenüber der Wohngemeinschaft gerade dadurch
> gekennzeichnet, dass ihre Mitglieder nicht nur vorübergehend in einer Wohnung
> zusammenleben, sondern einen gemeinsamen Haushalt in der Weise führen, dass sie „aus
> einem Topf“ wirtschaften. Das gemeinsame Wirtschaften geht über die gemeinsame Nutzung
> von Bad, Küche und ggf. Gemeinschaftsräumen sowie über einen gemeinsam organisierten
> Einkauf über eine Gemeinschaftskasse, wie dies regelmäßig in Wohngemeinschaften
> organisiert ist, hinaus.
> https://www.berlin.de/sen/soziales/service/berliner-sozialrecht/kategorie/rundschreiben/2014_04-572017.php

#### Aggregation unit

- Not implemented yet. The current `arbeitslosengeld_2__eg_id` is not sufficient as it
  doesn't include children (it follows the SGB II definition).
- Potentially, `arbeitslosengeld_2__bg_id` could be used as the aggregation unit.

#### Pointers

- `hh_id`, `arbeitslosengeld_2__p_id_einstandspartner`, `familie__p_id_elternteil_1`,
  `familie__p_id_elternteil_2` (exogenous)

### SGB XII (Grundsicherung im Alter / bei Erwerbsminderung)

#### Description

Government expenditures: 7 Mrd €

- Entitled to benefits: Einstandsgemeinschaft (SGB XII) - §27 SGB XII
  - max 2 adults, marriage-like relationships
  - Their children under 18 living in the same household whose income does not exceed
    their own needs
- For income and wealth checks (§39 SGB XII):
  - Haushaltsgemeinschaft
  - Children with income above some threshold

#### Aggregation unit

- Currently: `arbeitslosengeld_2__eg_id` (endogenous)
- The current implementation of `arbeitslosengeld_2__eg_id` is not sufficient as it
  doesn't include children (it follows the SGB II definition).
- Potentially, `arbeitslosengeld_2__bg_id` could be used as the aggregation unit.

#### Pointers

- `arbeitslosengeld_2__p_id_einstandspartner`, `familie__p_id_elternteil_1`,
  `familie__p_id_elternteil_2` (exogenous)

### SGB XII (Eingliederungshilfe für Menschen mit Behinderung)

#### Description

Government expenditures: 20 Mrd €

- Not implemented.

### SGB XII (Hilfe zur Pflege)

#### Description

Government expenditures: 4 Mrd €

- Not implemented.

### Interactions between SGB II / SGB XII

- Partnerships where one partner falls under SGB II and one under SGB XII -> Whole
  household falls under SGB II
- Bedarfsgemeinschaft with child under 25 falling under SGB II -> ?

## Wohngeld

#### Description

- Household (§5 WoGG)
  - Applicant
  - Spouse / registered partner / life partner (as long as in same household)
  - Parents (incl. step-, foster- and in-laws) (as long as in same household)
  - Children (incl. step-, foster- and adopted children) (as long as in same household)
  - "Einstandspartner": non-relatives living in the same household and sharing
    responsibility for each other (e.g. couples that are not married or in a civil
    union) (as long as in same household)
    - A community of responsibility or joint liability is regulated in § 7 Abs. 3a SGB
      II according to which at least one of the following conditions must be met
      - if partners live together for longer than 1 year
      - if partners live together with a child
      - if children or relatives are cared for or looked after in the household (not
        only occasionally)
      - if partners are mutually authorized to dispose of income and assets
    - The prerequisite for all household members is that they live with the applicant
      live in a shared apartment or house and are also registered there.
  - Other relatives
- wohngeldrechtlicher Teilhaushalt: Level at which the transfer is paid out. A household
  consists of at most one wohngeldrechtlicher Teilhaushalt with positive Wohngeld
  transfer and may consist of several additional Bedarfsgemeinschaften.
  - Wohngeld has priority over SGB II transfers. The Vorrangprüfung decides which
    Bedarfsgemeinschaft gets Wohngeld and which gets SGB II.
  - If no or all household members receive Bürgergeld instead of an SGB II transfer, the
    wohngeldrechtlicher Teilhaushalt equals the Haushalt, i.e.
    `wohngeld__wthh_id = hh_id`.
  - Households that consist of at least one Bedarfsgemeinschaft and one
    wohngeldrechtlicher Teilhaushalt are called "Mischhaushalte".

#### Aggregation unit

- `wohngeld__wthh_id` (endogenous)

#### Pointers

- `hh_id`, `arbeitslosengeld_2__p_id_einstandspartner`, `familie__p_id_elternteil_1`,
  `familie__p_id_elternteil_2` (exogenous)

### Kinderwohngeld

#### Description

- Children that are part of the Bedarfsgemeinschaft of their parents can receive
  Wohngeld to drop out of the Bedarfsgemeinschaft ("Kinderwohngeld")
- Only possible if the child can cover its needs with the Wohngeld transfer
- Does not happen automatically, but upon request by the parents
- Not implemented yet.

## Limitations

- Within a Wohngeldhaushalt, no distinction can be made between persons without
  Einstandsverpflichtung according to SGB II or SGB XII and those with
  Einstandsverpflichtung

- Can only show the two extreme cases

  1. all non-vertical or partner relationships not a candidate for Haushaltsgemeinschaft
     according to SGB II / SGB XII
  1. all non-vertical or partner relationships are candidates for Haushaltsgemeinschaft
     according to SGB II / SGB XII

  Typically, 1. will be the solution (hurdles for joint economic activity are high).

- An alternative would be another ID variable that specifies Einstandsgemeinschaft
  according to SGB II and SGB XII.

### Parts of the data not available

- Adult children exist, but not in the dataset
- Spouse that should pay child support is not in the dataset

Solution:

Add support for missing IDs in the data. Missing IDs are represented by negative IDs
(exact value doesn't matter for now).
