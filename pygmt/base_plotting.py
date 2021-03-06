"""
Base class with plot generating commands.

Does not define any special non-GMT methods (savefig, show, etc).
"""
import contextlib

import numpy as np
from pygmt.clib import Session
from pygmt.exceptions import GMTInvalidInput
from pygmt.helpers import (
    args_in_kwargs,
    build_arg_string,
    data_kind,
    dummy_context,
    fmt_docstring,
    is_nonstr_iter,
    kwargs_to_strings,
    use_alias,
)


class BasePlotting:
    """
    Base class for Figure and Subplot.

    Defines the plot generating methods and a hook for subclasses to insert
    special arguments (the _preprocess method).
    """

    def _preprocess(self, **kwargs):  # pylint: disable=no-self-use
        """
        Make any changes to kwargs or required actions before plotting.

        This method is run before all plotting commands and can be used to
        insert special arguments into the kwargs or make any actions that are
        required before ``call_module``.

        For example, the :class:`pygmt.Figure` needs this to tell the GMT
        modules to plot to a specific figure.

        This is a dummy method that does nothing.

        Returns
        -------
        kwargs : dict
            The same input kwargs dictionary.

        Examples
        --------

        >>> base = BasePlotting()
        >>> base._preprocess(resolution="low")
        {'resolution': 'low'}
        """
        return kwargs

    @fmt_docstring
    @use_alias(
        R="region",
        J="projection",
        A="area_thresh",
        C="lakes",
        B="frame",
        D="resolution",
        E="dcw",
        I="rivers",
        L="map_scale",
        N="borders",
        W="shorelines",
        G="land",
        S="water",
        U="timestamp",
        V="verbose",
        X="xshift",
        Y="yshift",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", p="sequence")
    def coast(self, **kwargs):
        r"""
        Plot continents, shorelines, rivers, and borders on maps

        Plots grayshaded, colored, or textured land-masses [or water-masses] on
        maps and [optionally] draws coastlines, rivers, and political
        boundaries.  Alternatively, it can (1) issue clip paths that will
        contain all land or all water areas, or (2) dump the data to an ASCII
        table. The data files come in 5 different resolutions: (**f**)ull,
        (**h**)igh, (**i**)ntermediate, (**l**)ow, and (**c**)rude. The full
        resolution files amount to more than 55 Mb of data and provide great
        detail; for maps of larger geographical extent it is more economical to
        use one of the other resolutions. If the user selects to paint the
        land-areas and does not specify fill of water-areas then the latter
        will be transparent (i.e., earlier graphics drawn in those areas will
        not be overwritten).  Likewise, if the water-areas are painted and no
        land fill is set then the land-areas will be transparent.

        A map projection must be supplied.

        Full option list at :gmt-docs:`coast.html`

        {aliases}

        Parameters
        ----------
        {J}
        {R}
        area_thresh : int, float, or str
            *min_area*\ [/*min_level*/*max_level*][**+ag**\|\ **i**\
            \|\ **s**\|\ **S**][**+r**\|\ **l**][**+p**\
            *percent*].
            Features with an area smaller than min_area in km^2 or of
            hierarchical level that is lower than min_level or higher than
            max_level will not be plotted.
        {B}
        lakes : str or list
            *fill*\ [**+l**\|\ **+r**].
            Set the shade, color, or pattern for lakes and river-lakes. The
            default is the fill chosen for wet areas set by the ``water``
            argument. Optionally, specify separate fills by appending
            **+l** for lakes or **+r** for river-lakes, and passing multiple
            strings in a list.
        resolution : str
            **f**\|\ **h**\|\ **i**\|\ **l**\|\ **c**.
            Selects the resolution of the data set to: (**f**\ )ull,
            (**h**\ )igh, (**i**\ )ntermediate, (**l**\ )ow,
            and (**c**\ )rude.
        land : str
            Select filling or clipping of “dry” areas.
        rivers : int or str or list
            *river*\ [/*pen*].
            Draw rivers. Specify the type of rivers and [optionally] append
            pen attributes [Default pen: width = default, color = black,
            style = solid].

            Choose from the list of river types below; pass a list to
            ``rivers`` to use multiple arguments.

            0 = Double-lined rivers (river-lakes)

            1 = Permanent major rivers

            2 = Additional major rivers

            3 = Additional rivers

            4 = Minor rivers

            5 = Intermittent rivers - major

            6 = Intermittent rivers - additional

            7 = Intermittent rivers - minor

            8 = Major canals

            9 = Minor canals

            10 = Irrigation canals

            You can also choose from several preconfigured river groups:

            a = All rivers and canals (0-10)

            A = All rivers and canals except river-lakes (1-10)

            r = All permanent rivers (0-4)

            R = All permanent rivers except river-lakes (1-4)

            i = All intermittent rivers (5-7)

            c = All canals (8-10)
        map_scale : str
            [**g**\|\ **j**\|\ **J**\|\ **n**\|\ **x**]\ *refpoint*.
            Draws a simple map scale centered on the reference point specified.
        borders : int or str or list
            *border*\ [/*pen*].
            Draw political boundaries. Specify the type of boundary and
            [optionally] append pen attributes [Default pen: width = default,
            color = black, style = solid].

            Choose from the list of boundaries below. Pass a list to
            ``borders`` to use multiple arguments.

            1 = National boundaries

            2 = State boundaries within the Americas

            3 = Marine boundaries

            a = All boundaries (1-3)
        water : str
            Select filling or clipping of “wet” areas.
        {U}
        shorelines : int or str or list
            [*level*\ /]\ *pen*.
            Draw shorelines [Default is no shorelines]. Append pen attributes
            [Defaults: width = default, color = black, style = solid] which
            apply to all four levels. To set the pen for a single level,
            pass a string with *level*\ /*pen*\ , where level is
            1-4 and represent coastline, lakeshore, island-in-lake shore, and
            lake-in-island-in-lake shore. Pass a list of *level*\ /*pen*
            strings to ``shorelines`` to set multiple levels. When specific
            level pens are set, those not listed will not be drawn.
        dcw : str or list
            *code1,code2,…*\ [**+l**\|\ **L**\ ][**+g**\ *fill*\ ]
            [**+p**\ *pen*\ ][**+z**].
            Select painting or dumping country polygons from the
            `Digital Chart of the World
            <https://en.wikipedia.org/wiki/Digital_Chart_of_the_World>`__.
            Append one or more comma-separated countries using the 2-character
            `ISO 3166-1 alpha-2 convention
            <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`__.
            To select a state of a country (if available), append
            .\ *state*, (e.g, US.TX for Texas).  To specify a whole continent,
            prepend **=** to any of the continent codes (e.g. =EU for Europe).
            Append **+p**\ *pen* to draw polygon outlines
            (default is no outline) and **+g**\ *fill* to fill them
            (default is no fill). Append **+l**\|\ **+L** to *=continent* to
            only list countries in that continent; repeat if more than one
            continent is requested. Append **+z** to place the country code in
            the segment headers via **-Z**\ *code* settings.To apply different
            settings to different countries, pass a list of string arguments.
        {XY}
        {p}
        {t}
        {V}
        """
        kwargs = self._preprocess(**kwargs)
        if not args_in_kwargs(args=["C", "G", "S", "I", "N", "Q", "W"], kwargs=kwargs):
            raise GMTInvalidInput(
                """At least one of the following arguments must be specified:
                lakes, land, water, rivers, borders, Q, or shorelines"""
            )
        with Session() as lib:
            lib.call_module("coast", build_arg_string(kwargs))

    @fmt_docstring
    @use_alias(
        R="region",
        J="projection",
        B="frame",
        C="cmap",
        D="position",
        F="box",
        G="truncate",
        I="shading",
        W="scale",
        V="verbose",
        X="xshift",
        Y="yshift",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", G="sequence", I="sequence", p="sequence")
    def colorbar(self, **kwargs):
        """
        Plot a gray or color scale-bar on maps.

        Both horizontal and vertical scales are supported. For CPTs with
        gradational colors (i.e., the lower and upper boundary of an interval
        have different colors) we will interpolate to give a continuous scale.
        Variations in intensity due to shading/illumination may be displayed by
        setting the option -I. Colors may be spaced according to a linear
        scale, all be equal size, or by providing a file with individual tile
        widths.

        Full option list at :gmt-docs:`colorbar.html`

        {aliases}

        Parameters
        ----------
        frame : str or list
            Set color bar boundary frame, labels, and axes attributes.
        {CPT}
        position : str
            ``[g|j|J|n|x]refpoint[+wlength[/width]][+e[b|f][length]][+h|v]
            [+jjustify][+m[a|c|l|u]][+n[txt]][+odx[/dy]]``. Defines the
            reference point on the map for the color scale using one of four
            coordinate systems: (1) Use *g* for map (user) coordinates, (2) use
            *j* or *J* for setting refpoint via a 2-char justification code
            that refers to the (invisible) map domain rectangle, (3) use *n*
            for normalized (0-1) coordinates, or (4) use *x* for plot
            coordinates (inches, cm, etc.). All but *x* requires both *region*
            and *projection* to be specified. Append +w followed by the length
            and width of the color bar. If width is not specified then it is
            set to 4% of the given length. Give a negative length to reverse
            the scale bar. Append +h to get a horizontal scale
            [Default is vertical (+v)]. By default, the anchor point on the
            scale is assumed to be the bottom left corner (BL), but this can be
            changed by appending +j followed by a 2-char justification code
            *justify*.
        box : bool or str
            ``[+cclearances][+gfill][+i[[gap/]pen]][+p[pen]][+r[radius]]
            [+s[[dx/dy/][shade]]]``. If set to True, draws a rectangular
            border around the color scale. Alternatively, specify a different
            pen with +ppen. Add +gfill to fill the scale panel [no fill].
            Append +cclearance where clearance is either gap, xgap/ygap, or
            lgap/rgap/bgap/tgap where these items are uniform, separate in x-
            and y-direction, or individual side spacings between scale and
            border. Append +i to draw a secondary, inner border as well. We use
            a uniform gap between borders of 2p and the MAP_DEFAULTS_PEN unless
            other values are specified. Append +r to draw rounded rectangular
            borders instead, with a 6p corner radius. You can override this
            radius by appending another value. Finally, append +s to draw an
            offset background shaded region. Here, dx/dy indicates the shift
            relative to the foreground frame [4p/-4p] and shade sets the fill
            style to use for shading [gray50].
        truncate : list or str
            ``zlo/zhi`` Truncate the incoming CPT so that the lowest and
            highest z-levels are to zlo and zhi. If one of these equal NaN then
            we leave that end of the CPT alone. The truncation takes place
            before the plotting.
        scale : float
            Multiply all z-values in the CPT by the provided scale. By default
            the CPT is used as is.
        shading : str or list or bool
            Add illumination effects. Passing a single numerical value sets the
            range of intensities from -value to +value. If not specified, 1 is
            used. Alternatively, set ``shading=[low, high]`` to specify an
            asymmetric intensity range from *low* to *high*. The default is no
            illumination.
        {V}
        {XY}
        {p}
        {t}
        """
        kwargs = self._preprocess(**kwargs)
        with Session() as lib:
            lib.call_module("colorbar", build_arg_string(kwargs))

    @fmt_docstring
    @use_alias(
        A="annotation",
        B="frame",
        C="interval",
        G="label_placement",
        J="projection",
        L="limit",
        Q="cut",
        R="region",
        S="resample",
        U="timestamp",
        V="verbose",
        W="pen",
        l="label",
        X="xshift",
        Y="yshift",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", L="sequence", A="sequence_plus", p="sequence")
    def grdcontour(self, grid, **kwargs):
        """
        Convert grids or images to contours and plot them on maps.

        Takes a grid file name or an xarray.DataArray object as input.

        Full option list at :gmt-docs:`grdcontour.html`

        {aliases}

        Parameters
        ----------
        grid : str or xarray.DataArray
            The file name of the input grid or the grid loaded as a DataArray.
        interval : str or int
            Specify the contour lines to generate.

            - The filename of a `CPT`  file where the color boundaries will
              be used as contour levels.
            - The filename of a 2 (or 3) column file containing the contour
              levels (col 1), (C)ontour or (A)nnotate (col 2), and optional
              angle (col 3)
            - A fixed contour interval ``cont_int`` or a single contour with
              ``+[cont_int]``
        annotation : str,  int, or list
            Specify or disable annotated contour levels, modifies annotated
            contours specified in ``-C``.

            - Specify a fixed annotation interval ``annot_int`` or a
              single annotation level ``+[annot_int]``
            - Disable all annotation  with  ``'-'``
            - Optional label modifiers can be specified as a single string
              ``'[annot_int]+e'``  or with a list of options
              ``([annot_int], 'e', 'f10p', 'gred')``.
        limit : str or list of 2 ints
            Do no draw contours below `low` or above `high`, specify as string
            ``'[low]/[high]'``  or list ``[low,high]``.
        cut : str or int
            Do not draw contours with less than `cut` number of points.
        resample : str or int
            Resample smoothing factor.
        {J}
        {R}
        {B}
        label_placement : str
            ``[d|f|n|l|L|x|X]params``.
            The required argument controls the placement of labels along the
            quoted lines. It supports five controlling algorithms. See
            :gmt-docs:`grdcontour.html#g` for details.
        {U}
        {V}
        {W}
        {XY}
        label : str
            Add a legend entry for the contour being plotted. Normally, the
            annotated contour is selected for the legend. You can select the
            regular contour instead, or both of them, by considering the label
            to be of the format [*annotcontlabel*][/*contlabel*]. If either
            label contains a slash (/) character then use ``|`` as the
            separator for the two labels instead.
        {p}
        {t}
        """
        kwargs = self._preprocess(**kwargs)
        kind = data_kind(grid, None, None)
        with Session() as lib:
            if kind == "file":
                file_context = dummy_context(grid)
            elif kind == "grid":
                file_context = lib.virtualfile_from_grid(grid)
            else:
                raise GMTInvalidInput("Unrecognized data type: {}".format(type(grid)))
            with file_context as fname:
                arg_str = " ".join([fname, build_arg_string(kwargs)])
                lib.call_module("grdcontour", arg_str)

    @fmt_docstring
    @use_alias(
        A="img_out",
        B="frame",
        C="cmap",
        D="img_in",
        E="dpi",
        G="bit_color",
        I="shading",
        J="projection",
        M="monochrome",
        N="no_clip",
        Q="nan_transparent",
        R="region",
        U="timestamp",
        V="verbose",
        X="xshift",
        Y="yshift",
        n="interpolation",
        p="perspective",
        t="transparency",
        x="cores",
    )
    @kwargs_to_strings(R="sequence", p="sequence")
    def grdimage(self, grid, **kwargs):
        """
        Project and plot grids or images.

        Reads a 2-D grid file and produces a gray-shaded (or colored) map by
        building a rectangular image and assigning pixels a gray-shade (or
        color) based on the z-value and the CPT file. Optionally, illumination
        may be added by providing a file with intensities in the (-1,+1) range
        or instructions to derive intensities from the input data grid. Values
        outside this range will be clipped. Such intensity files can be created
        from the grid using `grdgradient` and, optionally, modified by
        `grdmath` or `grdhisteq`. If GMT is built with GDAL support, *grid* can
        be an image file (geo-referenced or not). In this case the image can
        optionally be illuminated with the file provided via the *shading*
        option. Here, if image has no coordinates then those of the intensity
        file will be used.

        When using map projections, the grid is first resampled on a new
        rectangular grid with the same dimensions. Higher resolution images can
        be obtained by using the *dpi* option. To obtain the resampled value
        (and hence shade or color) of each map pixel, its location is inversely
        projected back onto the input grid after which a value is interpolated
        between the surrounding input grid values. By default bi-cubic
        interpolation is used. Aliasing is avoided by also forward projecting
        the input grid nodes. If two or more nodes are projected onto the same
        pixel, their average will dominate in the calculation of the pixel
        value. Interpolation and aliasing is controlled with the
        *interpolation* option.

        The *region* option can be used to select a map region larger or
        smaller than that implied by the extent of the grid.

        Full option list at :gmt-docs:`grdimage.html`

        {aliases}

        Parameters
        ----------
        grid : str or xarray.DataArray
            The file name or a DataArray containing the input 2-D gridded data
            set or image to be plotted (See GRID FILE FORMATS at
            :gmt-docs:`grdimage.html#grid-file-formats`).
        img_out : str
            ``out_img[=driver]``.
            Save an image in a raster format instead of PostScript. Use
            extension .ppm for a Portable Pixel Map format which is the only
            raster format GMT can natively write. For GMT installations
            configured with GDAL support there are more choices: Append
            *out_img* to select the image file name and extension. If the
            extension is one of .bmp, .gif, .jpg, .png, or .tif then no driver
            information is required. For other output formats you must append
            the required GDAL driver. The *driver* is the driver code name used
            by GDAL; see your GDAL installation's documentation for available
            drivers. Append a **+c**\\ *options* string where options is a list
            of one or more concatenated number of GDAL **-co** options. For
            example, to write a GeoPDF with the TerraGo format use
            ``=PDF+cGEO_ENCODING=OGC_BP``. Notes: (1) If a tiff file (.tif) is
            selected then we will write a GeoTiff image if the GMT projection
            syntax translates into a PROJ syntax, otherwise a plain tiff file
            is produced. (2) Any vector elements will be lost.
        {B}
        {CPT}
        img_in : str
            ``[r]``
            GMT will automatically detect standard image files (Geotiff, TIFF,
            JPG, PNG, GIF, etc.) and will read those via GDAL. For very obscure
            image formats you may need to explicitly set *img_in*, which
            specifies that the grid is in fact an image file to be read via
            GDAL. Append **r** to assign the region specified by *region*
            to the image. For example, if you have used ``region='d'`` then the
            image will be assigned a global domain. This mode allows you to
            project a raw image (an image without referencing coordinates).
        dpi : int
            ``[i|dpi]``.
            Sets the resolution of the projected grid that will be created if a
            map projection other than Linear or Mercator was selected [100]. By
            default, the projected grid will be of the same size (rows and
            columns) as the input file. Specify **i** to use the PostScript
            image operator to interpolate the image at the device resolution.
        bit_color : str
            ``color[+b|f]``.
            This option only applies when a resulting 1-bit image otherwise
            would consist of only two colors: black (0) and white (255). If so,
            this option will instead use the image as a transparent mask and
            paint the mask with the given color. Append **+b** to paint the
            background pixels (1) or **+f** for the foreground pixels
            [Default].
        shading : str
            ``[intensfile|intensity|modifiers]``.
            Give the name of a grid file with intensities in the (-1,+1) range,
            or a constant intensity to apply everywhere (affects the ambient
            light). Alternatively, derive an intensity grid from the input data
            grid via a call to `grdgradient`; append **+a**\\ *azimuth*,
            **+n**\\ *args*, and **+m**\\ *ambient* to specify azimuth,
            intensity, and ambient arguments for that module, or just give
            **+d** to select the default arguments (``+a-45+nt1+m0``). If you
            want a more specific intensity scenario then run `grdgradient`
            separately first. If we should derive intensities from another file
            than grid, specify the file with suitable modifiers [Default is no
            illumination].
        {J}
        monochrome : bool
            Force conversion to monochrome image using the (television) YIQ
            transformation. Cannot be used with *nan_transparent*.
        no_clip : bool
            Do not clip the image at the map boundary (only relevant for
            non-rectangular maps).
        nan_transparent : bool
            Make grid nodes with z = NaN transparent, using the color-masking
            feature in PostScript Level 3 (the PS device must support PS Level
            3).
        {R}
        {V}
        {XY}
        {n}
        {p}
        {t}
        {x}
        """
        kwargs = self._preprocess(**kwargs)
        kind = data_kind(grid, None, None)
        with Session() as lib:
            if kind == "file":
                file_context = dummy_context(grid)
            elif kind == "grid":
                file_context = lib.virtualfile_from_grid(grid)
            else:
                raise GMTInvalidInput("Unrecognized data type: {}".format(type(grid)))
            with file_context as fname:
                arg_str = " ".join([fname, build_arg_string(kwargs)])
                lib.call_module("grdimage", arg_str)

    @fmt_docstring
    @use_alias(
        R="region",
        J="projection",
        Jz="zscale",
        JZ="zsize",
        B="frame",
        C="cmap",
        G="drapegrid",
        N="plane",
        Q="surftype",
        Wc="contourpen",
        Wm="meshpen",
        Wf="facadepen",
        I="shading",
        V="verbose",
        X="xshift",
        Y="yshift",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", p="sequence")
    def grdview(self, grid, **kwargs):
        """
        Create 3-D perspective image or surface mesh from a grid.

        Reads a 2-D grid file and produces a 3-D perspective plot by drawing a
        mesh, painting a colored/gray-shaded surface made up of polygons, or by
        scanline conversion of these polygons to a raster image. Options
        include draping a data set on top of a surface, plotting of contours on
        top of the surface, and apply artificial illumination based on
        intensities provided in a separate grid file.

        Full option list at :gmt-docs:`grdview.html`

        {aliases}

        Parameters
        ----------
        grid : str or xarray.DataArray
            The file name of the input relief grid or the grid loaded as a
            DataArray.

        zscale/zsize : float or str
            Set z-axis scaling or z-axis size.

        {B}

        cmap : str
            The name of the color palette table to use.

        drapegrid : str or xarray.DataArray
            The file name or a DataArray of the image grid to be draped on top
            of the relief provided by grid. [Default determines colors from
            grid]. Note that -Jz and -N always refers to the grid. The
            drapegrid only provides the information pertaining to colors, which
            (if drapegrid is a grid) will be looked-up via the CPT (see -C).

        plane : float or str
            ``level[+gfill]``.
            Draws a plane at this z-level. If the optional color is provided
            via the +g modifier, and the projection is not oblique, the frontal
            facade between the plane and the data perimeter is colored.

        surftype : str
            Specifies cover type of the grid.
            Select one of following settings:
            1. 'm' for mesh plot [Default].
            2. 'mx' or 'my' for waterfall plots (row or column profiles).
            3. 's' for surface plot.
            4. 'i' for image plot.
            5. 'c'. Same as 'i' but will make nodes with z = NaN transparent.
            For any of these choices, you may force a monochrome image by
            appending the modifier +m.

        contourpen : str
            Draw contour lines on top of surface or mesh (not image). Append
            pen attributes used for the contours.
        meshpen : str
            Sets the pen attributes used for the mesh. You must also select -Qm
            or -Qsm for meshlines to be drawn.
        facadepen :str
            Sets the pen attributes used for the facade. You must also select
            -N for the facade outline to be drawn.

        shading : str
            Provide the name of a grid file with intensities in the (-1,+1)
            range, or a constant intensity to apply everywhere (affects the
            ambient light). Alternatively, derive an intensity grid from the
            input data grid reliefgrid via a call to ``grdgradient``; append
            ``+aazimuth``, ``+nargs``, and ``+mambient`` to specify azimuth,
            intensity, and ambient arguments for that module, or just give
            ``+d`` to select the default arguments (``+a-45+nt1+m0``).

        {V}
        {XY}
        {p}
        {t}
        """
        kwargs = self._preprocess(**kwargs)
        kind = data_kind(grid, None, None)
        with Session() as lib:
            if kind == "file":
                file_context = dummy_context(grid)
            elif kind == "grid":
                file_context = lib.virtualfile_from_grid(grid)
            else:
                raise GMTInvalidInput(f"Unrecognized data type for grid: {type(grid)}")

            with contextlib.ExitStack() as stack:
                if "G" in kwargs:  # deal with kwargs["G"] if drapegrid is xr.DataArray
                    drapegrid = kwargs["G"]
                    if data_kind(drapegrid) in ("file", "grid"):
                        if data_kind(drapegrid) == "grid":
                            drape_context = lib.virtualfile_from_grid(drapegrid)
                            kwargs["G"] = stack.enter_context(drape_context)
                    else:
                        raise GMTInvalidInput(
                            f"Unrecognized data type for drapegrid: {type(drapegrid)}"
                        )
                fname = stack.enter_context(file_context)
                arg_str = " ".join([fname, build_arg_string(kwargs)])
                lib.call_module("grdview", arg_str)

    @fmt_docstring
    @use_alias(
        A="straight_line",
        B="frame",
        C="cmap",
        D="offset",
        E="error_bar",
        F="connection",
        G="color",
        I="intensity",
        J="projection",
        L="close",
        N="no_clip",
        R="region",
        S="style",
        U="timestamp",
        V="verbose",
        W="pen",
        X="xshift",
        Y="yshift",
        Z="zvalue",
        i="columns",
        l="label",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", i="sequence_comma", p="sequence")
    def plot(self, x=None, y=None, data=None, sizes=None, direction=None, **kwargs):
        """
        Plot lines, polygons, and symbols in 2-D.

        Takes a matrix, (x,y) pairs, or a file name as input and plots lines,
        polygons, or symbols at those locations on a map.

        Must provide either *data* or *x* and *y*.

        If providing data through *x* and *y*, *color* can be a 1d array that
        will be mapped to a colormap.

        If a symbol is selected and no symbol size given, then plot will
        interpret the third column of the input data as symbol size. Symbols
        whose size is <= 0 are skipped. If no symbols are specified then the
        symbol code (see *style* below) must be present as last column in the
        input. If *style* is not used, a line connecting the data points will
        be drawn instead. To explicitly close polygons, use *close*. Select a
        fill with *color*. If *color* is set, *pen* will control whether the
        polygon outline is drawn or not. If a symbol is selected, *color* and
        *pen* determines the fill and outline/no outline, respectively.

        Full option list at :gmt-docs:`plot.html`

        {aliases}

        Parameters
        ----------
        x/y : float or 1d arrays
            The x and y coordinates, or arrays of x and y coordinates of the
            data points
        data : str or 2d array
            Either a data file name or a 2d numpy array with the tabular data.
            Use option *columns* (i) to choose which columns are x, y, color,
            and size, respectively.
        sizes : 1d array
            The sizes of the data points in units specified in *style* (S).
            Only valid if using *x* and *y*.
        direction : list of two 1d arrays
            If plotting vectors (using ``style='V'`` or ``style='v'``), then
            should be a list of two 1d arrays with the vector directions. These
            can be angle and length, azimuth and length, or x and y components,
            depending on the style options chosen.
        {J}
        {R}
        straight_line : bool or str
            ``[m|p|x|y]``.
            By default, geographic line segments are drawn as great circle
            arcs. To draw them as straight lines, use *straight_line*.
            Alternatively, add **m** to draw the line by first following a
            meridian, then a parallel. Or append **p** to start following a
            parallel, then a meridian. (This can be practical to draw a line
            along parallels, for example). For Cartesian data, points are
            simply connected, unless you append **x** or **y** to draw
            stair-case curves that whose first move is along *x* or *y*,
            respectively.
        {B}
        {CPT}
        offset : str
            ``dx/dy``.
            Offset the plot symbol or line locations by the given amounts
            *dx/dy* [Default is no offset]. If *dy* is not given it is set
            equal to *dx*.
        error_bar : bool or str
            ``[x|y|X|Y][+a][+cl|f][+n][+wcap][+ppen]``.
            Draw symmetrical error bars. Full documentation is at
            :gmt-docs:`plot.html#e`.
        connection : str
            ``[c|n|r][a|f|s|r|refpoint]``.
            Alter the way points are connected (by specifying a *scheme*) and
            data are grouped (by specifying a *method*). Append one of three
            line connection schemes:

            - **c** : Draw continuous line segments for each group [Default].
            - **r** : Draw line segments from a reference point reset for each
              group.
            - **n** : Draw networks of line segments between all points in
              each group.

            Optionally, append the one of four segmentation methods to define
            the group:

            - **a** : Ignore all segment headers, i.e., let all points belong
              to a single group, and set group reference point to the very
              first point of the first file.
            - **f** : Consider all data in each file to be a single separate
              group and reset the group reference point to the first point of
              each group.
            - **s** : Segment headers are honored so each segment is a group;
              the group reference point is reset to the first point of each
              incoming segment [Default].
            - **r** : Same as **s**, but the group reference point is reset
              after each record to the previous point (this method is only
              available with the ``connection='r'`` scheme).

            Instead of the codes **a**|**f**|**s**|**r** you may append the
            coordinates of a *refpoint* which will serve as a fixed external
            reference point for all groups.
        {G}
        intensity : float or bool
            Provide an *intens* value (nominally in the -1 to +1 range) to
            modulate the fill color by simulating illumination [None]. If
            using ``intensity=True``, we will instead read *intens* from the
            first data column after the symbol parameters (if given).
        close : str
            ``[+b|d|D][+xl|r|x0][+yl|r|y0][+ppen]``.
            Force closed polygons. Full documentation is at
            :gmt-docs:`plot.html#l`.
        no_clip : bool or str
            ``'[c|r]'``.
            Do NOT clip symbols that fall outside map border [Default plots
            points whose coordinates are strictly inside the map border only].
            The option does not apply to lines and polygons which are always
            clipped to the map region. For periodic (360-longitude) maps we
            must plot all symbols twice in case they are clipped by the
            repeating boundary. ``no_clip=True`` will turn off clipping and not
            plot repeating symbols. Use ``no_clip="r"`` to turn off clipping
            but retain the plotting of such repeating symbols, or use
            ``no_clip="c"`` to retain clipping but turn off plotting of
            repeating symbols.
        style : str
            Plot symbols (including vectors, pie slices, fronts, decorated or
            quoted lines).
        {W}
        {U}
        {V}
        {XY}
        zvalue : str
            ``value|file``.
            Instead of specifying a symbol or polygon fill and outline color
            via **color** and **pen**, give both a *value* via **zvalue** and a
            color lookup table via **cmap**.  Alternatively, give the name of a
            *file* with one z-value (read from the last column) for each
            polygon in the input data. To apply it to the fill color, use
            ``color='+z'``. To apply it to the pen color, append **+z** to
            **pen**.
        columns : str or 1d array
            Choose which columns are x, y, color, and size, respectively if
            input is provided via *data*. E.g. ``columns = [0, 1]`` or
            ``columns = '0,1'`` if the *x* values are stored in the first
            column and *y* values in the second one. Note: zero-based
            indexing is used.
        label : str
            Add a legend entry for the symbol or line being plotted.

        {p}
        {t}
            *transparency* can also be a 1d array to set varying transparency
            for symbols.
        """
        kwargs = self._preprocess(**kwargs)

        kind = data_kind(data, x, y)

        extra_arrays = []
        if "S" in kwargs and kwargs["S"][0] in "vV" and direction is not None:
            extra_arrays.extend(direction)
        if "G" in kwargs and not isinstance(kwargs["G"], str):
            if kind != "vectors":
                raise GMTInvalidInput(
                    "Can't use arrays for color if data is matrix or file."
                )
            extra_arrays.append(kwargs["G"])
            del kwargs["G"]
        if sizes is not None:
            if kind != "vectors":
                raise GMTInvalidInput(
                    "Can't use arrays for sizes if data is matrix or file."
                )
            extra_arrays.append(sizes)

        if "t" in kwargs and is_nonstr_iter(kwargs["t"]):
            extra_arrays.append(kwargs["t"])
            kwargs["t"] = ""

        with Session() as lib:
            # Choose how data will be passed in to the module
            if kind == "file":
                file_context = dummy_context(data)
            elif kind == "matrix":
                file_context = lib.virtualfile_from_matrix(data)
            elif kind == "vectors":
                file_context = lib.virtualfile_from_vectors(
                    np.atleast_1d(x), np.atleast_1d(y), *extra_arrays
                )

            with file_context as fname:
                arg_str = " ".join([fname, build_arg_string(kwargs)])
                lib.call_module("plot", arg_str)

    @fmt_docstring
    @use_alias(
        A="straight_line",
        B="frame",
        C="cmap",
        D="offset",
        G="color",
        I="intensity",
        J="projection",
        Jz="zscale",
        JZ="zsize",
        L="close",
        N="no_clip",
        Q="no_sort",
        R="region",
        S="style",
        V="verbose",
        W="pen",
        X="xshift",
        Y="yshift",
        Z="zvalue",
        i="columns",
        l="label",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", i="sequence_comma", p="sequence")
    def plot3d(
        self, x=None, y=None, z=None, data=None, sizes=None, direction=None, **kwargs
    ):
        """
        Plot lines, polygons, and symbols in 3-D.

        Takes a matrix, (x,y,z) triplets, or a file name as input and plots
        lines, polygons, or symbols at those locations in 3-D.

        Must provide either *data* or *x*, *y* and *z*.

        If providing data through *x*, *y* and *z*, *color* can be a 1d array
        that will be mapped to a colormap.

        If a symbol is selected and no symbol size given, then plot3d will
        interpret the fourth column of the input data as symbol size. Symbols
        whose size is <= 0 are skipped. If no symbols are specified then the
        symbol code (see *style* below) must be present as last column in the
        input. If *style* is not used, a line connecting the data points will
        be drawn instead. To explicitly close polygons, use *close*. Select a
        fill with *color*. If *color* is set, *pen* will control whether the
        polygon outline is drawn or not. If a symbol is selected, *color* and
        *pen* determines the fill and outline/no outline, respectively.

        Full option list at :gmt-docs:`plot3d.html`

        {aliases}

        Parameters
        ----------
        x/y/z : float or 1d arrays
            The x, y, and z coordinates, or arrays of x, y and z coordinates of
            the data points
        data : str or 2d array
            Either a data file name or a 2d numpy array with the tabular data.
            Use option *columns* (i) to choose which columns are x, y, z,
            color, and size, respectively.
        sizes : 1d array
            The sizes of the data points in units specified in *style* (S).
            Only valid if using *x*, *y* and *z*.
        direction : list of two 1d arrays
            If plotting vectors (using ``style='V'`` or ``style='v'``), then
            should be a list of two 1d arrays with the vector directions. These
            can be angle and length, azimuth and length, or x and y components,
            depending on the style options chosen.
        {J}
        zscale/zsize : float or str
            Set z-axis scaling or z-axis size.
        {R}
        straight_line : bool or str
            ``[m|p|x|y]``.
            By default, geographic line segments are drawn as great circle
            arcs. To draw them as straight lines, use *straight_line*.
            Alternatively, add **m** to draw the line by first following a
            meridian, then a parallel. Or append **p** to start following a
            parallel, then a meridian. (This can be practical to draw a line
            along parallels, for example). For Cartesian data, points are
            simply connected, unless you append **x** or **y** to draw
            stair-case curves that whose first move is along *x* or *y*,
            respectively. **Note**: The **straight_line** option requires
            constant *z*-coordinates.
        {B}
        {CPT}
        offset : str
            ``dx/dy[/dz]``.
            Offset the plot symbol or line locations by the given amounts
            *dx/dy*[*dz*] [Default is no offset].
        {G}
        intensity : float or bool
            Provide an *intens* value (nominally in the -1 to +1 range) to
            modulate the fill color by simulating illumination [None]. If
            using ``intensity=True``, we will instead read *intens* from the
            first data column after the symbol parameters (if given).
        close : str
            ``[+b|d|D][+xl|r|x0][+yl|r|y0][+ppen]``.
            Force closed polygons. Full documentation is at
            :gmt-docs:`plot3d.html#l`.
        no_clip : bool or str
            ``[c|r]``.
            Do NOT clip symbols that fall outside map border [Default plots
            points whose coordinates are strictly inside the map border only].
            The option does not apply to lines and polygons which are always
            clipped to the map region. For periodic (360-longitude) maps we
            must plot all symbols twice in case they are clipped by the
            repeating boundary. ``no_clip=True`` will turn off clipping and not
            plot repeating symbols. Use ``no_clip="r"`` to turn off clipping
            but retain the plotting of such repeating symbols, or use
            ``no_clip="c"`` to retain clipping but turn off plotting of
            repeating symbols.
        no_sort : bool
            Turn off the automatic sorting of items based on their distance
            from the viewer. The default is to sort the items so that items in
            the foreground are plotted after items in the background.
        style : str
            Plot symbols. Full documentation is at :gmt-docs:`plot3d.html#s`.
        {U}
        {V}
        {W}
        {XY}
        zvalue : str
            ``value|file``.
            Instead of specifying a symbol or polygon fill and outline color
            via **color** and **pen**, give both a *value* via **zvalue** and a
            color lookup table via **cmap**.  Alternatively, give the name of a
            *file* with one z-value (read from the last column) for each
            polygon in the input data. To apply it to the fill color, use
            ``color='+z'``. To apply it to the pen color, append **+z** to
            **pen**.
        label : str
            Add a legend entry for the symbol or line being plotted.
        {p}
        {t}
            *transparency* can also be a 1d array to set varying transparency
            for symbols.
        """
        kwargs = self._preprocess(**kwargs)

        kind = data_kind(data, x, y, z)

        extra_arrays = []
        if "S" in kwargs and kwargs["S"][0] in "vV" and direction is not None:
            extra_arrays.extend(direction)
        if "G" in kwargs and not isinstance(kwargs["G"], str):
            if kind != "vectors":
                raise GMTInvalidInput(
                    "Can't use arrays for color if data is matrix or file."
                )
            extra_arrays.append(kwargs["G"])
            del kwargs["G"]
        if sizes is not None:
            if kind != "vectors":
                raise GMTInvalidInput(
                    "Can't use arrays for sizes if data is matrix or file."
                )
            extra_arrays.append(sizes)

        if "t" in kwargs and is_nonstr_iter(kwargs["t"]):
            extra_arrays.append(kwargs["t"])
            kwargs["t"] = ""

        with Session() as lib:
            # Choose how data will be passed in to the module
            if kind == "file":
                file_context = dummy_context(data)
            elif kind == "matrix":
                file_context = lib.virtualfile_from_matrix(data)
            elif kind == "vectors":
                file_context = lib.virtualfile_from_vectors(
                    np.atleast_1d(x), np.atleast_1d(y), np.atleast_1d(z), *extra_arrays
                )

            with file_context as fname:
                arg_str = " ".join([fname, build_arg_string(kwargs)])
                lib.call_module("plot3d", arg_str)

    @fmt_docstring
    @use_alias(
        R="region",
        J="projection",
        B="frame",
        S="skip",
        G="label_placement",
        W="pen",
        L="triangular_mesh_pen",
        N="no_clip",
        i="columns",
        l="label",
        C="levels",
        V="verbose",
        X="xshift",
        Y="yshift",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", i="sequence_comma", p="sequence")
    def contour(self, x=None, y=None, z=None, data=None, **kwargs):
        """
        Contour table data by direct triangulation.

        Takes a matrix, (x,y,z) pairs, or a file name as input and plots lines,
        polygons, or symbols at those locations on a map.

        Must provide either *data* or *x*, *y*, and *z*.

        [TODO: Insert more documentation]

        Full option list at :gmt-docs:`contour.html`

        {aliases}

        Parameters
        ----------
        x/y/z : 1d arrays
            Arrays of x and y coordinates and values z of the data points.
        data : str or 2d array
            Either a data file name or a 2d numpy array with the tabular data.
        {J}
        {R}
        A : bool or str
            ``'[m|p|x|y]'``
            By default, geographic line segments are drawn as great circle
            arcs. To draw them as straight lines, use *A*.
        {B}
        levels : str
            Contour file or level(s)
        D : str
            Dump contour coordinates
        E : str
            Network information
        label_placement : str
            Placement of labels
        I : bool
            Color the triangles using CPT
        triangular_mesh_pen : str
            Pen to draw the underlying triangulation (default none)
        no_clip : bool
            Do NOT clip contours or image at the boundaries [Default will clip
            to fit inside region].
        Q : float or str
            Do not draw contours with less than cut number of points.
            ``'[cut[unit]][+z]'``
        skip : bool or str
            Skip input points outside region ``'[p|t]'``
        {W}
        label : str
            Add a legend entry for the contour being plotted. Normally, the
            annotated contour is selected for the legend. You can select the
            regular contour instead, or both of them, by considering the label
            to be of the format [*annotcontlabel*][/*contlabel*]. If either
            label contains a slash (/) character then use ``|`` as the
            separator for the two labels instead.
        {V}
        {XY}
        {p}
        {t}
        """
        kwargs = self._preprocess(**kwargs)

        kind = data_kind(data, x, y, z)
        if kind == "vectors" and z is None:
            raise GMTInvalidInput("Must provided both x, y, and z.")

        with Session() as lib:
            # Choose how data will be passed in to the module
            if kind == "file":
                file_context = dummy_context(data)
            elif kind == "matrix":
                file_context = lib.virtualfile_from_matrix(data)
            elif kind == "vectors":
                file_context = lib.virtualfile_from_vectors(x, y, z)

            with file_context as fname:
                arg_str = " ".join([fname, build_arg_string(kwargs)])
                lib.call_module("contour", arg_str)

    @fmt_docstring
    @use_alias(
        R="region",
        J="projection",
        Jz="zscale",
        JZ="zsize",
        B="frame",
        L="map_scale",
        Td="rose",
        Tm="compass",
        U="timestamp",
        V="verbose",
        X="xshift",
        Y="yshift",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", p="sequence")
    def basemap(self, **kwargs):
        """
        Plot base maps and frames for the figure.

        Creates a basic or fancy basemap with axes, fill, and titles. Several
        map projections are available, and the user may specify separate
        tick-mark intervals for boundary annotation, ticking, and [optionally]
        gridlines. A simple map scale or directional rose may also be plotted.

        At least one of the options *frame*, *map_scale*, *rose* or *compass*
        must be specified.

        Full option list at :gmt-docs:`basemap.html`

        {aliases}

        Parameters
        ----------
        {J}
        zscale/zsize : float or str
            Set z-axis scaling or z-axis size.
        {R}
        {B}
        map_scale : str
            ``'[g|j|J|n|x]refpoint'``
            Draws a simple map scale centered on the reference point specified.
        rose : str
            Draws a map directional rose on the map at the location defined by
            the reference and anchor points.
        compass : str
            Draws a map magnetic rose on the map at the location defined by the
            reference and anchor points
        {U}
        {V}
        {XY}
        {p}
        {t}
        """
        kwargs = self._preprocess(**kwargs)
        if not args_in_kwargs(args=["B", "L", "Td", "Tm"], kwargs=kwargs):
            raise GMTInvalidInput(
                "At least one of frame, map_scale, compass, or rose must be specified."
            )
        with Session() as lib:
            lib.call_module("basemap", build_arg_string(kwargs))

    @fmt_docstring
    @use_alias(
        R="region",
        J="projection",
        D="position",
        F="box",
        S="style",
        U="timestamp",
        V="verbose",
        X="xshift",
        Y="yshift",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", p="sequence")
    def logo(self, **kwargs):
        """
        Plot the GMT logo.

        By default, the GMT logo is 2 inches wide and 1 inch high and
        will be positioned relative to the current plot origin.
        Use various options to change this and to place a transparent or
        opaque rectangular map panel behind the GMT logo.

        Full option list at :gmt-docs:`gmtlogo.html`.

        {aliases}

        Parameters
        ----------
        {J}
        {R}
        position : str
            ``'[g|j|J|n|x]refpoint+wwidth[+jjustify][+odx[/dy]]'``.
            Sets reference point on the map for the image.
        box : bool or str
            Without further options, draws a rectangular border around the
            GMT logo.
        style : str
            ``l|n|u``.
            Control what is written beneath the map portion of the logo.

            - **l** to plot the text label "The Generic Mapping Tools"
              [Default]
            - **n** to skip the label placement
            - **u** to place the URL to the GMT site
        {U}
        {V}
        {XY}
        {t}
        """
        kwargs = self._preprocess(**kwargs)
        with Session() as lib:
            lib.call_module("logo", build_arg_string(kwargs))

    @fmt_docstring
    @use_alias(
        R="region",
        J="projection",
        D="position",
        F="box",
        M="monochrome",
        V="verbose",
        X="xshift",
        Y="yshift",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", p="sequence")
    def image(self, imagefile, **kwargs):
        """
        Place images or EPS files on maps.

        Reads an Encapsulated PostScript file or a raster image file and plots
        it on a map.

        Full option list at :gmt-docs:`image.html`

        {aliases}

        Parameters
        ----------
        imagefile : str
            This must be an Encapsulated PostScript (EPS) file or a raster
            image. An EPS file must contain an appropriate BoundingBox. A
            raster file can have a depth of 1, 8, 24, or 32 bits and is read
            via GDAL. Note: If GDAL was not configured during GMT installation
            then only EPS files are supported.
        {J}
        {R}
        position : str
            ``'[g|j|J|n|x]refpoint+rdpi+w[-]width[/height][+jjustify]
            [+nnx[/ny]][+odx[/dy]]'`` Sets reference point on the map for the
            image.
        box : bool or str
            ``'[+cclearances][+gfill][+i[[gap/]pen]][+p[pen]][+r[radius]]
            [+s[[dx/dy/][shade]]]'`` Without further options, draws a
            rectangular border around the image using **MAP_FRAME_PEN**.
        monochrome : bool
            Convert color image to monochrome grayshades using the (television)
            YIQ-transformation.
        {V}
        {XY}
        {p}
        {t}
        """
        kwargs = self._preprocess(**kwargs)
        with Session() as lib:
            arg_str = " ".join([imagefile, build_arg_string(kwargs)])
            lib.call_module("image", arg_str)

    @fmt_docstring
    @use_alias(
        R="region",
        J="projection",
        D="position",
        F="box",
        V="verbose",
        X="xshift",
        Y="yshift",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(R="sequence", p="sequence")
    def legend(self, spec=None, position="JTR+jTR+o0.2c", box="+gwhite+p1p", **kwargs):
        """
        Plot legends on maps.

        Makes legends that can be overlaid on maps. Reads specific
        legend-related information from an input file, or automatically creates
        legend entries from plotted symbols that have labels. Unless otherwise
        noted, annotations will be made using the primary annotation font and
        size in effect (i.e., FONT_ANNOT_PRIMARY).

        Full option list at :gmt-docs:`legend.html`

        {aliases}

        Parameters
        ----------
        spec : None or str
            Either None (default) for using the automatically generated legend
            specification file, or a filename pointing to the legend
            specification file.
        {J}
        {R}
        position : str
            ``'[g|j|J|n|x]refpoint+wwidth[/height][+jjustify][+lspacing]
            [+odx[/dy]]'`` Defines the reference point on the map for the
            legend. By default, uses 'JTR+jTR+o0.2c' which places the legend at
            the top-right corner inside the map frame, with a 0.2 cm offset.
        box : bool or str
            ``'[+cclearances][+gfill][+i[[gap/]pen]][+p[pen]][+r[radius]]
            [+s[[dx/dy/][shade]]]'`` Without further options, draws a
            rectangular border around the legend using **MAP_FRAME_PEN**. By
            default, uses '+gwhite+p1p' which draws a box around the legend
            using a 1 point black pen and adds a white background.
        {V}
        {XY}
        {p}
        {t}
        """
        kwargs = self._preprocess(**kwargs)

        if "D" not in kwargs:
            kwargs["D"] = position

            if "F" not in kwargs:
                kwargs["F"] = box

        with Session() as lib:
            if spec is None:
                specfile = ""
            elif data_kind(spec) == "file":
                specfile = spec
            else:
                raise GMTInvalidInput("Unrecognized data type: {}".format(type(spec)))
            arg_str = " ".join([specfile, build_arg_string(kwargs)])
            lib.call_module("legend", arg_str)

    @fmt_docstring
    @use_alias(
        R="region",
        J="projection",
        B="frame",
        C="clearance",
        D="offset",
        G="fill",
        N="no_clip",
        V="verbose",
        W="pen",
        X="xshift",
        Y="yshift",
        p="perspective",
        t="transparency",
    )
    @kwargs_to_strings(
        R="sequence",
        textfiles="sequence_space",
        angle="sequence_comma",
        font="sequence_comma",
        justify="sequence_comma",
        p="sequence",
    )
    def text(
        self,
        textfiles=None,
        x=None,
        y=None,
        position=None,
        text=None,
        angle=None,
        font=None,
        justify=None,
        **kwargs,
    ):
        """
        Plot or typeset text strings of variable size, font type, and
        orientation.

        Must provide at least one of the following combinations as input:

        - *textfiles*
        - *x*, *y*, and *text*
        - *position* and *text*

        Full option list at :gmt-docs:`text.html`

        {aliases}

        Parameters
        ----------
        textfiles : str or list
            A text data file name, or a list of filenames containing 1 or more
            records with (x, y[, angle, font, justify], text).
        x/y : float or 1d arrays
            The x and y coordinates, or an array of x and y coordinates to plot
            the text
        position : str
            Sets reference point on the map for the text by using x,y
            coordinates extracted from *region* instead of providing them
            through *x* and *y*. Specify with a two letter (order independent)
            code, chosen from:

            * Horizontal: L(eft), C(entre), R(ight)
            * Vertical: T(op), M(iddle), B(ottom)

            For example, position="TL" plots the text at the Upper Left corner
            of the map.
        text : str or 1d array
            The text string, or an array of strings to plot on the figure
        angle: int, float, str or bool
            Set the angle measured in degrees counter-clockwise from
            horizontal. E.g. 30 sets the text at 30 degrees. If no angle is
            explicitly given (i.e. angle=True) then the input textfile(s) must
            have this as a column.
        font : str or bool
            Set the font specification with format "size,font,color" where size
            is text size in points, font is the font to use, and color sets the
            font color. E.g. "12p,Helvetica-Bold,red" selects a 12p red
            Helvetica-Bold font. If no font info is explicitly given (i.e.
            font=True), then the input textfile(s) must have this information
            in one of its columns.
        justify : str or bool
            Set the alignment which refers to the part of the text string that
            will be mapped onto the (x,y) point. Choose a 2 character
            combination of L, C, R (for left, center, or right) and T, M, B for
            top, middle, or bottom. E.g., BL for lower left. If no
            justification is explicitly given (i.e. justify=True), then the
            input textfile(s) must have this as a column.
        {J}
        {R}
        clearance : str
            ``[dx/dy][+to|O|c|C]``
            Adjust the clearance between the text and the surrounding box
            [15%]. Only used if *pen* or *fill* are specified. Append the unit
            you want ('c' for cm, 'i' for inch, or 'p' for point; if not given
            we consult 'PROJ_LENGTH_UNIT') or '%' for a percentage of the
            font size. Optionally, use modifier '+t' to set the shape of the
            textbox when using *fill* and/or *pen*. Append lower case 'o' to
            get a straight rectangle [Default]. Append upper case 'O' to get a
            rounded rectangle. In paragraph mode (*paragraph*) you can also
            append lower case 'c' to get a concave rectangle or append upper
            case 'C' to get a convex rectangle.
        fill : str
            Sets the shade or color used for filling the text box [Default is
            no fill].
        offset : str
            ``[j|J]dx[/dy][+v[pen]]``
            Offsets the text from the projected (x,y) point by dx,dy [0/0]. If
            dy is not specified then it is set equal to dx. Use offset='j' to
            offset the text away from the point instead (i.e., the text
            justification will determine the direction of the shift). Using
            offset='J' will shorten diagonal offsets at corners by sqrt(2).
            Optionally, append '+v' which will draw a line from the original
            point to the shifted point; append a pen to change the attributes
            for this line.
        pen : str
            Sets the pen used to draw a rectangle around the text string
            (see *clearance*) [Default is width = default, color = black,
            style = solid].
        no_clip : bool
            Do NOT clip text at map boundaries [Default is False, i.e. will
            clip].
        {V}
        {XY}
        {p}
        {t}
        """

        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches

        kwargs = self._preprocess(**kwargs)

        # Ensure inputs are either textfiles, x/y/text, or position/text
        if position is None:
            kind = data_kind(textfiles, x, y, text)
        else:
            if x is not None or y is not None:
                raise GMTInvalidInput(
                    "Provide either position only, or x/y pairs, not both"
                )
            kind = "vectors"

        if kind == "vectors" and text is None:
            raise GMTInvalidInput("Must provide text with x/y pairs or position")

        # Build the `-F` argument in gmt text.
        if "F" not in kwargs.keys() and (
            (
                position is not None
                or angle is not None
                or font is not None
                or justify is not None
            )
        ):
            kwargs.update({"F": ""})
        if angle is not None and isinstance(angle, (int, float, str)):
            kwargs["F"] += f"+a{str(angle)}"
        if font is not None and isinstance(font, str):
            kwargs["F"] += f"+f{font}"
        if justify is not None and isinstance(justify, str):
            kwargs["F"] += f"+j{justify}"
        if position is not None and isinstance(position, str):
            kwargs["F"] += f'+c{position}+t"{text}"'

        extra_arrays = []
        # If an array of transparency is given, GMT will read it from
        # the last numerical column per data record.
        if "t" in kwargs and is_nonstr_iter(kwargs["t"]):
            extra_arrays.append(kwargs["t"])
            kwargs["t"] = ""

        with Session() as lib:
            file_context = dummy_context(textfiles) if kind == "file" else ""
            if kind == "vectors":
                if position is not None:
                    file_context = dummy_context("")
                else:
                    file_context = lib.virtualfile_from_vectors(
                        np.atleast_1d(x),
                        np.atleast_1d(y),
                        *extra_arrays,
                        # text must be in str type, see issue #706
                        np.atleast_1d(text).astype(str),
                    )
            with file_context as fname:
                arg_str = " ".join([fname, build_arg_string(kwargs)])
                lib.call_module("text", arg_str)

    # GMT Supplementary modules
    from pygmt.src import meca  # pylint: disable=import-outside-toplevel
