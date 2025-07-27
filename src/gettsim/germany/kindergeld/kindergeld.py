"""Basic child allowance (Kindergeld)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    AggType,
    ConsecutiveIntLookupTableParamValue,
    agg_by_p_id_function,
    get_consecutive_int_lookup_table_param_value,
    join,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.typing import BoolColumn, IntColumn


@agg_by_p_id_function(agg_type=AggType.SUM)
def anzahl_ansprüche(
    ist_leistungsbegründendes_kind: bool,
    p_id_empfänger: int,
    p_id: int,
) -> int:
    pass


@policy_function(start_date="2023-01-01", leaf_name="betrag_m")
def betrag_ohne_staffelung_m(
    anzahl_ansprüche: int,
    satz: float,
) -> float:
    """Sum of Kindergeld for eligible children.

    Kindergeld claim is the same for each child, i.e. increases linearly with the number
    of children.

    """
    return satz * anzahl_ansprüche


@policy_function(end_date="2022-12-31", leaf_name="betrag_m")
def betrag_gestaffelt_m(
    anzahl_ansprüche: int,
    satz_nach_anzahl_kinder: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Sum of Kindergeld that parents receive for their children.

    Kindergeld claim for each child depends on the number of children Kindergeld is
    being claimed for.

    """
    return satz_nach_anzahl_kinder.look_up(anzahl_ansprüche)


@policy_function(
    end_date="1995-12-31",
    leaf_name="ist_leistungsbegründendes_kind",
    fail_msg_if_included="Kindergeld eligibility is not implemented prior to 1996.",
)
def leistungsbegründendes_kind_nach_lohn_bis_1995() -> bool:
    pass


@policy_function(
    start_date="1996-01-01",
    end_date="2011-12-31",
    leaf_name="ist_leistungsbegründendes_kind",
)
def leistungsbegründendes_kind_nach_lohn(
    alter: int,
    in_ausbildung: bool,
    einnahmen__bruttolohn_y: float,
    altersgrenze: dict[str, int],
    maximales_einkommen_des_kindes: float,
) -> bool:
    """Child gives rise to a Kindergeld claim.

    Until 2011, there was an income ceiling for children
    returns a boolean variable whether a specific person is a child eligible for
    child benefit

    """
    return (alter < altersgrenze["ohne_bedingungen"]) or (
        (alter < altersgrenze["mit_bedingungen"])
        and in_ausbildung
        and (einnahmen__bruttolohn_y <= maximales_einkommen_des_kindes)
    )


@policy_function(
    start_date="2012-01-01",
    leaf_name="ist_leistungsbegründendes_kind",
)
def leistungsbegründendes_kind_nach_stunden(
    alter: int,
    in_ausbildung: bool,
    arbeitsstunden_w: float,
    altersgrenze: dict[str, int],
    maximale_arbeitsstunden_des_kindes: float,
) -> bool:
    """Child gives rise to a Kindergeld claim.

    The current eligibility rule is, that kids must not work more than 20
    hour and are below 25.

    """
    return (alter < altersgrenze["ohne_bedingungen"]) or (
        (alter < altersgrenze["mit_bedingungen"])
        and in_ausbildung
        and (arbeitsstunden_w <= maximale_arbeitsstunden_des_kindes)
    )


@policy_function(end_date="2015-12-31")
def kind_bis_10_mit_kindergeld(
    alter: int,
    ist_leistungsbegründendes_kind: bool,
) -> bool:
    """Child under the age of 11 and eligible for Kindergeld."""
    return ist_leistungsbegründendes_kind and (alter <= 10)  # noqa: PLR2004


@policy_function(vectorization_strategy="not_required")
def gleiche_fg_wie_empfänger(
    p_id: IntColumn,
    p_id_empfänger: IntColumn,
    fg_id: IntColumn,
    xnp: ModuleType,
) -> BoolColumn:
    """The child's Kindergeldempfänger is in the same Familiengemeinschaft."""
    fg_id_kindergeldempfänger = join(
        foreign_key=p_id_empfänger,
        primary_key=p_id,
        target=fg_id,
        value_if_foreign_key_is_missing=-1,
        xnp=xnp,
    )

    return fg_id_kindergeldempfänger == fg_id


@param_function(end_date="2022-12-31")
def satz_nach_anzahl_kinder(
    satz_gestaffelt: dict[int, float],
    xnp: ModuleType,
) -> ConsecutiveIntLookupTableParamValue:
    """Convert the Kindergeld-Satz by child to the amount of Kindergeld by number of
    children.
    """
    max_num_children = 30
    max_num_children_in_spec = max(satz_gestaffelt.keys())
    base_spec = {
        k: sum(satz_gestaffelt[i] for i in range(1, k + 1))
        for k in range(1, max_num_children_in_spec + 1)
    }
    extended_spec = {
        k: base_spec[max_num_children_in_spec]
        + satz_gestaffelt[max_num_children_in_spec] * (k - max_num_children_in_spec)
        for k in range(max_num_children_in_spec + 1, max_num_children)
    }
    return get_consecutive_int_lookup_table_param_value(
        raw={0: 0.0, **base_spec, **extended_spec},
        xnp=xnp,
    )
