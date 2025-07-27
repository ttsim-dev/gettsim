"""Housing benefits (Wohngeld).

Wohngeld has priority over ALG2 if the recipients can cover their needs according to
SGB II when receiving Wohngeld.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from gettsim.tt import (
    AggType,
    RoundingSpec,
    agg_by_group_function,
    get_consecutive_int_lookup_table_param_value,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType

    from gettsim.germany.param_types import ConsecutiveIntLookupTableParamValue


@agg_by_group_function(agg_type=AggType.COUNT)
def anzahl_personen_wthh(wthh_id: int) -> int:
    pass


@policy_function()
def betrag_m_wthh(
    anspruchshöhe_m_wthh: float,
    volljährige_alle_rentenbezieher_hh: bool,
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger: bool,
) -> float:
    """Housing benefit after wealth and priority checks."""
    # TODO (@MImmesberger): No interaction between Wohngeld/ALG2 and Grundsicherung im
    # Alter (SGB XII) is implemented yet. We assume for now that households with only
    # retirees are eligible for Grundsicherung im Alter but not for ALG2/Wohngeld. All
    # other households are not eligible for SGB XII, but SGB II / Wohngeld. Once this is
    # resolved, remove the `volljährige_alle_rentenbezieher_hh` condition.
    # https://github.com/ttsim-dev/gettsim/issues/703

    if not volljährige_alle_rentenbezieher_hh and (
        vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger
    ):
        out = anspruchshöhe_m_wthh
    else:
        out = 0.0

    return out


@policy_function(
    leaf_name="anspruchshöhe_m_wthh",
    end_date="2000-12-31",
    rounding_spec=RoundingSpec(
        base=1,
        direction="nearest",
        reference="§ 19 WoGG Abs.2 Anlage 3",
    ),
)
def anspruchshöhe_m_wthh_bis_2000(
    anzahl_personen_wthh: int,
    einkommen_m_wthh: float,
    miete_m_wthh: float,
    grundsätzlich_anspruchsberechtigt_wthh: bool,
    basisformel_params: BasisformelParamValues,
    xnp: ModuleType,
) -> float:
    """Housing benefit after wealth and income check."""
    a = basisformel_params.a.look_up(anzahl_personen_wthh)
    b = basisformel_params.b.look_up(anzahl_personen_wthh)
    c = basisformel_params.c.look_up(anzahl_personen_wthh)
    anspruch_laut_abc_formel = xnp.maximum(
        0.0,
        basisformel_params.skalierungsfaktor
        * (
            miete_m_wthh
            - ((a + (b * miete_m_wthh) + (c * einkommen_m_wthh)) * einkommen_m_wthh)
        ),
    )
    if grundsätzlich_anspruchsberechtigt_wthh:
        return xnp.minimum(miete_m_wthh, anspruch_laut_abc_formel)
    else:
        return 0.0


@policy_function(
    leaf_name="anspruchshöhe_m_wthh",
    start_date="2001-01-01",
    rounding_spec=RoundingSpec(
        base=1,
        direction="nearest",
        reference="§ 19 WoGG Abs.2 Anlage 3",
    ),
)
def anspruchshöhe_m_wthh_ab_2001(
    anzahl_personen_wthh: int,
    einkommen_m_wthh: float,
    miete_m_wthh: float,
    grundsätzlich_anspruchsberechtigt_wthh: bool,
    basisformel_params: BasisformelParamValuesMitZusatzbetragNachHaushaltsgröße,
    xnp: ModuleType,
) -> float:
    """Housing benefit after wealth and income check."""
    a = basisformel_params.a.look_up(anzahl_personen_wthh)
    b = basisformel_params.b.look_up(anzahl_personen_wthh)
    c = basisformel_params.c.look_up(anzahl_personen_wthh)
    zusatzbetrag_nach_haushaltsgröße = (
        basisformel_params.zusatzbetrag_nach_haushaltsgröße.look_up(
            anzahl_personen_wthh
        )
    )
    anspruch_laut_abc_formel = zusatzbetrag_nach_haushaltsgröße + xnp.maximum(
        0.0,
        basisformel_params.skalierungsfaktor
        * (
            miete_m_wthh
            - ((a + (b * miete_m_wthh) + (c * einkommen_m_wthh)) * einkommen_m_wthh)
        ),
    )
    if grundsätzlich_anspruchsberechtigt_wthh:
        return xnp.minimum(miete_m_wthh, anspruch_laut_abc_formel)
    else:
        return 0.0


@dataclass(frozen=True)
class BasisformelParamValues:
    skalierungsfaktor: float
    a: ConsecutiveIntLookupTableParamValue
    b: ConsecutiveIntLookupTableParamValue
    c: ConsecutiveIntLookupTableParamValue


@param_function(end_date="2000-12-31", leaf_name="basisformel_params")
def basisformel_params_bis_2000(
    skalierungsfaktor: float,
    koeffizienten_berechnungsformel: dict[int, dict[str, float]],
    max_anzahl_personen: dict[str, int],
    xnp: ModuleType,
) -> BasisformelParamValues:
    """Convert the parameters of the Wohngeld basis formula to a format that can be
    used by Numpy and Jax.

    Note: Not entirely sure that 'zusatzbetrag_pro_person_in_großen_haushalten' was not
    part of the pre-2001 parameters. At least it wasn't part of the 1993 novella, see
    BGBl I 1993 S. 183.
    """
    a = {i: v["a"] for i, v in koeffizienten_berechnungsformel.items()}
    b = {i: v["b"] for i, v in koeffizienten_berechnungsformel.items()}
    c = {i: v["c"] for i, v in koeffizienten_berechnungsformel.items()}
    max_normal = max_anzahl_personen["normale_berechnung"]
    for koeff in [a, b, c]:
        if max(koeff.keys()) != max_normal:
            raise ValueError(
                "The maximum number of persons for the normal calculation of the basic"
                "Wohngeld formula `max_anzahl_personen['normale_berechnung'] "
                f"(got: {max_normal}) must be the same as the maximum number of household "
                f"members in `koeffizienten_berechnungsformel` (got: {max(koeff.keys())})"
            )

    return BasisformelParamValues(
        skalierungsfaktor=skalierungsfaktor,
        a=get_consecutive_int_lookup_table_param_value(raw=a, xnp=xnp),
        b=get_consecutive_int_lookup_table_param_value(raw=b, xnp=xnp),
        c=get_consecutive_int_lookup_table_param_value(raw=c, xnp=xnp),
    )


@dataclass(frozen=True)
class BasisformelParamValuesMitZusatzbetragNachHaushaltsgröße(BasisformelParamValues):
    zusatzbetrag_nach_haushaltsgröße: ConsecutiveIntLookupTableParamValue


@param_function(start_date="2001-01-01", leaf_name="basisformel_params")
def basisformel_params_ab_2001(
    skalierungsfaktor: float,
    koeffizienten_berechnungsformel: dict[int, dict[str, float]],
    max_anzahl_personen: dict[str, int],
    zusatzbetrag_pro_person_in_großen_haushalten: float,
    xnp: ModuleType,
) -> BasisformelParamValuesMitZusatzbetragNachHaushaltsgröße:
    """Convert the parameters of the Wohngeld basis formula to a format that can be
    used by Numpy and Jax.
    """
    a = {i: v["a"] for i, v in koeffizienten_berechnungsformel.items()}
    b = {i: v["b"] for i, v in koeffizienten_berechnungsformel.items()}
    c = {i: v["c"] for i, v in koeffizienten_berechnungsformel.items()}
    max_normal = max_anzahl_personen["normale_berechnung"]
    for koeff in [a, b, c]:
        if max(koeff.keys()) != max_normal:
            raise ValueError(
                "The maximum number of persons for the normal calculation of the basic"
                "Wohngeld formula `max_anzahl_personen['normale_berechnung'] "
                f"(got: {max_normal}) must be the same as the maximum number of household "
                f"members in `koeffizienten_berechnungsformel` (got: {max(koeff.keys())})"
            )
    zusatzbetrag_nach_haushaltsgröße = dict.fromkeys(range(max_normal + 1), 0.0)
    for i in range(max_normal + 1, max_anzahl_personen["indizierung"] + 1):
        for koeff in [a, b, c]:
            koeff[i] = koeff[max_normal]
        zusatzbetrag_nach_haushaltsgröße[i] = (
            i - max_normal
        ) * zusatzbetrag_pro_person_in_großen_haushalten

    return BasisformelParamValuesMitZusatzbetragNachHaushaltsgröße(
        skalierungsfaktor=skalierungsfaktor,
        a=get_consecutive_int_lookup_table_param_value(raw=a, xnp=xnp),
        b=get_consecutive_int_lookup_table_param_value(raw=b, xnp=xnp),
        c=get_consecutive_int_lookup_table_param_value(raw=c, xnp=xnp),
        zusatzbetrag_nach_haushaltsgröße=get_consecutive_int_lookup_table_param_value(
            raw=zusatzbetrag_nach_haushaltsgröße,
            xnp=xnp,
        ),
    )
