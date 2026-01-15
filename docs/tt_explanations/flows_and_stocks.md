(flows_and_stocks)=

# Flows, stocks, and sensible time periods

## Stock transitions need to be calculated outside of GETTSIM

It is useful

- **Flows**: Values per unit of time (e.g., gross monthly earnings from dependent
  employment `bruttolohn_m`, new pension points earned this year
  `neue_entgeltpunkte_y`). These always have a period suffix.
- **Stocks**: Accumulated values that persist over time (e.g., wealth `vermögen`,
  lifetime pension earnings points `entgeltpunkte`).

GETTSIM calculates tax and transfer amounts for a **single point in time**. It then
calculates flows for any of the supported period lengths (year, quarter, month, week,
day) by multiplying/dividing with the appropriate factors.

Stocks are updated by a combining a stock with a flow (next period's wealth would be
after-tax income including asset price changes minus consumption; `entgeltpunkte` and
`neue_entgeltpunkte_y` would simply be added up).

**This transition has to be done outside of GETTSIM.** That is, GETTSIM does not
automatically accumulate flows into stocks because it would mean it would need to know
the length of the period you are thinking about. Since

1. these rules are typically very simple (as in the two examples above),
1. adding this period length as a parameter to `main` would entail large costs and
1. it affects only a small subset of use cases (dynamic models) we decided against
   including it. Put differently, GETTSIM will only ever calculate flows; stocks are
   input variables.

## Sensible evaluation periods

The automatic time conversion inside of GETTSIM assume constancy across different
intervals. This may or may not make sense. Some examples

Examples:

- income tax only annualy
- aktivrente in the year of becoming eligible, i.e., reaching nra
- elterngeld only makes sense at the monthly level; it is almost impossible that it is
  constant within a year
- alg 2 / bürgergeld when the rules change mid-year (e.g. 2023 and Claude: find other
  examples)

## Recipe for being precise when we can't assume constancy

If you need to be precise across programmes with different evaluation frequency---e.g.,
calculating Elterngeld and income taxes---you can:

1. Run GETTSIM for each month to get the monthly values of Elterngeld
1. Sum them up and pass them as inputs to another GETTSIM run for calculating income
   taxes.

This is simply a consequence of the fact that GETTSIM does not allow for long format in
terms of calendar time; it just allows for long format in terms of persons / households
(see link to hh_concepts).

Here's the example (change to Elterngeld):

```python
entgeltpunkte = 0.0  # Initial stock
for year in range(start_year, end_year):
    results = main(
        policy_date_str=f"{year}-01-01",
        input_data=InputData.tree({..., "entgeltpunkte": entgeltpunkte}),
        tt_targets=TTTargets.tree({"sozialversicherung": {"rente": {"neue_entgeltpunkte_y": None}}}),
    )
    # Accumulate the flow into the stock
    entgeltpunkte += results["sozialversicherung"]["rente"]["neue_entgeltpunkte_y"]
```

You may see these values directly in your input data, in which case there is nothing to
do beyond the usual procedure.
