"""Re-export of `ttsim.typing` aliases for use inside gettsim.

The runtime-resolvable aliases (column types, scalar types, User* boundary
types, simple-name aliases) are re-exported at module scope so beartype
can resolve string annotations on `gettsim.germany.*` policy functions at
call time.

Aliases that reference forward types (`ColumnObject`, `ParamFunction`,
…) and would cause an import cycle at runtime stay inside the
`TYPE_CHECKING` block. They are referenced only from string annotations
in modules that opt into `from __future__ import annotations`, and
beartype is never asked to resolve them on a checked signature.
"""

# TYPE_CHECKING-only re-exports for forward-reference aliases. These never
# appear as runtime-resolvable types under beartype; ty consumes the
# precise definitions and runtime code refers to them only via string
# annotations.
from typing import TYPE_CHECKING

from ttsim.typing import (
    BoolColumn,
    DashedISOString,
    FlatData,
    FloatColumn,
    IntColumn,
    NestedData,
    NestedStrings,
    NestedTargetDict,
    OrderedQNames,
    QNameData,
    QNameStrings,
    RawParamValue,
    ScalarBool,
    ScalarFloat,
    ScalarInt,
    UnorderedQNames,
    UserBoolColumn,
    UserFloatColumn,
    UserIntColumn,
    UserScalarBool,
    UserScalarFloat,
    UserScalarInt,
)

if TYPE_CHECKING:
    from ttsim.typing import (
        ColumnFunction,
        ColumnObject,
        FlatColumnObjectsParamFunctions,
        FlatInterfaceObjects,
        FlatOrigParamSpecs,
        FlatPolicyEnvironment,
        InterfaceFunction,
        InterfaceInput,
        NestedColumnObjectsParamFunctions,
        NestedInputsMapper,
        NestedInputStructureDict,
        NestedLookupDict,
        NestedParamObjects,
        NestedPolicyInputs,
        OrigParamSpec,
        ParamFunction,
        ParamObject,
        PolicyEnvironment,
        PolicyInput,
        QNameColumnObjects,
        SpecEnvWithoutTreeLogicAndWithDerivedFunctions,
        SpecEnvWithPartialledParamsAndScalars,
        SpecEnvWithProcessedParamsAndScalars,
    )

__all__ = [
    "BoolColumn",
    "DashedISOString",
    "FlatData",
    "FloatColumn",
    "IntColumn",
    "NestedData",
    "NestedStrings",
    "NestedTargetDict",
    "OrderedQNames",
    "QNameData",
    "QNameStrings",
    "RawParamValue",
    "ScalarBool",
    "ScalarFloat",
    "ScalarInt",
    "UnorderedQNames",
    "UserBoolColumn",
    "UserFloatColumn",
    "UserIntColumn",
    "UserScalarBool",
    "UserScalarFloat",
    "UserScalarInt",
]
