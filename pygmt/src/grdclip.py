"""
grdclip - Clip the range of grid values.
"""

import xarray as xr
from pygmt.clib import Session
from pygmt.helpers import (
    build_arg_list,
    deprecate_parameter,
    fmt_docstring,
    kwargs_to_strings,
    use_alias,
)

__doctest_skip__ = ["grdclip"]


# TODO(PyGMT>=0.19.0): Remove the deprecated "new" parameter.
@fmt_docstring
@deprecate_parameter("new", "replace", "v0.15.0", remove_version="v0.19.0")
@use_alias(
    R="region",
    Sa="above",
    Sb="below",
    Si="between",
    Sr="replace",
    V="verbose",
)
@kwargs_to_strings(
    R="sequence",
    Sa="sequence",
    Sb="sequence",
    Si="sequence",
    Sr="sequence",
)
def grdclip(grid, outgrid: str | None = None, **kwargs) -> xr.DataArray | None:
    r"""
    Clip the range of grid values.

    Produce a clipped ``outgrid`` or :class:`xarray.DataArray` version of the
    input ``grid`` file.

    The parameters ``above`` and ``below`` allow for a given value to be set
    for values above or below a set amount, respectively. This allows for
    extreme values in a grid, such as points below a certain depth when
    plotting Earth relief, to all be set to the same value.

    Full option list at :gmt-docs:`grdclip.html`

    {aliases}

    Parameters
    ----------
    {grid}
    {outgrid}
    {region}
    above : str or list
        [*high*, *above*].
        Set all data[i] > *high* to *above*.
    below : str or list
        [*low*, *below*].
        Set all data[i] < *low* to *below*.
    between : str or list
        [*low*, *high*, *between*].
        Set all data[i] >= *low* and <= *high* to *between*.
    replace : str or list
        [*old*, *new*].
        Set all data[i] == *old* to *new*. This is mostly useful when
        your data are known to be integer values.
    {verbose}

    Returns
    -------
    ret
        Return type depends on whether the ``outgrid`` parameter is set:

        - :class:`xarray.DataArray` if ``outgrid`` is not set
        - ``None`` if ``outgrid`` is set (grid output will be stored in the file set by
          ``outgrid``)

    Example
    -------
    >>> import pygmt
    >>> # Load a grid of @earth_relief_30m data, with a longitude range of
    >>> # 10° E to 30° E, and a latitude range of 15° N to 25° N
    >>> grid = pygmt.datasets.load_earth_relief(
    ...     resolution="30m", region=[10, 30, 15, 25]
    ... )
    >>> # Report the minimum and maximum data values
    >>> [grid.data.min(), grid.data.max()]
    [183.5, 1807.0]
    >>> # Create a new grid from an input grid. Set all values below 1,000 to
    >>> # 0 and all values above 1,500 to 10,000
    >>> new_grid = pygmt.grdclip(grid=grid, below=[1000, 0], above=[1500, 10000])
    >>> # Report the minimum and maximum data values
    >>> [new_grid.data.min(), new_grid.data.max()]
    [0.0, 10000.0]
    """
    with Session() as lib:
        with (
            lib.virtualfile_in(check_kind="raster", data=grid) as vingrd,
            lib.virtualfile_out(kind="grid", fname=outgrid) as voutgrd,
        ):
            kwargs["G"] = voutgrd
            lib.call_module(
                module="grdclip", args=build_arg_list(kwargs, infile=vingrd)
            )
            return lib.virtualfile_to_raster(vfname=voutgrd, outgrid=outgrid)
