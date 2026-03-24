(gemischte-bedarfsgemeinschaften)=

# Gemischte Bedarfsgemeinschaften

In the German tax-transfer system, the unit at which benefits are computed does not
always coincide with the household. Members of the same household can fall under
different benefit systems (SGB II vs. SGB XII, or SGB II vs. Wohngeld). This document
explains three "mixed" scenarios that arise from these interactions.

## Gemischte Bedarfsgemeinschaft (SGB II / SGB XII)

A *gemischte Bedarfsgemeinschaft* arises when members of the same couple fall under
different benefit systems:

- One partner is *erwerbsfähig* and below the *Regelaltersgrenze* → eligible for **SGB
  II** (Bürgergeld)
- The other partner has reached the *Regelaltersgrenze* → eligible for **SGB XII**
  (Grundsicherung im Alter)

The partner past the Regelaltersgrenze remains a *member* of the SGB II
Bedarfsgemeinschaft (§7 Abs. 3 SGB II) but receives no Bürgergeld (§19 Abs. 1 Satz 2 SGB
II; §5 Abs. 2 Satz 2 SGB II). Their needs are covered by SGB XII instead (§43 Abs. 1 SGB
XII).

### Individual entitlements within a Bedarfsgemeinschaft

Bürgergeld is an **individual entitlement**, not a group-level payment. Even within a
normal Bedarfsgemeinschaft, each person has their own individual claim. The
Bedarfsgemeinschaft serves as the *calculation unit* for pooling income and determining
need, but the resulting benefit amount is attributed to individual persons.

In principle, there are two methods for attributing income to individual BG members:

|                           | Horizontal method                                                            | Vertical method                                                           |
| ------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Income attribution**    | Pooled and distributed proportionally to each person's share of total Bedarf | Stays with the earner; only surplus above own Bedarf flows to the partner |
| **Who is hilfebedürftig** | All members, proportionally                                                  | Only members whose own income falls short                                 |
| **Applies to**            | Normal BG (all members SGB II eligible)                                      | Mixed BG (one SGB II, one SGB XII)                                        |
| **Legal basis**           | §9 Abs. 2 Satz 3 SGB II; BSG B 14 AS 55/07 R                                 | BSG B 14 AS 89/20 R                                                       |

### Horizontal method (normal BG)

In a normal BG where all members are SGB II eligible, the *Bedarfsanteilsmethode*
applies (BSG 18.06.2008 — B 14 AS 55/07 R):

1. Compute each person's individual Bedarf (Regelsatz + kopfteilig KdU + Mehrbedarfe).
   In GETTSIM, this is `bürgergeld__regelbedarf_m`.
1. Sum to the total Bedarf of the BG (`bürgergeld__regelbedarf_m_bg`).
1. Pool all countable income (`bürgergeld__anzurechnendes_einkommen_m_bg`).
1. Distribute income proportionally: each person's attributed income equals their share
   of total Bedarf times the total countable income of the BG.
1. Individual benefit: the difference between individual Bedarf and attributed income,
   floored at zero.

The sum of individual benefits equals the BG-level benefit. This equivalence holds
because, when the BG is hilfebedürftig, each person's Bedarf is scaled by the same
factor (one minus the ratio of total income to total Bedarf).

### Vertical method (mixed BG)

When the partner actually receives SGB XII benefits, BSG B 14 AS 89/20 R mandates a
restrictive interpretation of §9 Abs. 2 Satz 3 SGB II. The SGB XII partner's needs and
income are **excluded entirely** from the horizontal income distribution. Each system
computes independently:

- **SGB II** (erwerbsfähige person): own Bedarf minus own countable income
- **SGB XII** (person past Regelaltersgrenze): own Bedarf minus own countable income
  under SGB XII rules

Both systems use **raw income**, not each other's transfer amounts (§11 Abs. 1 SGB II;
§82 Abs. 1 SGB XII), so there is no circular dependency.

The relevant calculation unit for the SGB XII partner is the **Einsatzgemeinschaft**
(`eg_id`, § 27 Abs. 2 SGB XII), which is analogous to the Bedarfsgemeinschaft for SGB
II. In a mixed BG, the SGB XII partner forms their own Einsatzgemeinschaft; their Bedarf
and income are computed at the `_eg` level.

### Additional rules for mixed BGs

- Both partners receive **Regelbedarfsstufe 2** (the partner rate), not RBS 1 (BSG
  16.10.2007 — B 8/9b SO 2/06 R).
- KdU is split per capita (*Kopfteilprinzip*) — the Jobcenter covers the SGB II
  partner's share, the Sozialamt covers the SGB XII partner's share.
- Income protected by SGB II Freibeträge for the erwerbsfähige partner must not be
  counted against the SGB XII partner (BSG 09.06.2011 — B 8 SO 20/09 R; §82 Abs. 3 Satz
  3 SGB XII).

### Example

Anna (age 55, erwerbsfähig) and Bernd (age 67, past Regelaltersgrenze) live together.
Monthly KdU for the household is 600 EUR.

|                                     | Anna (SGB II)                    | Bernd (SGB XII)                      |
| ----------------------------------- | -------------------------------- | ------------------------------------ |
| Regelsatz (RBS 2)                   | 506                              | 506                                  |
| KdU (kopfteilig)                    | 300                              | 300                                  |
| **Bedarf**                          | **806**                          | **806**                              |
| Gross earnings                      | 1000                             | 0                                    |
| Altersrente                         | 0                                | 400                                  |
| Countable income (after deductions) | 600                              | 400                                  |
| **Benefit**                         | 806 − 600 = **206** (Bürgergeld) | 806 − 400 = **406** (Grundsicherung) |

The vertical method means Anna's earnings are not attributed to Bernd, and Bernd's
pension is not attributed to Anna. Each person's shortfall is covered by their
respective system.

For comparison, the **horizontal method** would attribute income proportionally (50/50
because both have the same Bedarf):

|                   | Anna             | Bernd            |
| ----------------- | ---------------- | ---------------- |
| Income attributed | 50% × 1000 = 500 | 50% × 1000 = 500 |
| Benefit           | 806 − 500 = 306  | 806 − 500 = 306  |

The total benefit is the same (612 EUR in both cases), but the attribution to
individuals — and thus to SGB II vs. SGB XII — differs.

## Wohngeldrechtlicher Teilhaushalt and Mischhaushalte

A *Mischhaushalt* is a household where some members receive transfer payments
(Bürgergeld, Grundsicherung) and are therefore excluded from Wohngeld (§7 Abs. 1 WoGG),
while other members are eligible for Wohngeld. The eligible members form the
*wohngeldrechtlicher Teilhaushalt* (see also {ref}`relevant-unit-concepts`).

Each Mischhaushalt contains exactly one wohngeldrechtlicher Teilhaushalt — the subset of
household members who are to be considered for the Wohngeld calculation.

### When does this occur?

A Mischhaushalt arises when the Vorrangprüfung (§12a SGB II) determines that Wohngeld is
more favorable than Bürgergeld for some but not all household members. This typically
happens when a household contains multiple Familiengemeinschaften. For example:

- Parents with an adult child (aged 25+) who forms their own Familiengemeinschaft
- Wohngeld covers the child's needs but not the parents' (because the child has own
  sources of income, for example alimony payments)

### Wohngeld calculation in a Mischhaushalt

In a Mischhaushalt, the Wohngeld calculation uses kopfteilig apportioned rent (§11 Abs.
3 WoGG):

- Only the share of rent corresponding to the ratio of eligible members to total
  household members is considered
- The Höchstbetrag (maximum rent, §12 Abs. 1 WoGG) is determined based on total
  household size but then apportioned by the same ratio

**Example**: A 4-person household (2 parents, 2 adult children) with rent of 600 EUR.
The parents receive Bürgergeld, the two adult children receive Wohngeld.

- Total household size: 4 → determines the Höchstbetrag tier
- Eligible members: 2 out of 4
- Wohngeld-eligible rent: 600 × 2/4 = 300 EUR
- Höchstbetrag: looked up for 4 persons, then apportioned: Höchstbetrag × 2/4

## Kinderwohngeld

*Kinderwohngeld* is not a separate legal category but a colloquial term for a specific
constellation: a child in a Bedarfsgemeinschaft whose parents receive Bürgergeld
receives Wohngeld in their own right, causing them to **exit the Bedarfsgemeinschaft**.

### How it works

The mechanism relies on a chain of legal provisions:

1. Parents receiving Bürgergeld are excluded from Wohngeld (§7 Abs. 1 Satz 1 Nr. 1
   WoGG).
1. Children in the BG are normally also excluded (§7 Abs. 2 Satz 1 Nr. 1 WoGG — BG
   members whose income was considered in the Bürgergeld calculation are excluded).
1. **Exception**: The exclusion does not apply if Wohngeld would *avoid or eliminate
   Hilfebedürftigkeit* under §9 SGB II (§7 Abs. 1 Satz 3 Nr. 2 WoGG).
1. If Wohngeld together with other income (Kindergeld, Unterhalt, Unterhaltsvorschuss)
   covers the child's needs, the child is no longer hilfebedürftig.
1. A child that is not hilfebedürftig exits the BG (§7 Abs. 3 Nr. 4 SGB II — unmarried
   children under 25 belong to the BG only if they cannot cover their livelihood from
   their own income/assets).

The Kinderwohngeld is counted as the **child's** income, not the parent's. The child
forms (or joins) a wohngeldrechtlicher Teilhaushalt, creating a Mischhaushalt.

### Interaction with the Bedarfsgemeinschaft

When a child exits the BG via Kinderwohngeld:

- The BG shrinks (fewer members → different KdU split, different Regelsatz allocation)
- The child's Kindergeld is no longer counted as BG income (this typically benefits the
  remaining BG members)
- The parents' Bürgergeld may increase or decrease depending on the child's net
  contribution to the BG

```{note}
The family has a *Wahlrecht* (right to choose) — the BG cannot be forced to apply for
Kinderwohngeld if it would not eliminate the Hilfebedürftigkeit of **all** BG members
for at least 3 consecutive months (§12a Satz 2 Nr. 2 SGB II).
```

## Implementation status in GETTSIM

| Topic                            | Status                             | Issues                                                                                                               |
| -------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Gemischte Bedarfsgemeinschaft    | Implemented                        | [#1146](https://github.com/ttsim-dev/gettsim/issues/1146), [#1157](https://github.com/ttsim-dev/gettsim/issues/1157) |
| Einsatzgemeinschaft (`_eg`)      | Implemented                        | [#1147](https://github.com/ttsim-dev/gettsim/issues/1147)                                                            |
| Wohngeldrechtlicher Teilhaushalt | Partially implemented (simplified) | [#710](https://github.com/ttsim-dev/gettsim/issues/710), [#1010](https://github.com/ttsim-dev/gettsim/issues/1010)   |
| Kinderwohngeld                   | Not implemented                    | [#750](https://github.com/ttsim-dev/gettsim/issues/750)                                                              |
| Endogenous BG/WTHH creation      | Simplified; external repo planned  | [#763](https://github.com/ttsim-dev/gettsim/issues/763), [#1010](https://github.com/ttsim-dev/gettsim/issues/1010)   |

```{seealso}
**Gemischte Bedarfsgemeinschaft:**
- [SGB II §9 Abs. 2 Satz 3](https://www.gesetze-im-internet.de/sgb_2/__9.html):
  Bedarfsanteilsmethode
- [SGB II §19 Abs. 1 Satz 2](https://www.gesetze-im-internet.de/sgb_2/__19.html):
  No Bürgergeld for persons with SGB XII Kap. 4 claims
- [BSG B 14 AS 55/07 R](https://openjur.de/u/170185.html) (18.06.2008):
  Horizontal method for normal BGs
- [BSG B 14 AS 89/20 R](https://www.bsg.bund.de/SharedDocs/Entscheidungen/DE/2021/2021_11_11_B_14_AS_89_20_R.html) (11.11.2021):
  Vertical method for mixed BGs

**Wohngeldrechtlicher Teilhaushalt:**
- [WoGG §7](https://www.gesetze-im-internet.de/wogg/__7.html):
  Exclusion from Wohngeld
- [WoGG §11 Abs. 3](https://www.gesetze-im-internet.de/wogg/__11.html):
  Kopfteilige Miete in Mischhaushalten

**Kinderwohngeld:**
- [WoGG §7 Abs. 1 Satz 3 Nr. 2](https://www.gesetze-im-internet.de/wogg/__7.html):
  Exception from Wohngeld exclusion when it avoids Hilfebedürftigkeit
- [SGB II §7 Abs. 3 Nr. 4](https://www.gesetze-im-internet.de/sgb_2/__7.html):
  Children exit BG when not hilfebedürftig
- [SGB II §12a](https://www.gesetze-im-internet.de/sgb_2/__12a.html):
  Vorrangprüfung and Wahlrecht
```
