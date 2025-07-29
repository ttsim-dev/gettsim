"""Test the new input_node_paths feature for GETTSIM DAG plotting."""

import pytest

from gettsim.plot.dag import tt


class TestInputNodePathsGETTSIM:
    """Test the input_node_paths feature in GETTSIM."""

    def test_basic_gettsim_plotting_still_works(self):
        """Ensure basic GETTSIM plotting functionality is unchanged."""
        fig = tt(
            policy_date_str="2025-01-01",
            title="Basic GETTSIM Test",
            include_params=False
        )
        assert fig is not None
        assert hasattr(fig, 'data')

    def test_gettsim_input_node_paths_parameter(self):
        """Test the new input_node_paths parameter in GETTSIM."""
        fig = tt(
            policy_date_str="2025-01-01",
            title="GETTSIM Test with input_node_paths",
            include_params=False,
            input_node_paths=[
                ("arbeitsl_geld_2", "regelsatz"),
                ("eink_st", "zu_verst_eink")
            ]
        )
        assert fig is not None
        assert hasattr(fig, 'data')

    def test_gettsim_multiple_input_node_paths(self):
        """Test GETTSIM with multiple input node paths."""
        fig = tt(
            policy_date_str="2025-01-01",
            title="GETTSIM Test with multiple inputs",
            include_params=False,
            input_node_paths=[
                ("arbeitsl_geld_2", "regelsatz"),
                ("eink_st", "zu_verst_eink"),
                ("soli_st", "soli_st_rate")
            ]
        )
        assert fig is not None
        assert hasattr(fig, 'data')

    def test_gettsim_empty_input_node_paths(self):
        """Test GETTSIM with empty input_node_paths list."""
        fig = tt(
            policy_date_str="2025-01-01",
            title="GETTSIM Test with empty input_node_paths",
            include_params=False,
            input_node_paths=[]
        )
        assert fig is not None
        assert hasattr(fig, 'data')
