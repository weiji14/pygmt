"""
Test pygmt.binstats.
"""

from pathlib import Path

import numpy.testing as npt
import pytest
from pygmt import binstats
from pygmt.enums import GridRegistration, GridType
from pygmt.helpers import GMTTempFile


def test_binstats_outgrid():
    """
    Test binstats with a set outgrid.
    """
    with GMTTempFile(suffix=".nc") as tmpfile:
        result = binstats(
            data="@capitals.gmt",
            outgrid=tmpfile.name,
            spacing=5,
            statistic="z",
            search_radius="1000k",
            aspatial="2=population",
            region="g",
        )
        assert result is None  # return value is None
        assert Path(tmpfile.name).stat().st_size > 0  # check that outgrid exists


@pytest.mark.benchmark
def test_binstats_no_outgrid():
    """
    Test binstats with no set outgrid.
    """
    temp_grid = binstats(
        data="@capitals.gmt",
        spacing=5,
        statistic="z",
        search_radius="1000k",
        aspatial="2=population",
        region="g",
    )
    assert temp_grid.dims == ("y", "x")
    assert temp_grid.gmt.gtype is GridType.CARTESIAN
    assert temp_grid.gmt.registration is GridRegistration.GRIDLINE
    npt.assert_allclose(temp_grid.max(), 35971536)
    npt.assert_allclose(temp_grid.min(), 53)
    npt.assert_allclose(temp_grid.median(), 1232714.5)
    npt.assert_allclose(temp_grid.mean(), 4227489)
