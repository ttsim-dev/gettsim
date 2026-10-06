"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def übergangsgeld_y() -> float:
    """Übergangsgeld received, net of repayments.

    Covers Übergangsgeld under any of the laws named in § 32b Abs. 1 Nr. 1 EStG.
    """


@policy_input(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def sonstige_leistungen_y() -> float:
    """All other benefits under § 32b Abs. 1 Nr. 1 EStG, net of repayments.

    Every benefit of the catalogue in force that has no column of its own, for example
    Arbeitslosenhilfe, Teilarbeitslosengeld, Qualifizierungsgeld, employer top-ups to
    Kurzarbeitergeld (§ 3 Nr. 28a EStG), Entschädigungen under the
    Infektionsschutzgesetz, and Anpassungsgelder.
    """
