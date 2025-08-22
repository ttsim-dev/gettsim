"""Test that GETTSIM and TTSIM interfaces stay in sync."""

from __future__ import annotations

import inspect

import ttsim

from gettsim import main as gettsim_main


def test_parameters_missing_in_gettsim():
    gettsim_sig = inspect.signature(gettsim_main)
    gettsim_params = set(gettsim_sig.parameters.keys())

    ttsim_sig = inspect.signature(ttsim.main)
    ttsim_params = set(ttsim_sig.parameters.keys())

    missing_params = ttsim_params - gettsim_params
    assert not missing_params, (
        "GETTSIM main function is missing the following parameters that exist in "
        f"TTSIM:\n\n{missing_params}.\n\n"
        "This indicates an interface drift that needs to be fixed."
    )


def test_too_many_parameters_in_gettsim():
    gettsim_sig = inspect.signature(gettsim_main)
    gettsim_params = set(gettsim_sig.parameters.keys())

    ttsim_sig = inspect.signature(ttsim.main)
    ttsim_params = set(ttsim_sig.parameters.keys())

    extra_params = gettsim_params - ttsim_params
    assert not extra_params, (
        "GETTSIM main function has the following parameters that do not exist in "
        f"TTSIM:\n\n{extra_params}.\n\n"
        "This indicates an interface drift that needs to be fixed."
    )
