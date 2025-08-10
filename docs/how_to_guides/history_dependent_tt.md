# How to calculate taxes and transfers that depend on prior-year values

Many tax and transfer programs base their calculations not only on current information
but also on data from previous years. For example, parental leave benefits often rely on
an estimate of the claimant’s net income during the 12 months preceding the child’s
birth.

As GETTSIM is a static taxes and transfers calculator for a specific policy date, it is
not able to calculate these taxes and transfers in a single run. However, GETTSIM
provides policy functions that make it very easy to calculate these taxes and transfers
by calling GETTSIM multiple times.

## General recipe

In general, follow this recipe to calculate these taxes and transfers:

1. **Identify historical inputs**: Determine which historical inputs you need to
   calculate the taxes and transfers for the year you're interested in. These are always
   input variables marked with `@policy_input()`. Look for keywords like `vorjahr`
   (previous year) in the variable names.

1. **Calculate historical inputs using panel data**: Every historical input function
   corresponds to a policy function you can select as a target in a GETTSIM call. For
   example, `("elterngeld", "zu_versteuerndes_einkommen_vorjahr_y_sn")` can be
   calculated via `("einkommensteuer", "zu_versteuerndes_einkommen_y_sn")` using data
   from the year prior to the birth of the child. These relationships are typically
   documented in the `policy_input` docstring.

1. **Use historical inputs for final calculation**: Use the calculated historical inputs
   as inputs for the policy functions you're interested in to get the final result.

## Examples

Below is a non-exhaustive list of taxes and transfers that require historical inputs,
along with the specific policy functions needed.

**Elterngeld (Parental Allowance)**

For a thorough explanation on how to calculate Elterngeld, see the
[Elterngeld tutorial](calculating_elterngeld.ipynb).

**Pensions**

Pensions are based on Entgeltpunkte (earnings points), which are calculated from
historical income:

- **Historical input**:
  - Since July 2023: `("sozialversicherung", "rente", "entgeltpunkte")`
  - Before July 2023: `("sozialversicherung", "rente", "entgeltpunkte_west")` and
    `("sozialversicherung", "rente", "entgeltpunkte_ost")`
- **Calculation targets**:
  - Since July 2023: `("sozialversicherung", "rente", "entgeltpunkte_updated")`
  - Before July 2023: `("sozialversicherung", "rente", "entgeltpunkte_updated_west")`
    and `("sozialversicherung", "rente", "entgeltpunkte_updated_ost")`

**Unemployment benefits (Arbeitslosengeld)**

Unemployment benefits are based on historical income:

- **Historical input**:
  `("arbeitslosengeld", "mean_nettoeinkommen_in_12_monaten_vor_arbeitslosigkeit_m")`
- **Calculation target**:
  `("arbeitslosengeld", "mean_nettoeinkommen_für_bemessungsgrundlage_bei_arbeitslosigkeit_y")`
