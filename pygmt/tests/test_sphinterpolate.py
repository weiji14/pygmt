"""
Test pygmt.sphinterpolate.
"""

from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest
from packaging.version import Version
from pygmt import sphinterpolate
from pygmt.datasets import load_sample_data
from pygmt.enums import GridRegistration, GridType
from pygmt.helpers import GMTTempFile


@pytest.fixture(scope="module", name="mars")
def fixture_mars():
    """
    Load the table data for the shape of Mars.
    """
    return load_sample_data(name="mars_shape")


def test_sphinterpolate_outgrid(mars):
    """
    Test sphinterpolate with a set outgrid.
    """
    with GMTTempFile(suffix=".nc") as tmpfile:
        result = sphinterpolate(data=mars, outgrid=tmpfile.name, spacing=1, region="g")
        assert result is None  # return value is None
        assert Path(tmpfile.name).stat().st_size > 0  # check that outgrid exists


@pytest.mark.benchmark
def test_sphinterpolate_no_outgrid(mars):
    """
    Test sphinterpolate with no set outgrid.
    """
    temp_grid = sphinterpolate(data=mars, spacing=1, region="g")
    assert temp_grid.dims == ("lat", "lon")
    assert temp_grid.gmt.gtype is GridType.GEOGRAPHIC
    assert temp_grid.gmt.registration is GridRegistration.GRIDLINE
    npt.assert_allclose(temp_grid.max(), 14628.144)
    npt.assert_allclose(temp_grid.min(), -6908.1987)
    npt.assert_allclose(temp_grid.median(), 118.96849)
    # TODO(NumPy>=2.3.0): Remove the numpy version check.
    mean = 272.60568 if Version(np.__version__) >= Version("2.3.0dev") else 272.60593
    npt.assert_allclose(temp_grid.mean(), mean)
