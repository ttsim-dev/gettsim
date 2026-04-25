(besteuerung-renteneinkünfte)=

# Taxation of pension income

The taxation of pension income depends on how contributions were taxed during the
accumulation period. Since 2005, there are two types of taxation schemes:

- **Deferred taxation** (nachgelagerte Besteuerung): Pension income is fully (or
  partially) taxed when payout is received.
- **Ertragsanteilbesteuerung**: Pension income is taxed based on a fixed share of the
  notional return.

In principle, pensions that were favourably taxes during the accumulation phase (i.e.,
contributions were fully or partially income tax-deductible) are taxed via the deferred
taxation schemes. Pensions for which contributions were paid from already-taxed income
are taxed via the Ertragsanteilbesteuerung.

Before 2005, all pensions were taxed via the Ertragsanteilbesteuerung.

## Mapping products to GETTSIM input columns

All inputs below live under `einnahmen.renten`.

### 1st pillar (statutory)

1st pillar pensions are subject to deferred taxation since 2005 (AltEinkG, BGBl. 2004 I
Nr. 33). There is a phase-in based on the year of retirement that determines the taxable
share of the pension (Besteuerungsanteil, § 22 Nr. 1 Satz 3 Buchst. a aa EStG).

You can pass them to GETTSIM via the following inputs:

- `einnahmen.renten.gesetzliche_m` — Gesetzliche Rentenversicherung (DRV).
- `einnahmen.renten.aus_berufsständischen_versicherungen_m` — Berufsständisches
  Versorgungswerk (Ärzte, Anwälte, Apotheker, etc.).

### 2nd pillar (occupational)

According to § 19 EStG, occupational pensions are fully taxable (§ 22 Nr. 5 EStG / § 19
EStG).

You can pass them to GETTSIM via the following input:

- `einnahmen.renten.betriebliche_altersvorsorge_m` — Betriebliche Altersversorgung.

### 3rd pillar (private)

Private pensions are subject to deferred taxation or Ertragsanteilbesteuerung depending
on how contributions were taxed during accumulation.

The following inputs are taxed at the deferred taxation regime:

- **einnahmen.renten.basisrente_m** — Basisrente / Rürup-Rente. Taxed at the
  Besteuerungsanteil (§ 22 Nr. 1 Satz 3 Buchst. a aa EStG).
- **einnahmen.renten.geförderte_private_vorsorge_m** — Riester-Rente and other Verträge
  subsidised via § 10a EStG. Fully taxable (§ 22 Nr. 5 EStG).

Additionally, other private pensions that were not subsidised during accumulation are
taxed via the Ertragsanteilbesteuerung (§ 22 Nr. 1 Satz 3 Buchst. a bb EStG):

- **einnahmen.renten.sonstige_private_vorsorge_m** — Kapitallebensversicherung and other
  private pension plans outside Basisrente / Riester.
