"""Input columns."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Literal

from gettsim.germany import WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC
from gettsim.tt import group_creation_function, policy_input

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.typing import BoolColumn, IntColumn


@policy_input()
def p_id() -> int:
    """Unique identifier for each person. Always required, must be unique."""


@policy_input()
def hh_id() -> int:
    """Individuals living together in a household in the Wohngeld sense (§5 WoGG)."""


@group_creation_function()
def ehe_id(
    p_id: IntColumn,
    familie__p_id_ehepartner: IntColumn,
    xnp: ModuleType,
) -> IntColumn:
    """Couples that are either married or in a civil union."""
    n = xnp.max(p_id) + 1
    p_id_ehepartner_or_own_p_id = xnp.where(
        familie__p_id_ehepartner < 0,
        p_id,
        familie__p_id_ehepartner,
    )
    result = (
        xnp.maximum(p_id, p_id_ehepartner_or_own_p_id)
        + xnp.minimum(p_id, p_id_ehepartner_or_own_p_id) * n
    )

    return result


@group_creation_function(leaf_name="fg_id", end_date="2022-12-31")
def fg_id_arbeitslosengeld_2(
    arbeitslosengeld_2__p_id_einstandspartner: IntColumn,
    p_id: IntColumn,
    hh_id: IntColumn,
    alter: IntColumn,
    familie__p_id_elternteil_1: IntColumn,
    familie__p_id_elternteil_2: IntColumn,
    xnp: ModuleType,
    backend: Literal["numpy", "jax"],
) -> IntColumn:
    """Familiengemeinschaft. Base unit for some transfers.

    Maximum of two generations, the relevant base unit for Bürgergeld / Arbeitslosengeld
    2, before excluding children who have enough income to fend for themselves.
    """
    return sgb_ii_fg_id_formula(
        p_id_einstandspartner=arbeitslosengeld_2__p_id_einstandspartner,
        p_id=p_id,
        hh_id=hh_id,
        alter=alter,
        p_id_elternteil_1=familie__p_id_elternteil_1,
        p_id_elternteil_2=familie__p_id_elternteil_2,
        xnp=xnp,
        backend=backend,
    )


@group_creation_function(leaf_name="fg_id", start_date="2023-01-01")
def fg_id_bürgergeld(
    bürgergeld__p_id_einstandspartner: IntColumn,
    p_id: IntColumn,
    hh_id: IntColumn,
    alter: IntColumn,
    familie__p_id_elternteil_1: IntColumn,
    familie__p_id_elternteil_2: IntColumn,
    xnp: ModuleType,
    backend: Literal["numpy", "jax"],
) -> IntColumn:
    """Familiengemeinschaft. Base unit for some transfers.

    Maximum of two generations, the relevant base unit for Bürgergeld / Arbeitslosengeld
    2, before excluding children who have enough income to fend for themselves.
    """
    return sgb_ii_fg_id_formula(
        p_id_einstandspartner=bürgergeld__p_id_einstandspartner,
        p_id=p_id,
        hh_id=hh_id,
        alter=alter,
        p_id_elternteil_1=familie__p_id_elternteil_1,
        p_id_elternteil_2=familie__p_id_elternteil_2,
        xnp=xnp,
        backend=backend,
    )


def sgb_ii_fg_id_formula(
    p_id_einstandspartner: IntColumn,
    p_id: IntColumn,
    hh_id: IntColumn,
    alter: IntColumn,
    p_id_elternteil_1: IntColumn,
    p_id_elternteil_2: IntColumn,
    xnp: ModuleType,
    backend: Literal["numpy", "jax"],
) -> IntColumn:
    """Formula to compute the FG ID for SGB II transfers"""
    n = xnp.max(p_id) + 1

    # Sort all arrays according to p_id to make the id equal location in array
    sorting = xnp.argsort(p_id)
    index_after_sort = xnp.argsort(xnp.arange(p_id.shape[0])[sorting])
    sorted_p_id = p_id[sorting]
    sorted_hh_id = hh_id[sorting]
    sorted_alter = alter[sorting]
    sorted_p_id_elternteil_1 = p_id_elternteil_1[sorting]
    sorted_p_id_elternteil_2 = p_id_elternteil_2[sorting]
    sorted_p_id_einstandspartner = p_id_einstandspartner[sorting]

    # Necessary because JAX's `isin` uses keyword `method` instead of NumPy's `kind`
    # See https://github.com/ttsim-dev/ttsim/pull/41#issuecomment-3180607171
    if backend == "jax":
        isin = functools.partial(xnp.isin, method="sort")
    else:
        isin = xnp.isin

    children = isin(sorted_p_id, sorted_p_id_elternteil_1) | isin(
        sorted_p_id, sorted_p_id_elternteil_2
    )

    # Assign the same fg_id to everybody who has an Einstandspartner,
    # otherwise create a new one from p_id
    out = xnp.where(
        sorted_p_id_einstandspartner < 0,
        sorted_p_id + sorted_p_id * n,
        xnp.maximum(sorted_p_id, sorted_p_id_einstandspartner)
        + xnp.minimum(sorted_p_id, sorted_p_id_einstandspartner) * n,
    )

    out = _assign_parents_fg_id(
        fg_id=out,
        p_id=sorted_p_id,
        p_id_elternteil_loc=sorted_p_id_elternteil_1,
        hh_id=sorted_hh_id,
        alter=sorted_alter,
        children=children,
        n=n,
        xnp=xnp,
    )
    out = _assign_parents_fg_id(
        fg_id=out,
        p_id=sorted_p_id,
        p_id_elternteil_loc=sorted_p_id_elternteil_2,
        hh_id=sorted_hh_id,
        alter=sorted_alter,
        children=children,
        n=n,
        xnp=xnp,
    )

    return out[index_after_sort]


def _assign_parents_fg_id(
    fg_id: IntColumn,
    p_id: IntColumn,
    p_id_elternteil_loc: IntColumn,
    hh_id: IntColumn,
    alter: IntColumn,
    children: IntColumn,
    n: IntColumn,
    xnp: ModuleType,
) -> IntColumn:
    """Return the fg_id of the child's parents."""
    # TODO(@MImmesberger): Remove hard-coded number
    # https://github.com/ttsim-dev/gettsim/issues/668

    return xnp.where(
        (p_id_elternteil_loc >= 0)
        * (fg_id == p_id + p_id * n)
        * (hh_id == hh_id[p_id_elternteil_loc])
        * (alter < 25)  # noqa: PLR2004
        * (1 - children),
        fg_id[p_id_elternteil_loc],
        fg_id,
    )


@group_creation_function(warn_msg_if_included=WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC)
def bg_id(
    fg_id: IntColumn,
    # xnp is needed to instantiate the GroupCreationFunction (because of `reorder_ids`)
    xnp: ModuleType,  # noqa: ARG001
) -> IntColumn:
    """Bedarfsgemeinschaft. Relevant unit for Bürgergeld / Arbeitslosengeld 2.

    Note: GETTSIM can compute the Bedarfsgemeinschaft endogenously for the most common
    household structures. That is, results will be correct if there is exactly one
    Familiengemeinschaft in one household and the Familiengemeinschaft coincides with
    the Bedarfsgemeinschaft and the wohngeldrechtlicher Teilhaushalt.

    If you plan to use more complex household and family structures (e.g. multiple
    families within a household, households consisting of more than one generation --
    with the exception of parents and their children up to the age of 25 --, or families
    with children who have enough income to fend for themselves, you can compute these
    IDs by following the instructions in this repo: [link eventually]. You can then pass
    the IDs obtained from there as input data to your main GETTSIM call.
    """
    return fg_id


@group_creation_function(leaf_name="eg_id", end_date="2022-12-31")
def eg_id_arbeitslosengeld_2(
    arbeitslosengeld_2__p_id_einstandspartner: IntColumn,
    p_id: IntColumn,
    xnp: ModuleType,
) -> IntColumn:
    """Einstandsgemeinschaft / Einstandspartner according to SGB II.

    A couple whose members are deemed to be responsible for each other.
    """
    return sgb_ii_eg_id_formula(
        p_id_einstandspartner=arbeitslosengeld_2__p_id_einstandspartner,
        p_id=p_id,
        xnp=xnp,
    )


@group_creation_function(leaf_name="eg_id", start_date="2023-01-01")
def eg_id_bürgergeld(
    bürgergeld__p_id_einstandspartner: IntColumn,
    p_id: IntColumn,
    xnp: ModuleType,
) -> IntColumn:
    """Einstandsgemeinschaft / Einstandspartner according to SGB II.

    A couple whose members are deemed to be responsible for each other.
    """
    return sgb_ii_eg_id_formula(
        p_id_einstandspartner=bürgergeld__p_id_einstandspartner,
        p_id=p_id,
        xnp=xnp,
    )


def sgb_ii_eg_id_formula(
    p_id_einstandspartner: IntColumn,
    p_id: IntColumn,
    xnp: ModuleType,
) -> IntColumn:
    """Einstandsgemeinschaft / Einstandspartner according to SGB II.

    A couple whose members are deemed to be responsible for each other.
    """
    n = xnp.max(p_id) + 1
    p_id_einstandspartner__or_own_p_id = xnp.where(
        p_id_einstandspartner < 0,
        p_id,
        p_id_einstandspartner,
    )

    return (
        xnp.maximum(p_id, p_id_einstandspartner__or_own_p_id)
        + xnp.minimum(p_id, p_id_einstandspartner__or_own_p_id) * n
    )


@group_creation_function(warn_msg_if_included=WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC)
def wthh_id(
    fg_id: IntColumn,
    xnp: ModuleType,  # noqa: ARG001
    # we need xnp for the ID reordering operation here
) -> IntColumn:
    """Wohngeldrechtlicher Teilhaushalt. The relevant unit for Wohngeld.

    Note: GETTSIM can compute the wohngeldrechtlicher Teilhaushalt endogenously for the
    most common household structures. That is, results will be correct if there is
    exactly one Familiengemeinschaft in one household and the Familiengemeinschaft
    coincides with the Bedarfsgemeinschaft and the wohngeldrechtlicher Teilhaushalt.

    If you plan to use more complex household and family structures (e.g. multiple
    families within a household, households consisting of more than one generation --
    with the exception of parents and their children up to the age of 25 --, or families
    with children who have enough income to fend for themselves, you can compute these
    IDs by following the instructions in this repo: [link eventually]. You can then pass
    the IDs obtained from there as input data to your main GETTSIM call.
    """
    return fg_id


@group_creation_function()
def sn_id(
    p_id: IntColumn,
    familie__p_id_ehepartner: IntColumn,
    einkommensteuer__gemeinsam_veranlagt: BoolColumn,
    xnp: ModuleType,
) -> IntColumn:
    """Steuernummer. Spouses filing taxes jointly or individuals."""
    n = xnp.max(p_id) + 1

    p_id_ehepartner_or_own_p_id = xnp.where(
        (familie__p_id_ehepartner >= 0) * (einkommensteuer__gemeinsam_veranlagt),
        familie__p_id_ehepartner,
        p_id,
    )

    return (
        xnp.maximum(p_id, p_id_ehepartner_or_own_p_id)
        + xnp.minimum(p_id, p_id_ehepartner_or_own_p_id) * n
    )
