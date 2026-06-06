(childrens_income_grundsicherung_im_alter)=

# Children's income and Grundsicherung im Alter

Eligibility for Grundsicherung im Alter may depend on the income of the claimant's
children. The legal mechanism changed fundamentally on 2020-01-01; GETTSIM models only
the regime until 2019.

## 2005–2019: Exclusion from the benefit (§ 43 SGB XII)

Until the end of 2019, § 43 SGB XII (originally Abs. 2, later Abs. 5; BGBl. I 2003 S.
3022\) excluded persons from Grundsicherung im Alter altogether if any of their children
had an annual Gesamteinkommen (§ 16 SGB IV) of 100,000 Euro or more. Excluded persons
could claim Hilfe zum Lebensunterhalt (3. Kapitel SGB XII) instead, where the
Sozialhilfeträger could take recourse against the children (Unterhaltsrückgriff, § 94
SGB XII).

For policy dates up to 2019-12-31, GETTSIM sets `grundsicherung__im_alter__betrag_m` to
zero for persons for whom
`grundsicherung__im_alter__hat_kind_mit_einkommen_über_einkommensgrenze` is true. A
child's income is compared against the threshold parameter
`grundsicherung__im_alter__einkommensgrenze_kinder` (100,000 Euro per year). Children
are linked to their parents via `familie__p_id_elternteil_1` and
`familie__p_id_elternteil_2`; the threshold applies to each child individually, not to
the sum of all children's incomes.

```{note}
Caveats of the GETTSIM implementation:

- The law contains a Vermutungsregelung: the Sozialhilfeträger presumes that the
  children's income is below the threshold unless there are sufficient indications to
  the contrary (hinreichende Anhaltspunkte). GETTSIM abstracts from this procedural
  rule and applies the cutoff to observed incomes (full-enforcement assumption).
- The exclusion also covered the claimant's *parents'* income, which is mainly
  relevant for Grundsicherung bei Erwerbsminderung. This is not implemented (see
  [#1145](https://github.com/ttsim-dev/gettsim/issues/1145)).
- The fallback to Hilfe zum Lebensunterhalt of excluded persons and the
  Unterhaltsrückgriff against their children are currently not modeled.
```

## Since 2020: Recourse limit only (Angehörigen-Entlastungsgesetz)

The Angehörigen-Entlastungsgesetz (BGBl. I 2019 S. 2135) repealed § 43 Abs. 5 SGB XII as
of 2020-01-01. Since then, children's income no longer affects eligibility for or the
amount of Grundsicherung im Alter. The 100,000 Euro threshold lives on in § 94 Abs. 1a
SGB XII, where it limits the recourse of the Sozialhilfeträger against the children:
maintenance claims are only transferred to the Träger if a child's annual
Gesamteinkommen exceeds 100,000 Euro.

Because the recourse happens between the Sozialhilfeträger and the children, it does not
change the benefit received by the claimant. GETTSIM therefore computes Grundsicherung
im Alter independently of children's incomes for policy dates from 2020-01-01 onwards.
The fiscal burden shift from the Sozialhilfeträger to high-income children (i.e., the
recourse itself) is not modeled.

```{seealso}
- § 43 SGB XII in its version up to 2019:
  [buzer.de change history](https://www.buzer.de/gesetz/3415/index.htm)
- § 94 Abs. 1a SGB XII:
  [https://www.gesetze-im-internet.de/sgb_12/\_\_94.html](https://www.gesetze-im-internet.de/sgb_12/__94.html)
- Angehörigen-Entlastungsgesetz:
  [buzer.de](https://www.buzer.de/gesetz/13689/index.htm)
```
