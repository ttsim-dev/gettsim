"""`BeartypeConf` instances for gettsim's perimeter and internal claws.

gettsim does not add user-facing constructors beyond those that ttsim
already provides; every per-component conf re-exported here points at a
`ttsim.exceptions.*` class. Decorators in gettsim's policy modules can
import these by name without taking a direct dependency on the backend
package path.

`INTERNAL_CONF` is the conf used by the package-wide claw registered in
`gettsim/__init__.py`. It matches ttsim's `INTERNAL_CONF`: violations
inside gettsim modules surface as beartype's own
`BeartypeCallHintViolation`, not as a project exception.
"""

from ttsim._beartype_conf import (
    AGGREGATION_CONF,
    ENTRY_POINT_CONF,
    GROUP_CREATION_CONF,
    INPUT_DATA_CONF,
    INTERNAL_CONF,
    PARAM_FUNCTION_CONF,
    POLICY_FUNCTION_CONF,
    POLICY_INPUT_CONF,
    ROUNDING_SPEC_CONF,
    TT_TARGETS_CONF,
    project_conf,
)

__all__ = [
    "AGGREGATION_CONF",
    "ENTRY_POINT_CONF",
    "GROUP_CREATION_CONF",
    "INPUT_DATA_CONF",
    "INTERNAL_CONF",
    "PARAM_FUNCTION_CONF",
    "POLICY_FUNCTION_CONF",
    "POLICY_INPUT_CONF",
    "ROUNDING_SPEC_CONF",
    "TT_TARGETS_CONF",
    "project_conf",
]
