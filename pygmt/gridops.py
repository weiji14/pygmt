"""
GMT modules for grid operations.
"""

import xarray as xr
from pygmt.clib import Session
from pygmt.exceptions import GMTInvalidInput
from pygmt.helpers import (
    GMTTempFile,
    build_arg_string,
    data_kind,
    dummy_context,
    fmt_docstring,
    kwargs_to_strings,
    use_alias,
)


@fmt_docstring
@use_alias(
    G="outgrid",
    R="region",
    J="projection",
    N="extend",
    S="circ_subregion",
    V="verbose",
    Z="z_subregion",
)
@kwargs_to_strings(R="sequence")
def grdcut(grid, **kwargs):
    """
    Extract subregion from a grid.

    Produce a new *outgrid* file which is a subregion of *grid*. The
    subregion is specified with *region*; the specified range must not exceed
    the range of *grid* (but see *extend*). If in doubt, run
    :meth:`pygmt.grdinfo` to check range. Alternatively, define the subregion
    indirectly via a range check on the node values or via distances from a
    given point. Finally, you can give *projection* for oblique projections to
    determine the corresponding rectangular *region* setting that will give a
    grid that fully covers the oblique domain.

    Full option list at :gmt-docs:`grdcut.html`

    {aliases}

    Parameters
    ----------
    grid : str or xarray.DataArray
        The file name of the input grid or the grid loaded as a DataArray.
    outgrid : str or None
        The name of the output netCDF file with extension .nc to store the grid
        in.
    {J}
    {R}
    extend : bool or int or float
        Allow grid to be extended if new *region* exceeds existing boundaries.
        Give a value to initialize nodes outside current region.
    circ_subregion : str
        ``'lon/lat/radius[unit][+n]'``.
        Specify an origin (*lon* and *lat*) and *radius*; append a distance
        *unit* and we determine the corresponding rectangular region so that
        all grid nodes on or inside the circle are contained in the subset.
        If **+n** is appended we set all nodes outside the circle to NaN.
    z_subregion : str
        ``'[min/max][+n|N|r]'``.
        Determine a new rectangular region so that all nodes outside this
        region are also outside the given z-range [-inf/+inf]. To indicate no
        limit on *min* or *max* only, specify a hyphen (-). Normally, any NaNs
        encountered are simply skipped and not considered in the
        range-decision. Append **+n** to consider a NaN to be outside the given
        z-range. This means the new subset will be NaN-free. Alternatively,
        append **+r** to consider NaNs to be within the data range. In this
        case we stop shrinking the boundaries once a NaN is found [Default
        simply skips NaNs when making the range decision]. Finally, if your
        core subset grid is surrounded by rows and/or columns that are all
        NaNs, append **+N** to strip off such columns before (optionally)
        considering the range of the core subset for further reduction of the
        area.

    {V}

    Returns
    -------
    ret: xarray.DataArray or None
        Return type depends on whether the *outgrid* parameter is set:

        - xarray.DataArray if *outgrid* is not set
        - None if *outgrid* is set (grid output will be stored in *outgrid*)
    """
    kind = data_kind(grid)

    with GMTTempFile(suffix=".nc") as tmpfile:
        with Session() as lib:
            if kind == "file":
                file_context = dummy_context(grid)
            elif kind == "grid":
                file_context = lib.virtualfile_from_grid(grid)
            else:
                raise GMTInvalidInput("Unrecognized data type: {}".format(type(grid)))

            with file_context as infile:
                if "G" not in kwargs.keys():  # if outgrid is unset, output to tempfile
                    kwargs.update({"G": tmpfile.name})
                outgrid = kwargs["G"]
                arg_str = " ".join([infile, build_arg_string(kwargs)])
                lib.call_module("grdcut", arg_str)

        if outgrid == tmpfile.name:  # if user did not set outgrid, return DataArray
            with xr.open_dataarray(outgrid) as dataarray:
                result = dataarray.load()
                _ = result.gmt  # load GMTDataArray accessor information
        else:
            result = None  # if user sets an outgrid, return None

        return result


@fmt_docstring
@use_alias(
    D="distance",
    F="filter",
    G="outgrid",
    I="spacing",
    N="nans",
    R="region",
    T="toggle",
    V="verbose",
)
@kwargs_to_strings(R="sequence")
def grdfilter(grid, **kwargs):
    """
    Filter a grid in the space (or time) domain.

    Filter a grid file in the time domain using one of the selected convolution
    or non-convolution isotropic or rectangular filters and compute distances
    using Cartesian or Spherical geometries. The output grid file can
    optionally be generated as a sub-region of the input (via *region*) and/or
    with new increment (via *spacing*) or registration (via *toggle*). In this
    way, one may have "extra space" in the input data so that the edges will
    not be used and the output can be within one half-width of the input edges.
    If the filter is low-pass, then the output may be less frequently sampled
    than the input.

    Full option list at :gmt-docs:`grdfilter.html`

    {aliases}

    Parameters
    ----------
    grid : str or xarray.DataArray
        The file name of the input grid or the grid loaded as a DataArray.
    outgrid : str or None
        The name of the output netCDF file with extension .nc to store the grid
        in.
    filter : str
        ``xwidth[/width2][modifiers]``.
        Name of filter type you which to apply, followed by the width
        b: Box Car; c: Cosine Arch; g: Gaussian; o: Operator; m: Median;
        p: Maximum Likelihood probability; h: histogram
        Example: F='m600' for a median filter with width of 600
    distance : str
        Distance *flag* tells how grid (x,y) relates to filter width as
        follows:

        p: grid (px,py) with *width* an odd number of pixels; Cartesian
        distances.

        0: grid (x,y) same units as *width*, Cartesian distances.

        1: grid (x,y) in degrees, *width* in kilometers, Cartesian distances.

        2: grid (x,y) in degrees, *width* in km, dx scaled by cos(middle y),
        Cartesian distances.

        The above options are fastest because they allow weight matrix to be
        computed only once. The next three options are slower because they
        recompute weights for each latitude.

        3: grid (x,y) in degrees, *width* in km, dx scaled by cosine(y),
        Cartesian distance calculation.

        4: grid (x,y) in degrees, *width* in km, Spherical distance
        calculation.

        5: grid (x,y) in Mercator ``projection='m1'`` img units, *width* in km,
        Spherical distance calculation.

    spacing : str
        ``xinc[+e|n][/yinc[+e|n]]``.
        x_inc [and optionally y_inc] is the grid spacing.
    nans : str or float
        ``i|p|r``.
        Determine how NaN-values in the input grid affects the filtered output.
    {R}
    toggle : bool
        Toggle the node registration for the output grid so as to become the
        opposite of the input grid. [Default gives the same registration as the
        input grid].
    {V}

    Returns
    -------
    ret: xarray.DataArray or None
        Return type depends on whether the *outgrid* parameter is set:
        - xarray.DataArray if *outgrid* is not set
        - None if *outgrid* is set (grid output will be stored in *outgrid*)

    Examples
    --------
    >>> import os
    >>> import pygmt

    >>> # Apply a filter of 600km (full width) to the @earth_relief_30m file
    >>> # and return a filtered field (saved as netcdf)
    >>> pygmt.grdfilter(
    ...     grid="@earth_relief_30m",
    ...     filter="m600",
    ...     distance="4",
    ...     region=[150, 250, 10, 40],
    ...     spacing=0.5,
    ...     outgrid="filtered_pacific.nc",
    ... )
    >>> os.remove("filtered_pacific.nc")  # cleanup file

    >>> # Apply a gaussian smoothing filter of 600 km in the input data array,
    >>> # and returns a filtered data array with the smoothed field.
    >>> grid = pygmt.datasets.load_earth_relief()
    >>> smooth_field = pygmt.grdfilter(grid=grid, filter="g600", distance="4")
    """
    kind = data_kind(grid)

    with GMTTempFile(suffix=".nc") as tmpfile:
        with Session() as lib:
            if kind == "file":
                file_context = dummy_context(grid)
            elif kind == "grid":
                file_context = lib.virtualfile_from_grid(grid)
            else:
                raise GMTInvalidInput("Unrecognized data type: {}".format(type(grid)))

            with file_context as infile:
                if "G" not in kwargs.keys():  # if outgrid is unset, output to tempfile
                    kwargs.update({"G": tmpfile.name})
                outgrid = kwargs["G"]
                arg_str = " ".join([infile, build_arg_string(kwargs)])
                lib.call_module("grdfilter", arg_str)

        if outgrid == tmpfile.name:  # if user did not set outgrid, return DataArray
            with xr.open_dataarray(outgrid) as dataarray:
                result = dataarray.load()
                _ = result.gmt  # load GMTDataArray accessor information
        else:
            result = None  # if user sets an outgrid, return None

        return result
