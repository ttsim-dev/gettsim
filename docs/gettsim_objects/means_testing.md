(means_testing)=

# Assets considered for means testing

The table below gives an overview of all tangible and intangible assets which are
considered when performing means for several transfers. A cross indicates that the asset
class is not considered and, hence, deducted from the overall assets.

This documentation shall help to understand the composition of the

{ref}`basic input variable <input_variables>`

'vermögen'. Despite small differences over the transfers, we decided, for now, to
require only one wealth variable as input and use it for all transfers.

Note that GETTSIM requests wealth on the individual level as input. This variable is
then aggregated on the respective grouping level for each transfer (some transfers are
calculated at the sub-household level (Bedarfsgemeinschaften), which is endogenous). In
most data sets wealth is only measured on the household level and, hence, needs to be
split up on the individual level before feeding it into GETTSIM. If in doubt, robustness
checks regarding different distributions of wealth across household members might be in
order.

```{note}
ALGII = Grundsicherung für Arbeitslose

GSA/E = Grundsicherung im Alter/ bei Erwerbsminderung

WoGe = Wohngeld

KiZu = Kinderzuschlag

HC = hardship case
(Asset class is not considered if it would constitute a particular hardship for that person, see § 90 Abs.3 SGBXII [https://www.gesetze-im-internet.de/sgb_12/\_\_90.html](https://www.gesetze-im-internet.de/sgb_12/__90.html))
```

| Not counted as assets                                                             | ALGII  | GSA/E  | WoGe | KiZu   |
| --------------------------------------------------------------------------------- | ------ | ------ | ---- | ------ |
| Appropriate household goods                                                       | x      | x      | x    | x      |
| Adequate motor vehicle for eachperson capable of working                          | x      | x (HC) | x    | x      |
| Assets for retirement provision andretirement assets                              | x      | x      | x    | x      |
| Owner-occupied house/apartment ofappropriate size                                 | x      | x      | x    | x      |
| Assets for obtaining/maintaining a houseproperty for people in need of care       | x      | x      | x    | x      |
| Assets to build up/secure a livelihoodor establishment of a household             | x      | x      | x    | x      |
| Family and heirloom pieces                                                        | x (HC) | x      |      | x (HC) |
| Property and rights, if realization wouldbe uneconomical or a particular hardship | x      | x      |      | x      |
| Items to start/continue vocationaltraining/employment                             | x      | x      | x    | x      |
| Items for the satisfaction of spiritual needs                                     |        | x      | x    |        |

```{seealso}
See the following links for legal bases for the definition of assets for each transfer.
: - ALGII: §12 SGBII [https://www.gesetze-im-internet.de/sgb_2/\_\_12.html](https://www.gesetze-im-internet.de/sgb_2/__12.html)
  - GSA/E: §90 SGBXII [https://www.gesetze-im-internet.de/sgb_12/\_\_90.html](https://www.gesetze-im-internet.de/sgb_12/__90.html)
  - WoGe: §21 WoGG [https://www.gesetze-im-internet.de/bkgg_1996/\_\_6a.html](https://www.gesetze-im-internet.de/bkgg_1996/__6a.html)
  - KiZu: §6a BKGG, Abs.3 [https://www.gesetze-im-internet.de/bkgg_1996/\_\_6a.html](https://www.gesetze-im-internet.de/bkgg_1996/__6a.html)
```
