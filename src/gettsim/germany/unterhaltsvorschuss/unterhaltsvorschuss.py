"""Advance alimony payments (Unterhaltsvorschuss)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.germany.param_types import Altersgrenzen, SatzMitAltersgrenzen
from gettsim.tt import (
    AggType,
    ConsecutiveIntLookupTableParamValue,
    RawParam,
    RoundingSpec,
    agg_by_p_id_function,
    join,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.typing import BoolColumn, IntColumn


@agg_by_p_id_function(agg_type=AggType.SUM)
def an_elternteil_auszuzahlender_betrag_m(
    betrag_m: float,
    kindergeld__p_id_empfänger: int,
    p_id: int,
) -> float:
    pass


@policy_function(
    start_date="2009-01-01",
    rounding_spec=RoundingSpec(
        base=1,
        direction="up",
        reference="§ 9 Abs. 3 UhVorschG",
    ),
)
def betrag_m(
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    anspruchshöhe_m: float,
    elternteil_alleinerziehend: bool,
) -> float:
    """Advance alimony payments (Unterhaltsvorschuss) on child level after deducting
    alimonies.

    Single Parents get alimony payments for themselves and for their child from the ex
    partner. If the ex partner is not able to pay the child alimony, the government pays
    the child alimony to the mother (or the father, if he has the kids).

    According to §1 Abs.1 Nr.3 UhVorschG those single parents are entitled to
    advance alimony payments, who do not or not regularly receive child alimony
    payments or orphans' benefits (Waisenbezüge) in at least the amount specified in
    §2 Abs.1 and 2 UhVorschG. The child alimonay payment paid by the other parent
    is credited against the amount of the advance alimony payments
    (§2 Abs.3 Nr.1 UhVorschG).

    The amount is specified in §1612a BGB and, ultimately, in
    Mindestunterhaltsverordnung.
    """
    if elternteil_alleinerziehend:
        out = max(anspruchshöhe_m - unterhalt__tatsächlich_erhaltener_betrag_m, 0.0)
    else:
        out = 0.0

    return out


@policy_function(vectorization_strategy="not_required")
def elternteil_alleinerziehend(
    kindergeld__p_id_empfänger: IntColumn,
    p_id: IntColumn,
    familie__alleinerziehend: BoolColumn,
    xnp: ModuleType,
) -> BoolColumn:
    """Check if parent that receives Kindergeld is a single parent.

    Only single parents receive Kindergeld.
    """
    return join(
        foreign_key=kindergeld__p_id_empfänger,
        primary_key=p_id,
        target=familie__alleinerziehend,
        value_if_foreign_key_is_missing=False,
        xnp=xnp,
    )


@policy_function(
    end_date="2008-12-31",
    leaf_name="betrag_m",
    rounding_spec=RoundingSpec(
        base=1,
        direction="down",
        reference="§ 9 Abs. 3 UhVorschG",
    ),
    fail_msg_if_included="Unterhaltsvorschuss is not implemented prior to 2009.",
)
def betrag_m_bis_2008() -> float:
    pass


@param_function(start_date="2023-01-01", leaf_name="kindergeld_erstes_kind_m")
def kindergeld_erstes_kind_ohne_staffelung_m(
    kindergeld__satz: float,
) -> float:
    """Kindergeld for first child when Kindergeld does not depend on number of children."""
    return kindergeld__satz


@param_function(end_date="2022-12-31", leaf_name="kindergeld_erstes_kind_m")
def kindergeld_erstes_kind_gestaffelt_m(
    kindergeld__satz_nach_anzahl_kinder: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Kindergeld for first child when Kindergeld depends on number of children."""
    return kindergeld__satz_nach_anzahl_kinder.look_up(1)


@policy_function(
    start_date="2009-01-01",
    end_date="2014-12-31",
    leaf_name="anspruchshöhe_m",
)
def unterhaltsvorschuss_anspruch_m_2009_bis_2014(
    alter: int,
    kindergeld_erstes_kind_m: float,
    berechtigte_altersgruppen: dict[str, Altersgrenzen],
    faktor_jüngste_altersgruppe: float,
    einkommensteuer__parameter_kinderfreibetrag: dict[str, float],
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    Relevant parameter is directly 'steuerfrei zu stellenden sächlichen Existenzminimum
    des minderjährigen Kindes' § 1612a (1). Modeling relative to the child allowance for
    this. The amout for the lower age group is defined relative to the middle age group
    with a factor of 0.87.

    Rule was in priciple also active for 2015 but has been overwritten by an
    Anwendungsvorschrift as Kinderfreibetrag and Kindergeld changed on July 2015.

    """
    # TODO(@MImmesberger): Remove explicit parameter conversion.
    # https://github.com/ttsim-dev/gettsim/issues/575
    sächliches_existenzmininmum = einkommensteuer__parameter_kinderfreibetrag[
        "sächliches_existenzminimum"
    ]

    if (
        berechtigte_altersgruppen["kleinkind"].min_alter <= alter
        and alter <= berechtigte_altersgruppen["kleinkind"].max_alter
    ):
        out = (
            faktor_jüngste_altersgruppe * (2 * sächliches_existenzmininmum / 12)
            - kindergeld_erstes_kind_m
        )
    elif (
        berechtigte_altersgruppen["schulkind"].min_alter <= alter
        and alter <= berechtigte_altersgruppen["schulkind"].max_alter
    ):
        out = 2 * sächliches_existenzmininmum / 12 - kindergeld_erstes_kind_m
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2015-01-01",
    end_date="2015-12-31",
    leaf_name="anspruchshöhe_m",
)
def anspruchshöhe_m_anwendungsvors(
    alter: int,
    berechtigte_altersgruppen: dict[str, Altersgrenzen],
    unterhaltsvorschuss_nach_anwendungsvorschrift: dict[str, float],
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    Rule anspruchshöhe_m_2009_bis_2014 was in priciple also active for
    2015 but has been overwritten by an Anwendungsvorschrift as Kinderfreibetrag and
    Kindergeld changed in July 2015.
    """
    if (
        berechtigte_altersgruppen["kleinkind"].min_alter <= alter
        and alter <= berechtigte_altersgruppen["kleinkind"].max_alter
    ):
        out = unterhaltsvorschuss_nach_anwendungsvorschrift["kleinkind"]
    elif (
        berechtigte_altersgruppen["schulkind"].min_alter <= alter
        and alter <= berechtigte_altersgruppen["schulkind"].max_alter
    ):
        out = unterhaltsvorschuss_nach_anwendungsvorschrift["schulkind"]
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2016-01-01",
    end_date="2017-06-30",
    leaf_name="anspruchshöhe_m",
)
def anspruchshöhe_m_2016_bis_2017_06(
    alter: int,
    kindergeld_erstes_kind_m: float,
    mindestunterhalt_nach_alter: dict[str, SatzMitAltersgrenzen],
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    § 2 Unterhaltsvorschussgesetz refers to Section § 1612a BGB. There still is the
    reference to 'steuerfrei zu stellenden sächlichen Existenzminimum des minderjährigen
    Kindes' (§ 1612a (1)) as well as a Verordnungsermächtigung (§ 1612a (4)). The § 1
    Mindesunterhaltsverordnung applies fixed amounts and no relative definition as
    before.
    """
    if (
        mindestunterhalt_nach_alter["kleinkind"].altersgrenzen.min_alter <= alter
        and alter <= mindestunterhalt_nach_alter["kleinkind"].altersgrenzen.max_alter
    ):
        out = mindestunterhalt_nach_alter["kleinkind"].satz - kindergeld_erstes_kind_m
    elif (
        mindestunterhalt_nach_alter["schulkind"].altersgrenzen.min_alter <= alter
        and alter <= mindestunterhalt_nach_alter["schulkind"].altersgrenzen.max_alter
    ):
        out = mindestunterhalt_nach_alter["schulkind"].satz - kindergeld_erstes_kind_m
    else:
        out = 0.0

    return out


@policy_function(start_date="2017-07-01", leaf_name="anspruchshöhe_m")
def anspruchshöhe_m_ab_2017_07(
    alter: int,
    elternteil_mindesteinkommen_erreicht: bool,
    kindergeld_erstes_kind_m: float,
    mindestunterhalt_nach_alter: dict[str, SatzMitAltersgrenzen],
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    Introduction of a minimum income threshold if child is older than some threshold and
    third age group (12-17) via Artikel 23 G. v. 14.08.2017 BGBl. I S. 3122.
    """
    if (
        mindestunterhalt_nach_alter["kleinkind"].altersgrenzen.min_alter <= alter
        and alter <= mindestunterhalt_nach_alter["kleinkind"].altersgrenzen.max_alter
    ):
        out = mindestunterhalt_nach_alter["kleinkind"].satz - kindergeld_erstes_kind_m
    elif (
        mindestunterhalt_nach_alter["schulkind"].altersgrenzen.min_alter <= alter
        and alter <= mindestunterhalt_nach_alter["schulkind"].altersgrenzen.max_alter
    ):
        out = mindestunterhalt_nach_alter["schulkind"].satz - kindergeld_erstes_kind_m
    elif (
        mindestunterhalt_nach_alter["jugendliche"].altersgrenzen.min_alter <= alter
        and alter <= mindestunterhalt_nach_alter["jugendliche"].altersgrenzen.max_alter
        and elternteil_mindesteinkommen_erreicht
    ):
        out = mindestunterhalt_nach_alter["jugendliche"].satz - kindergeld_erstes_kind_m
    else:
        out = 0.0

    return out


@policy_function(start_date="2017-07-01", vectorization_strategy="not_required")
def elternteil_mindesteinkommen_erreicht(
    kindergeld__p_id_empfänger: IntColumn,
    p_id: IntColumn,
    mindesteinkommen_erreicht: BoolColumn,
    xnp: ModuleType,
) -> BoolColumn:
    """Income of Unterhaltsvorschuss recipient above threshold (this variable is
    defined on child level).
    """
    return join(
        foreign_key=kindergeld__p_id_empfänger,
        primary_key=p_id,
        target=mindesteinkommen_erreicht,
        value_if_foreign_key_is_missing=False,
        xnp=xnp,
    )


@policy_function(start_date="2017-07-01")
def mindesteinkommen_erreicht(
    einkommen_m: float,
    mindesteinkommen: float,
) -> bool:
    """Check if income is above the threshold for advance alimony payments."""
    return einkommen_m >= mindesteinkommen


@policy_function(start_date="2017-07-01")
def einkommen_m(
    einnahmen__bruttolohn_m: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    einnahmen__kapitalerträge_m: float,
    einnahmen__renten__gesetzliche_m: float,
    einnahmen__renten__sonstige_private_vorsorge_m: float,
    einnahmen__renten__geförderte_private_vorsorge_m: float,
    einnahmen__renten__betriebliche_altersvorsorge_m: float,
    einkommensteuer__einkünfte__sonstige__alle_weiteren_m: float,
    sozialversicherung__arbeitslosen__betrag_m: float,
) -> float:
    """Calculate relevant income for advance on alimony payment."""
    return (
        einnahmen__bruttolohn_m
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
        + einnahmen__kapitalerträge_m
        + einnahmen__renten__gesetzliche_m
        + einnahmen__renten__sonstige_private_vorsorge_m
        + einnahmen__renten__geförderte_private_vorsorge_m
        + einnahmen__renten__betriebliche_altersvorsorge_m
        + einkommensteuer__einkünfte__sonstige__alle_weiteren_m
        + sozialversicherung__arbeitslosen__betrag_m
    )


@param_function(start_date="2008-01-01", end_date="2017-06-30")
def berechtigte_altersgruppen(
    raw_berechtigte_altersgruppen: RawParam,
) -> dict[str, Altersgrenzen]:
    return {
        "kleinkind": Altersgrenzen(
            min_alter=raw_berechtigte_altersgruppen["kleinkind"]["min_alter"],
            max_alter=raw_berechtigte_altersgruppen["kleinkind"]["max_alter"],
        ),
        "schulkind": Altersgrenzen(
            min_alter=raw_berechtigte_altersgruppen["schulkind"]["min_alter"],
            max_alter=raw_berechtigte_altersgruppen["schulkind"]["max_alter"],
        ),
    }


@param_function(start_date="2016-01-01")
def mindestunterhalt_nach_alter(
    raw_mindestunterhalt: RawParam,
) -> dict[str, SatzMitAltersgrenzen]:
    kleinkind = SatzMitAltersgrenzen(
        satz=raw_mindestunterhalt["kleinkind"]["satz"],
        altersgrenzen=Altersgrenzen(
            min_alter=raw_mindestunterhalt["kleinkind"]["min_alter"],
            max_alter=raw_mindestunterhalt["kleinkind"]["max_alter"],
        ),
    )
    schulkind = SatzMitAltersgrenzen(
        satz=raw_mindestunterhalt["schulkind"]["satz"],
        altersgrenzen=Altersgrenzen(
            min_alter=raw_mindestunterhalt["schulkind"]["min_alter"],
            max_alter=raw_mindestunterhalt["schulkind"]["max_alter"],
        ),
    )
    jugendliche = SatzMitAltersgrenzen(
        satz=raw_mindestunterhalt["jugendliche"]["satz"],
        altersgrenzen=Altersgrenzen(
            min_alter=raw_mindestunterhalt["jugendliche"]["min_alter"],
            max_alter=raw_mindestunterhalt["jugendliche"]["max_alter"],
        ),
    )
    return {
        "kleinkind": kleinkind,
        "schulkind": schulkind,
        "jugendliche": jugendliche,
    }
