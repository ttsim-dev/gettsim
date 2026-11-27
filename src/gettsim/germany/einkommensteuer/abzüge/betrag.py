"""Tax allowances."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR.PER_SN)
def betrag_y_sn(
    sonderausgaben_y_sn: float,
    vorsorgeaufwendungen_y_sn: float,
    betrag_ind_y_sn: float,
) -> float:
    """Calculate total allowances on Steuernummer level.

    Reference: § 2 Abs. 4 EStG idF B. v. 16.04.1997 BGBl. I S. 821
    """
    return sonderausgaben_y_sn + vorsorgeaufwendungen_y_sn + betrag_ind_y_sn


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def betrag_ind_y(
    pauschbetrag_behinderung_y: float,
    alleinerziehend_betrag_y: float,
    altersfreibetrag_y: float,
) -> float:
    """Sum up all tax-deductible allowances applicable at the individual level.

    Reference:
        - § 24a Satz 1 EStG idF Art. 1 G. v. 19.12.2000 BGBl. I S. 1790
        - § 32 Abs. 7 Satz 1 EStG idF Art. 1 G. v. 16.08.2001 BGBl. I S. 2074
        - § 33b Abs. 3 Satz 2 EStG idF Art. 1 G. v. 19.12.2000 BGBl. I S. 1790
    """

    return pauschbetrag_behinderung_y + alleinerziehend_betrag_y + altersfreibetrag_y
