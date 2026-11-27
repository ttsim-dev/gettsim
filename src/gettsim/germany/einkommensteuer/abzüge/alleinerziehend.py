"""Tax allowances for single parents."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, cast_ttsim_unit, policy_function


@policy_function(
    end_date="2014-12-31",
    leaf_name="alleinerziehend_betrag_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def alleinerziehend_betrag_y_pauschal(
    familie__alleinerziehend_sn: bool,
    alleinerziehendenfreibetrag_basis_y: float,
) -> float:
    """Calculate tax deduction allowance for single parents until 2014.

    Until 2003, the Haushaltsfreibetrag (§ 32 Abs. 7 EStG); from 2004, the
    Entlastungsbetrag für Alleinerziehende (§ 24b EStG).

    Reference:
        - § 32 Abs. 7 Satz 1 EStG idF Art. 1 G. v. 16.08.2001 BGBl. I S. 2074
        - § 24b Abs. 1 EStG idF Art. 9 G. v. 29.12.2003 BGBl. I S. 3076
    """
    return alleinerziehendenfreibetrag_basis_y if familie__alleinerziehend_sn else 0.0


@policy_function(
    start_date="2015-01-01",
    leaf_name="alleinerziehend_betrag_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def alleinerziehend_betrag_y_nach_kinderzahl(
    familie__alleinerziehend_sn: bool,
    kindergeld__anzahl_ansprüche_sn: int,
    alleinerziehendenfreibetrag_basis_y: float,
    alleinerziehendenfreibetrag_zusatz_pro_kind_y: float,
) -> float:
    """Calculate tax deduction allowance for single parents since 2015.

    Reference: § 24b Abs. 2 EStG idF Art. 1 G. v. 16.07.2015 BGBl. I S. 1202
    """

    if familie__alleinerziehend_sn:
        out = (
            alleinerziehendenfreibetrag_basis_y
            + (
                cast_ttsim_unit(
                    kindergeld__anzahl_ansprüche_sn, unit=TTSIMUnit.DIMENSIONLESS
                )
                - 1
            )
            * alleinerziehendenfreibetrag_zusatz_pro_kind_y
        )
    else:
        out = 0.0

    return out
