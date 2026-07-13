"""Hilfe zum Lebensunterhalt (SGB XII Kap. 3)."""

from gettsim.tt import Unit, param_function, policy_function


@policy_function(
    fail_msg_if_included="Hilfe zum Lebensunterhalt (SGB XII Kap. 3) is not implemented"
    " yet, see https://github.com/ttsim-dev/gettsim/issues/1153",
    unit=Unit.CURRENCY.PER_MONTH,
)
def betrag_m() -> float:
    """Hilfe zum Lebensunterhalt per person (§27 ff. SGB XII).

    Covers the livelihood of persons who are not eligible for Grundsicherung im Alter
    und bei Erwerbsminderung (SGB XII Kap. 4), in particular children whose parents
    receive Grundsicherung.

    # TODO (@MImmesberger): Implement Hilfe zum Lebensunterhalt.
    # https://github.com/ttsim-dev/gettsim/issues/1153
    """
    return 0.0  # pragma: no cover


@param_function(start_date="2005-01-01", unit=Unit.CURRENCY.PER_MONTH.PER_EG)
def überschusseinkommen_m_eg() -> float:
    """Excess HzL income flowing to the parent's Grundsicherung im Alter.

    Once Hilfe zum Lebensunterhalt is fully implemented, this should be computed from
    the child's ungedeckter Bedarf and einkommen_zur_verteilung.
    """
    # TODO (@MImmesberger): Transform to policy_function and compute from full HzL
    # Bedarf/Einkommen once implemented.
    # https://github.com/ttsim-dev/gettsim/issues/1153
    return 0.0
