# How to calculate input variables from prior periods' states

Many taxes and transfers require inputs from prior periods to serve as inputs for this
year's calculations.

For example, parental leave benefits often rely on an estimate of the claimant's net
income during the 12 months preceding the child's birth.

Another example is the calculation of public pension benefits, which relies on a measure
of lifetime earnings that is accumulated and updated each month. Prior-period inputs
therefore include both values taken from a fixed historical window (as in parental
leave) and state variables that evolve over time and are carried forward into the
current period.

## General recipe

In general, follow this recipe to calculate these taxes and transfers:

1. **Identify past inputs** Determine which past inputs you need to calculate the taxes
   and transfers for the year you are interested in. These will always be input
   variables marked with `@policy_input`.

1. **Calculate past inputs using panel data** Each past input corresponds to a policy
   function you can target in a GETTSIM run. For instance, the input (`"elterngeld"`,
   `"zu_versteuerndes_einkommen_vorjahr_y_sn"`) can be derived by calling
   `("einkommensteuer", "zu_versteuerndes_einkommen_y_sn")` for the year prior to the
   child’s birth. These connections, if present, are explained in the `@policy_input`s'
   docstrings.

1. **Use past inputs for final calculation** After computing the past values, include
   them among the inputs to the policy functions of interest to obtain the final tax or
   transfer amounts.

## Examples

Below is a non-exhaustive list of taxes and transfers that require past inputs that can
be calculated using GETTSIM, along with the specific policy functions that will do so.

**Elterngeld (Parental Allowance)**

For a thorough explanation on how to calculate Elterngeld, see the
[Elterngeld tutorial](calculating_elterngeld.ipynb).

**Pensions**

Pensions are based on Entgeltpunkte (earnings points), which are calculated from
lifetime earnings:

- **Past inputs**:
  - Since July 2023: `("sozialversicherung", "rente", "entgeltpunkte")`
  - Before July 2023: `("sozialversicherung", "rente", "entgeltpunkte_west")` and
    `("sozialversicherung", "rente", "entgeltpunkte_ost")`
- **Calculation target**: `("sozialversicherung", "rente", "neue_entgeltpunkte_y")`
  - This returns the yearly earnings points earned in the current year
  - For other time units, request `neue_entgeltpunkte_m`, `neue_entgeltpunkte_q`, etc.
    (these are auto-generated via time conversion)
- **Stock accumulation**: Users are responsible for accumulating earnings points. Add
  `neue_entgeltpunkte_y` to the previous year's `entgeltpunkte` to get the updated
  lifetime total.

**Unemployment benefits (Arbeitslosengeld)**

Unemployment benefits are based on the income in the 12 months preceding the beginning
of the unemployment spell:

- **Historical input**:
  `("arbeitslosengeld", "mean_nettoeinkommen_in_12_monaten_vor_arbeitslosigkeit_m")`
- **Calculation target**:
  `("arbeitslosengeld", "mean_nettoeinkommen_für_bemessungsgrundlage_bei_arbeitslosigkeit_y")`
