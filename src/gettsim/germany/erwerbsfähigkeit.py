"""Eligibility functions for SGB II / SGB XII determination."""

from __future__ import annotations

from ttsim.unit_converters import m_to_y

from gettsim.tt import AggType, agg_by_group_function, policy_function


@policy_function()
def über_regelaltersgrenze(
    alter_monate: int,
    sozialversicherung__rente__altersrente__regelaltersrente__altersgrenze: float,
) -> bool:
    """Whether a person has reached the Regelaltersgrenze.

    Reference: § 7 Abs. 1 Satz 1 Nr. 1 SGB II, § 35 SGB VI
    """
    # Floating comparison may fail due to rounding errors if alter ==
    # Regelaltersgrenze. Hence, we add a number << 1 / 12 to the RHS.
    return m_to_y(alter_monate) > (
        sozialversicherung__rente__altersrente__regelaltersrente__altersgrenze + 0.00001
    )


@policy_function()
def ist_erwerbsfähig(
    alter: int,
    über_regelaltersgrenze: bool,
) -> bool:
    """Whether a person is erwerbsfähig according to § 7 Abs. 1 SGB II.

    A person is erwerbsfähig if they are at least 15 years old and have not reached the
    Regelaltersgrenze (§ 7a SGB II).
    """
    return alter >= 15 and not über_regelaltersgrenze  # noqa: PLR2004


@agg_by_group_function(agg_type=AggType.ANY)
def hat_erwerbsfähiges_mitglied_bg(ist_erwerbsfähig: bool, bg_id: int) -> bool:
    pass


@agg_by_group_function(agg_type=AggType.ANY)
def hat_person_über_regelaltersgrenze_bg(
    über_regelaltersgrenze: bool, bg_id: int
) -> bool:
    pass


@policy_function()
def ist_gemischte_bg(
    hat_erwerbsfähiges_mitglied_bg: bool,
    hat_person_über_regelaltersgrenze_bg: bool,
) -> bool:
    """Whether the BG is a gemischte Bedarfsgemeinschaft.

    A gemischte BG arises when at least one member is erwerbsfähig (SGB II) and at least
    one member has reached the Regelaltersgrenze (SGB XII).

    Reference: § 7 Abs. 3 SGB II, BSG B 14 AS 89/20 R (11.11.2021)
    """
    return hat_erwerbsfähiges_mitglied_bg and hat_person_über_regelaltersgrenze_bg
