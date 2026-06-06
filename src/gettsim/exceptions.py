"""Exception hierarchy for gettsim.

gettsim reuses the `ttsim.exceptions` vocabulary; there is no
gettsim-specific base class. Every exception raised by gettsim — whether
from the German policy code in `gettsim.germany` or from a beartype
violation re-raised at a user-facing boundary — is a subclass of
`ttsim.exceptions.TTSIMError`.

Importing from `gettsim.exceptions` rather than `ttsim.exceptions` keeps
gettsim callers from depending on the backend package's import path. The
two names refer to the same classes.
"""

from ttsim.exceptions import (
    AggregationDefinitionError,
    EntryPointError,
    GroupCreationDefinitionError,
    InputDataError,
    ParamFunctionDefinitionError,
    PolicyFunctionDefinitionError,
    PolicyInputDefinitionError,
    RoundingSpecError,
    TTSIMError,
    TTTargetsError,
)

__all__ = [
    "AggregationDefinitionError",
    "EntryPointError",
    "GroupCreationDefinitionError",
    "InputDataError",
    "ParamFunctionDefinitionError",
    "PolicyFunctionDefinitionError",
    "PolicyInputDefinitionError",
    "RoundingSpecError",
    "TTSIMError",
    "TTTargetsError",
]
