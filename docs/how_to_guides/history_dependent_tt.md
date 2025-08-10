# How to calculate taxes and transfers that depend on taxes or transfers from previous years

Many taxes and transfers depend on calculations from previous years. Parental leave
benefits, for instance, depend on an approximated version of the parental net income in
the 12 months before the birth of the child.

As GETTSIM is a static taxes and transfers calculator for a specific policy date, it is
not able to calculate these taxes and transfers in a single run. However, GETTSIM
provides policy functions that make it very easy to calculate these taxes and transfers
by calling GETTSIM multiple times.

## General recipe

In general, follow this recipe to calculate these taxes and transfers:

1. Identify which historical inputs you need to calculate the taxes and transfers for
   the year you're interested in. Usually those are input variables (marked via
   `@policy_input()`). Sometimes they contain keywords like `vorjahr` to indicate that
   they should be calculated for the previous year.
1. Use panel data to calculate the historical inputs. Every such input function
   corresponds to a policy function you can select as a target in a GETTSIM call.
   `("elterngeld", "zu_versteuerndes_einkommen_vorjahr_y_sn")`, for example, can be
   calculated via `("einkommensteuer", "zu_versteuerndes_einkommen_y_sn")` using data
   from the year prior to the birth of the child. Usually, those links are documented in
   the `policy_input` docstring.
1. Use the calculated historical inputs to calculate the taxes and transfers for the
   year you're interested in. That is, use the results from the previous step as inputs
   for the policy functions you're interested in.

## Examples

Here is a (non-exhaustive) list of taxes and transfers that require historical inputs.

### Elterngeld

For a thorough explanation on how to calculate Elterngeld, see the
[Elterngeld tutorial](calculating_elterngeld.ipynb).

### Erziehungsgeld

The parental leave benefits before 2008 need
`("erziehungsgeld", "bruttolohn_vorjahr_nach_abzug_werbungskosten_y")`. Calculate it
using the target
`("einkommensteuer", "einkünfte", "aus_nichtselbstständiger_arbeit", "einnahmen_nach_abzug_werbungskosten_y")`.

### Pensions

Pensions are based on Entgeltpunkte, which are calculated based on historical income.
The corresponding policy input is `("sozialversicherung", "rente", "entgeltpunkte")`
since July 2023, `entgeltpunkte_west` and `entgeltpunkte_ost` before. You can calculate
them using historical income data via the
`("sozialversicherung", "rente","entgeltpunkte_updated")` (or
`("sozialversicherung", "rente","entgeltpunkte_updated_west")` /
`("sozialversicherung", "rente","entgeltpunkte_updated_ost")` before July 2023) policy
functions.

### Unemployment benefits

Unemployment benefits are based on historical income. The corresponding policy input is
`("arbeitslosengeld", "mean_nettoeinkommen_in_12_monaten_vor_arbeitslosigkeit_m")`.
Calculate it using the target
`("arbeitslosengeld", "mean_nettoeinkommen_für_bemessungsgrundlage_bei_arbeitslosigkeit_y")`.

### Grundrente

The Grundrente is based on historical income. The corresponding policy input is
`("sozialversicherung", "rente", "grundrente", "gesamteinnahmen_aus_renten_vorjahr_m")`.
Calculate it using the target
`("sozialversicherung", "rente", "grundrente", "gesamteinnahmen_aus_renten_für_einkommensberechnung_im_folgejahr_m")`.
