"""Kindergeldübertrag for Bürgergeld."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    AggType,
    agg_by_p_id_function,
    join,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.typing import BoolColumn, FloatColumn, IntColumn


@agg_by_p_id_function(start_date="2023-01-01", agg_type=AggType.SUM)
def kindergeldübertrag_m(
    differenz_kindergeld_kindbedarf_m: float,
    kindergeld__p_id_empfänger: int,
    p_id: int,
) -> float:
    pass


@policy_function(
    start_date="2023-01-01",
    leaf_name="kindergeld_pro_kind_m",
)
def _mean_kindergeld_per_child_ohne_staffelung_m(
    kindergeld__anzahl_ansprüche: int,
    kindergeld__satz: float,
) -> float:
    """Kindergeld per child.

    Returns the (average) Kindergeld per child. Helper function for
    `kindergeld_zur_bedarfsdeckung_m`.

    """
    return kindergeld__satz if kindergeld__anzahl_ansprüche > 0 else 0.0


@policy_function(start_date="2023-01-01", vectorization_strategy="not_required")
def kindergeld_zur_bedarfsdeckung_m(
    kindergeld_pro_kind_m: FloatColumn,
    kindergeld__p_id_empfänger: IntColumn,
    p_id: IntColumn,
    xnp: ModuleType,
) -> FloatColumn:
    """Kindergeld that is used to cover the SGB II Regelbedarf of the child.

    Even though the Kindergeld is paid to the parent (see function
    :func:`kindergeld__betrag_m`), the child that gives rise to the Kindergeld claim is
    entitled to it to cover its needs (§ 11 Abs. 1 Satz 5 SGB II). The amount of
    Kindergeld for which the child is entitled to is the sum of the Kindergeld for all
    children divided by the amount of children. Hence, the age of the child (in
    comparison to siblings) does not matter.

    """
    return join(
        foreign_key=kindergeld__p_id_empfänger,
        primary_key=p_id,
        target=kindergeld_pro_kind_m,
        value_if_foreign_key_is_missing=0.0,
        xnp=xnp,
    )


@policy_function(start_date="2023-01-01")
def differenz_kindergeld_kindbedarf_m(
    regelbedarf_m_bg: float,
    nettoeinkommen_nach_abzug_freibetrag_m: float,
    wohngeld__anspruchshöhe_m_wthh: float,
    wohngeld__anzahl_personen_wthh: int,
    kindergeld_zur_bedarfsdeckung_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    in_anderer_bg_als_kindergeldempfänger: bool,
) -> float:
    """Kindergeld that is used to cover the needs (SGB II) of the parent.

    If a child does not need all of the Kindergeld to cover its own needs (SGB II), the
    remaining Kindergeld is used to cover the needs of the parent (§ 11 Abs. 1 Satz 5
    SGB II).

    Kindergeldübertrag (`kindergeldübertrag_m`) is obtained by aggregating this function
    to the parental level.
    """
    fehlbetrag = max(
        regelbedarf_m_bg
        - wohngeld__anspruchshöhe_m_wthh / wohngeld__anzahl_personen_wthh
        - nettoeinkommen_nach_abzug_freibetrag_m
        - unterhalt__tatsächlich_erhaltener_betrag_m
        - unterhaltsvorschuss__betrag_m,
        0.0,
    )
    # Bedarf not covered or same Bedarfsgemeinschaft as parents
    if (
        not in_anderer_bg_als_kindergeldempfänger
        or fehlbetrag > kindergeld_zur_bedarfsdeckung_m
    ):
        out = 0.0
    # Bedarf is covered
    else:
        out = kindergeld_zur_bedarfsdeckung_m - fehlbetrag
    return out


@policy_function(start_date="2023-01-01", vectorization_strategy="not_required")
def in_anderer_bg_als_kindergeldempfänger(
    p_id: IntColumn,
    kindergeld__p_id_empfänger: IntColumn,
    bg_id: IntColumn,
    xnp: ModuleType,
) -> BoolColumn:
    """True if the person is in a different Bedarfsgemeinschaft than the
    Kindergeldempfänger of that person.
    """
    bg_id_empfänger = join(
        foreign_key=kindergeld__p_id_empfänger,
        primary_key=p_id,
        target=bg_id,
        value_if_foreign_key_is_missing=-1,
        xnp=xnp,
    )
    return bg_id_empfänger != bg_id
