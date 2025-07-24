"""Input columns."""

from __future__ import annotations

from ttsim.tt_dag_elements import FKType, policy_input


@policy_input(start_date="2023-01-01")
def bezug_im_vorjahr() -> bool:
    """Person received Arbeitslosengeld 2 / Bürgergeld in the last 12 months."""


# TODO(@MImmesberger): Remove input variable eigenbedarf_gedeckt once
# Bedarfsgemeinschaften are fully endogenous
# https://github.com/ttsim-dev/gettsim/issues/763
@policy_input(start_date="2005-01-01")
def eigenbedarf_gedeckt() -> bool:
    """Needs according to SGB II are covered by own income."""


@policy_input(start_date="2005-01-01", foreign_key_type=FKType.MUST_NOT_POINT_TO_SELF)
def p_id_einstandspartner() -> int:
    """Identifier of Einstandspartner."""
