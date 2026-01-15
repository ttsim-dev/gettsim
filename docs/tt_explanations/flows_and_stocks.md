(flows_and_stocks)=

# Flows, stocks, and sensible time periods

## Stock transitions need to be calculated outside of GETTSIM

It is useful to distinguish between two types of variables:

- **Flows**: Values per unit of time (e.g., gross monthly earnings from dependent
  employment `bruttolohn_m`, new pension points earned this year
  `neue_entgeltpunkte_y`). These always have a period suffix.
- **Stocks**: Accumulated values that persist over time (e.g., wealth `vermögen`,
  lifetime pension earnings points `entgeltpunkte`).

GETTSIM calculates tax and transfer amounts for a **single point in time**. It then
calculates flows for any of the supported period lengths (year, quarter, month, week,
day) by multiplying/dividing with the appropriate factors.

Stocks are updated by combining a stock with a flow (next period's wealth would be
after-tax income including asset price changes minus consumption; `entgeltpunkte` and
`neue_entgeltpunkte_y` would simply be added up).

**This transition has to be done outside of GETTSIM.** That is, GETTSIM does not
automatically accumulate flows into stocks because it would need to know the length of
the period you are thinking about. Since

1. these rules are typically very simple (as in the two examples above),
1. adding this period length as a parameter to `main` would entail large costs, and
1. it affects only a small subset of use cases (dynamic models),

we decided against including it. Put differently, GETTSIM will only ever calculate
flows; stocks are input variables.

## Sensible evaluation periods

The automatic time conversion inside of GETTSIM assumes constancy across different
intervals. This may or may not make sense. Some examples:

- **Income tax** (`einkommensteuer`): Only sensible at the annual level, since tax
  liability is determined yearly.
- **Altersrente**: In the year of reaching normal retirement age, pension benefits only
  apply for part of the year.
- **Elterngeld**: Only makes sense at the monthly level; it is almost impossible that it
  is constant within a year since eligibility and amounts change as the child ages.
- **Mid-year rule changes**: Some policies change mid-year, making annual averages
  misleading:
  - July 2017: Unterhaltsvorschuss reform (extended eligibility)
  - July 2023: Pension system unification (Rentenwert Ost = West)
  - January 2023: Bürgergeld replaced ALG 2

## Recipe for being precise when we can't assume constancy

If you need to be precise across programmes with different evaluation frequency---e.g.,
calculating Elterngeld and income taxes---you can:

1. Run GETTSIM for each month to get the monthly values of Elterngeld
1. Sum them up and pass them as inputs to another GETTSIM run for calculating income
   taxes.

This is simply a consequence of the fact that GETTSIM does not allow for long format in
terms of calendar time; it just allows for long format in terms of persons / households
(see {ref}`hh_concepts`).

Here's an example for calculating annual Elterngeld by summing monthly values:

```python
from gettsim import InputData, MainTarget, TTTargets, main

# Calculate Elterngeld for each month and sum up
elterngeld_total = 0.0
for month in range(1, 13):
    results = main(
        policy_date_str=f"2024-{month:02d}-01",
        input_data=InputData.tree(monthly_inputs),
        tt_targets=TTTargets.tree({"elterngeld": {"betrag_m": None}}),
    )
    elterngeld_total += results["elterngeld"]["betrag_m"].sum()

# Use the annual total as input for income tax calculation
annual_inputs = {
    ...,
    "elterngeld": {"betrag_y_sn": elterngeld_total},
}
tax_results = main(
    policy_date_str="2024-01-01",
    input_data=InputData.tree(annual_inputs),
    tt_targets=TTTargets.tree({"einkommensteuer": {"betrag_y_sn": None}}),
)
```
