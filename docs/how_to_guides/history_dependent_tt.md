# How to calculate taxes and transfers that depend on prior-year values

Many taxes and transfers require historical inputs computed in the prior year to serve
as inputs for this year’s calculations. For example, parental leave benefits often rely
on an estimate of the claimant’s net income during the 12 months preceding the child’s
birth.

As GETTSIM is a static taxes and transfers calculator for a specific policy date, it is
not able to calculate these taxes and transfers in a single run. However, GETTSIM
provides policy functions that make it very easy to calculate these taxes and transfers
by calling GETTSIM multiple times.

## General recipe

In general, follow this recipe to calculate these taxes and transfers:

1. **Identify historical inputs** Determine which historical inputs you need to
   calculate the taxes and transfers for the year you're interested in. These are always
   input variables marked with `@policy_input`.

1. **Calculate historical inputs using panel data** Each historical input corresponds to
   a policy function you can target in a GETTSIM run. For instance, the input
   ("elterngeld", "zu_versteuerndes_einkommen_vorjahr_y_sn") can be derived by calling
   ("einkommensteuer", "zu_versteuerndes_einkommen_y_sn") for the year prior to the
   child’s birth. These connections are explained in the `@policy_input` docstrings.

1. **Use historical inputs for final calculation** After computing the historical
   inputs, use them as inputs to the policy functions of interest to obtain the final
   tax or transfer amounts.

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
