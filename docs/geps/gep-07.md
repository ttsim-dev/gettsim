(gep-7)=

# GEP 7 — GETTSIM's User Interface

```{list-table}
- * Author
  * [Hans-Martin von Gaudecker](https://github.com/hmgaudecker)
- * Status
  * Draft
- * Type
  * Standards Track
- * Created
  * 2025-07-23
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/channel/309998-GEPs/topic/GEP.2007/near/530389224)
```

## Abstract

This GEP proposes a new user interface for GETTSIM that simplifies data input/output
handling, reduces the learning curve for new users, and provides more flexibility in
working with different datasets. The interface redesign aims to address the challenges
identified during the 2024 GETTSIM workshop and, more generally, experience with using
GETTSIM versions up to 0.7.0. At the same time, we maintain compatibility with the
namespace architecture introduced in GEP 6.

## Motivation and Scope

The current GETTSIM interface presents several challenges that affect both new and
experienced users:

1. **High Entry Barrier**: Users need detailed knowledge of the Directed Acyclic Graph
   (DAG) structure and precise input requirements, making it difficult for newcomers to
   get started.

1. **Data Mapping Complexity**: Matching existing datasets with GETTSIM's requirements
   is challenging due to the fine-grained nature of the graph.

1. **Limited Flexibility**: The current interface makes it difficult to work with
   different datasets / areas of the taxes and transfers system.

This GEP aims to address these issues by introducing a more intuitive and flexible
interface while maintaining GETTSIM's computational robustness.

## Usage and Impact

1. **Basic workflow**

   There is a single entry point for GETTSIM: The `main` function. It is powered by a
   DAG in the background.

   This means that the user will have to start by telling it the desired target
   ("`main_target`") or set of targets ("`main_targets`"). Ultimately, the main target
   will typically be a dataset with values for taxes and transfers. However, the `main`
   function can also be used to obtain intermediate objects. E. g., the taxes and
   transfers system at a particular date (the "`policy_environ­ment`"), which she wants
   to modify in order to model a reform.

   The targets determine the required inputs. For example, in order to compute taxes and
   transfers for a set of households, one will need as primitives

   - the date for which the policy environment is set up ("`policy_date_str`")
   - data on these households ("`input_data`")
   - the set of taxes and transfers to be computed ("`tt_targets`"). This could be left
     out, in which case all possible targets will be computed. However, that will often
     be a daunting task in terms of requirements on the data and computer memory.

   If only a policy environment is to be returned, just the date is required as an
   input.

1. **Worked example**

   Here is an example (the variables `inputs_df`, `inputs_map`, and `targets_tree` will
   be shown below).

   ```python
   from gettsim import InputData, MainTarget, TTTargets, main


   outputs_df = main(
       main_target=MainTarget.results.df_with_mapper,
       policy_date_str="2025-01-01",
       input_data=InputData.df_and_mapper(
           df=inputs_df,
           mapper=inputs_map,
       ),
       tt_targets=TTTargets(tree=targets_tree),
   )
   ```

   All elements that are not atomic are specified as GETTSIM objects, which means that
   users can benefit from autocompletion and type hints provided by their IDE (see
   below).

   The first argument, `main_target`, specifies the type of object to compute. In this
   case, we want the "results" in the "DataFrame with mapper" format. That is, GETTSIM
   will compute all desired targets and return a DataFrame with columns specified by the
   user.

   Say we want to compute the contributions to long term care insurance
   (Pflegeversicherung). The fourth argument, `tt_targets`, specifies the set of taxes
   and transfers ("`tt`") to compute. Because we ask for the "results" in the "DataFrame
   with mapper" format, this actually has to be a mapping from the targets to the
   columns in the output DataFrame. In this case, the argument `tt_targets` needs to be
   a *pytree*, which provides that mapping:

   ```python
   targets_tree = {
       "sozialversicherung": {
           "pflege": {
               "beitrag": {
                   "betrag_versicherter_m": "ltci_contrib",
               }
           }
       }
   }
   ```

   That is, the call to `main` above will return a DataFrame with one column
   `ltci_contrib`, which will be of the same length as the input data. As the possible
   target trees will depend on the policy environment, we will need to make the
   documentation dynamic.

   The second argument, `policy_date_str`, specifies the date at which the policy
   environment is set up and evaluated.

   Say we want to compute the long term care insurance contribution for three people,
   one of whom has an underage child living in her household. Our data looks as follows:

   |     | age | wage |  id | hh_id | mother_id | has_kids |
   | --: | --: | ---: | --: | ----: | --------: | :------- |
   |   0 |  25 |  950 |   0 |     0 |        -1 | False    |
   |   1 |  45 |  950 |   1 |     1 |        -1 | True     |
   |   2 |   3 |    0 |   2 |     1 |         1 | False    |
   |   3 |  65 |  950 |   3 |     2 |        -1 | True     |

   We can use this DataFrame directly. All we need to do is to tell GETTSIM how to map
   the columns of that DataFrame to the names of inputs it knows about. This is done by
   a *mapper*, which again is a *pytree*. In our case, it looks as follows:

   ```python
   inputs_map = {
       "p_id": "id",
       "hh_id": "hh_id",
       "alter": "age",
       "familie": {
           "p_id_elternteil_1": "mother_id",
           "p_id_elternteil_2": -1,
       },
       "einkommensteuer": {
           "einkünfte": {
               "aus_nichtselbstständiger_arbeit": {"bruttolohn_m": "wage"},
               "ist_selbstständig": False,
               "aus_selbstständiger_arbeit": {"betrag_m": 0.0},
           }
       },
       "sozialversicherung": {
           "pflege": {
               "beitrag": {
                   "hat_kinder": "has_kids",
               }
           },
           "kranken": {
               "beitrag": {"bemessungsgrundlage_rente_m": 0.0, "privat_versichert": False}
           },
       },
   }
   ```

   All *leaves* of the tree are either column names in the data or scalars. E.g., we do
   not consider self-employed people, pensioners, or people with (substitutive) private
   health insurance. Instead of requiring some default value in the data, we can simply
   use a scalar value in the mapper.

   *Note:* We picked an example with little, but not zero, complexity. The amount of
   inputs is simply necessary because public long term care insurance contributions
   depend on various kinds of income (from dependent employment, from self-employment,
   pensions), the combination of the insured person's age and her children, and whether
   the insured person is covered by private health insurance.

   Finally, here is the output of our example:

   |     | ltci_contrib |
   | --: | -----------: |
   |   0 |        14.72 |
   |   1 |         9.82 |
   |   2 |            0 |
   |   3 |         9.82 |

1. **Underlying structure**

   The interface DAG looks as follows:

   ```{raw} html
   ---
   file: ./interface_dag.html
   ---
   ```

   The **policy_date** is the date at which the policy environment is set up. It could
   be passed as `policy_date_str`, which is an ISO-string `YYYY-MM-DD`. By default, it
   is also used as the date for which the taxes and transfers function is evaluated (the
   distinction matters for things like pensions etc., which depend on cohort, age, and
   calendar time). If users need more control, `evaluation_date` (or
   `evaluation_date_str`) can be specified separately.

   The **policy environment** consists of all functions relevant at some point in time.
   E.g., when requesting a policy environment for some date in the 2020s, Erziehungsgeld
   will not be part of it because it was replaced by Elterngeld long before. Users
   wishing to implement reforms—whether they consist of changing parameter values or
   replacing functions—will do so at the level of the policy environment.

   The **input data** are the data provided by the user. They need to be passed in one
   of several forms.

   Users specify the **taxes and transfers targets** ("`tt_targets`"), which GETTSIM
   will return. When left out, GETTSIM will return all functions it can compute.

   The elements of the **specialized environment** combine policy environment and data.
   Even if users do not typically need to work with these elements, they are so central
   to GETTSIM that it is useful to list them here.

   - **with derived functions and without tree logic** adds aggregations (e.g., adding
     up individual incomes to income at the Steuernummer level) and time conversions
     (e.g., from month to year). Doing so requires knowing the names of the columns in
     the data.
   - **with processed params and scalars**. The parameters of the taxes and transfers
     system are stored in special objects. Some of them require further conversion
     through functions that do not depend on household data ("`param_functions`").
     Similarly, it is possible to pass scalars instead of data columns for things that
     are not observed in a dataset or that can be assumed constant in a particular
     application (e.g., setting pension payments to zero when looking at the labor
     supply of 30-year olds). In this step, these functions are run and all parameters
     are converted to their final form (e.g., a `ScalarParam` becomes just a number).
     Where relevant, policy functions are replaced by scalars passed as input data.
   - **with partialled params and scalars** partials all parameters and scalars to the
     functions that make up the taxes and transfers DAG. That is, the resulting
     functions only depend on column arguments (either passed as input data or computed
     earlier in the DAG).
   - **taxes and transfers DAG** is the DAG representation of the functions in the
     previous step.
   - **taxes and transfers function** is the function that takes the columns in the
     processed data as arguments and returns the desired taxes and transfers targets.
     Running this function leads to raw results (they still contain internals and should
     not be used by non-GETTSIM functions)

   The **results** contain the output of the taxes and transfers function, purged of
   internals and converted to the format requested by the user.

   The German taxes and transfers system is complex and specifying inputs can be a
   daunting task. The **templates** aim to help with that. E.g., asking for
   `MainTarget.templates.input_data` will return a nested dictionary that may include:

   ```python
   {
       "einkommensteuer": {
           "einkünfte": {"aus_forst_und_landwirtschaft": {"betrag_y": "FloatColumn"}}
       }
   }
   ```

   These templates can be modified to become a mapper, as in the above example. That is,
   "`FloatColumn`" could be replaced by the name of the column in the input data frame
   or by 0.0 if only employees who don't have other types of income are in the sample.

   Additional user-facing elements are:

   - **rounding** is a Boolean that determines whether to round the results. Defaults to
     `True`, which yields a more accurate depiction of the taxes and transfers system.
     Turn off if you need numerical derivatives or the like.

   * The **backend** is the backend used to compute the taxes and transfers. Default is
     `"numpy"`, the other option is `"jax"`.
   * **include_fail_nodes** is a Boolean that determines whether to raise errors for
     invalid inputs. Defaults to `True`, only turn off if you really know what you are
     doing (and even then, please turn it on before filing an issue).
   * **include_warn_nodes** is a Boolean that determines whether to display warnings for
     some cases that might lead to surprising behavior. Defaults to `True`, only turn
     off if you really know what you are doing (and even then, please turn it on before
     filing an issue).

   Other elements of the interface DAG, which will typically be less relevant for users,
   include:

   - The **original policy objects**, which consist of all functions and parameters that
     GETTSIM ships with. These are all functions and parameters that have been relevant
     at some point in time. A user won't typically need to work with this; a policy
     environment is constructed from this and a date.
   - The **labels** contain things like column names, names of root nodes, etc. —
     anything where we only need the label of something and not the object itself.
   - **num_segments** is the number of unique individuals in the data. It is required by
     the Jax backend to aggregate by group / another individual. determine the number of
     segments in the data.

1. **Autocompletion features**

   The internal structure of the building blocks described in the previous section can
   be rather complex. In order to minimize errors arising from typos and misconceptions,
   GETTSIM provides objects that allow to take advantage of modern IDEs'/editors'
   autocompletion and type hinting features.

   For example, after:

   ```python
   from gettsim import main, MainTarget

   main(main_target=MainTarget.)
   ```

   tools like VS Code will show the options:

   ```python
   results
   templates
   policy_environment
   specialized_environment
   orig_policy_objects
   processed_data
   raw_results
   labels
   policy_date_str
   input_data
   tt_targets
   num_segments
   backend
   policy_date
   evaluation_date_str
   evaluation_date
   xnp
   dnp
   rounding
   warn_if
   fail_if
   ```

   Such objects are provided for all arguments to main that need a hierarchical
   structure. E.g. , the `input_data` argument takes an instance of `InputData` like in
   the above example. Again, one will be able to benefit from autocompletion features
   from typing the first 'I' onwards.

1. **Ecosystem**

   More functionality will be added in external packages. Check out:

   - [gettsim-personas](https://github.com/ttsim-dev/gettsim-personas): Pre-defined
     example personas ("Musterhaushalte")
   - [soep-preparation](https://github.com/ttsim-dev/soep-preparation): A pipeline
     preparing the SOEP data for use with GETTSIM

1. **Interactive Graph Interface**

   We focus on the infrastructure for the moment; this will be easy to add and will
   require a much more interactive and user-driven approach. Top-down planning does not
   seem useful at this point.

## Backward Compatibility

This interface represents a significant change. There is no way to ensure backward
compatibility. This said, the former:

```python
from gettsim import (
    set_up_policy_environment,
    compute_taxes_and_transfers,

policy_params, policy_functions = set_up_policy_environment(2025)
result = compute_taxes_and_transfers(
    data=data,
    functions=policy_functions,
    params=policy_params,
    targets=targets,
)
```

can be replaced by:

```python
from gettsim import main, InputData, MainTarget, TTTargets

outputs = main(
    main_targets=[
        MainTarget.policy_environment,
        MainTarget.results.df_with_mapper,
    ],
    policy_date_str="2025-01-01",
    input_data=InputData.df_and_mapper(
        df=data,
        mapper=inputs_map,
    ),
    tt_targets=TTTargets(tree=tt_targets_tree),
)
policy_environment = outputs["policy_environment"]
result = outputs["results"]["df_with_mapper"]
```

Beyond the interface change, users will need to change `targets` to `tt_targets_tree`
and to create the `inputs_map`. Both adjustments are due to the changes in the internal
structure of GETTSIM described in [GEP 6](gep-06).

## Discussion

- **ENH: Interface, 2024 edition · Issue #781 · iza-institute-of-labor-economics/gettsim
  \- Part 1**.
  [https://github.com](https://github.com/iza-institute-of-labor-economics/gettsim/issues/781)

## Copyright

This document has been placed in the public domain.
