"""Housing benefits (Wohngeld).

Wohngeld has priority over ALG2 if the recipients can cover their needs according to
SGB II when receiving Wohngeld.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

from gettsim.tt import (
    UNSET_UNIT,
    AggType,
    ConsecutiveIntLookupTableParamValue,
    InputOutputUnits,
    RoundingSpec,
    TTSIMUnit,
    agg_by_group_function,
    cast_ttsim_unit,
    get_consecutive_int_lookup_table_param_value,
    param_function,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType


@agg_by_group_function(agg_type=AggType.COUNT, unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH)
def anzahl_personen_wthh(wthh_id: int) -> int:
    pass


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_WTHH)
def betrag_m_wthh(
    anspruchshöhe_m_wthh: float,
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger: bool,
) -> float:
    """Housing benefit after priority checks (§12a SGB II)."""
    if vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger:
        return anspruchshöhe_m_wthh
    else:
        return 0.0


@policy_function(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_WTHH)
def anspruchshöhe_m_wthh(
    basisbetrag_m_wthh: float,
    grundsätzlich_anspruchsberechtigt_wthh: bool,
) -> float:
    """Housing benefit after eligibility checks."""
    if grundsätzlich_anspruchsberechtigt_wthh:
        return basisbetrag_m_wthh
    else:
        return 0.0


@policy_function(
    leaf_name="basisbetrag_m_wthh",
    end_date="2000-12-31",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.DM.PER_MONTH.PER_WTHH,
        base=1,
        direction="nearest",
        reference="§ 19 WoGG Abs.2 Anlage 3",
    ),
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_WTHH,
)
def basisbetrag_m_wthh_bis_2000(
    anzahl_personen_wthh: int,
    einkommen_m_wthh: float,
    miete_m_wthh: float,
    basisformel_params: BasisformelParamValues,
    xnp: ModuleType,
) -> float:
    """Housing benefit from the basis formula."""
    a = basisformel_params.a.look_up(anzahl_personen_wthh)
    b = basisformel_params.b.look_up(anzahl_personen_wthh)
    c = basisformel_params.c.look_up(anzahl_personen_wthh)
    anspruch_laut_abc_formel = xnp.maximum(
        0.0,
        basisformel_params.skalierungsfaktor
        * (
            miete_m_wthh
            - (
                (
                    a
                    + cast_ttsim_unit(b * miete_m_wthh, TTSIMUnit.DIMENSIONLESS)
                    + cast_ttsim_unit(c * einkommen_m_wthh, TTSIMUnit.DIMENSIONLESS)
                )
                * einkommen_m_wthh
            )
        ),
    )
    return xnp.minimum(miete_m_wthh, anspruch_laut_abc_formel)


@policy_function(
    leaf_name="basisbetrag_m_wthh",
    start_date="2001-01-01",
    end_date="2001-12-31",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.DM.PER_MONTH.PER_WTHH,
        base=1,
        direction="nearest",
        reference="§ 19 WoGG Abs.2 Anlage 3",
    ),
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_WTHH,
)
def basisbetrag_m_wthh_2001(
    anzahl_personen_wthh: int,
    einkommen_m_wthh: float,
    miete_m_wthh: float,
    basisformel_params: BasisformelParamValuesMitZusatzbetragNachHaushaltsgröße,
    xnp: ModuleType,
) -> float:
    """Housing benefit from the basis formula."""
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
            - (
                (
                    a
                    + cast_ttsim_unit(b * miete_m_wthh, TTSIMUnit.DIMENSIONLESS)
                    + cast_ttsim_unit(c * einkommen_m_wthh, TTSIMUnit.DIMENSIONLESS)
                )
                * einkommen_m_wthh
            )
        ),
    )
    return xnp.minimum(miete_m_wthh, anspruch_laut_abc_formel)


@policy_function(
    leaf_name="basisbetrag_m_wthh",
    start_date="2002-01-01",
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH.PER_WTHH,
        base=1,
        direction="nearest",
        reference="§ 19 WoGG Abs.2 Anlage 3",
    ),
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_WTHH,
)
def basisbetrag_m_wthh_ab_2002(
    anzahl_personen_wthh: int,
    einkommen_m_wthh: float,
    miete_m_wthh: float,
    basisformel_params: BasisformelParamValuesMitZusatzbetragNachHaushaltsgröße,
    xnp: ModuleType,
) -> float:
    """Housing benefit from the basis formula."""
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
            - (
                (
                    a
                    + cast_ttsim_unit(b * miete_m_wthh, TTSIMUnit.DIMENSIONLESS)
                    + cast_ttsim_unit(c * einkommen_m_wthh, TTSIMUnit.DIMENSIONLESS)
                )
                * einkommen_m_wthh
            )
        ),
    )
    return xnp.minimum(miete_m_wthh, anspruch_laut_abc_formel)


@dataclass(frozen=True)
class BasisformelParamValues:
    skalierungsfaktor: Annotated[float, TTSIMUnit.DIMENSIONLESS]
    a: Annotated[
        ConsecutiveIntLookupTableParamValue,
        InputOutputUnits(
            input_unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH,
            output_unit=TTSIMUnit.DIMENSIONLESS,
        ),
    ]
    b: Annotated[
        ConsecutiveIntLookupTableParamValue,
        InputOutputUnits(
            input_unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH,
            output_unit=TTSIMUnit.DIMENSIONLESS,
        ),
    ]
    c: Annotated[
        ConsecutiveIntLookupTableParamValue,
        InputOutputUnits(
            input_unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH,
            output_unit=TTSIMUnit.DIMENSIONLESS,
        ),
    ]


@param_function(end_date="2000-12-31", leaf_name="basisformel_params", unit=UNSET_UNIT)
def basisformel_params_bis_2000(
    skalierungsfaktor: float,
    koeffizienten_berechnungsformel: dict[int, dict[str, float]],
    max_anzahl_personen: dict[str, int],
    xnp: ModuleType,
) -> BasisformelParamValues:
    """Convert the parameters of the Wohngeld basis formula to a format that can be
    used by Numpy and Jax.

    Note: Not entirely sure that 'zusatzbetrag_pro_person_in_großen_haushalten_m' was
    not part of the pre-2001 parameters. At least it wasn't part of the 1993 novella,
    see BGBl I 1993 S. 183.
    """
    a = {i: v["a"] for i, v in koeffizienten_berechnungsformel.items()}
    b = {i: v["b"] for i, v in koeffizienten_berechnungsformel.items()}
    c = {i: v["c"] for i, v in koeffizienten_berechnungsformel.items()}
    max_normal = max_anzahl_personen["normale_berechnung"]
    for koeff in [a, b, c]:
        if max(koeff.keys()) != max_normal:  # pragma: no cover
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
    zusatzbetrag_nach_haushaltsgröße: Annotated[
        ConsecutiveIntLookupTableParamValue,
        InputOutputUnits(
            input_unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH,
            output_unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_WTHH,
        ),
    ]


@param_function(
    start_date="2001-01-01", leaf_name="basisformel_params", unit=UNSET_UNIT
)
def basisformel_params_ab_2001(
    skalierungsfaktor: float,
    koeffizienten_berechnungsformel: dict[int, dict[str, float]],
    max_anzahl_personen: dict[str, int],
    zusatzbetrag_pro_person_in_großen_haushalten_m: float,
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
        if max(koeff.keys()) != max_normal:  # pragma: no cover
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
        zusatzbetrag_nach_haushaltsgröße[i] = float(
            (i - max_normal) * zusatzbetrag_pro_person_in_großen_haushalten_m
        )

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
