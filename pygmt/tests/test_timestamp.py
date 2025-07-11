"""
Test Figure.timestamp.
"""

import pytest
from pygmt import Figure
from pygmt.exceptions import GMTInvalidInput


@pytest.fixture(scope="module", name="faketime")
def fixture_faketime():
    """
    Fake datetime that will be passed to the "timefmt" parameter, so that the timestamp
    string always has a fixed value.
    """
    return "9999-99-99T99:99:99"


@pytest.mark.mpl_image_compare
def test_timestamp(faketime):
    """
    Test that the simplest timestamp() call works.
    """
    fig = Figure()
    fig.timestamp(timefmt=faketime)
    return fig


@pytest.mark.mpl_image_compare
def test_timestamp_label(faketime):
    """
    Check if the "label" parameter works.
    """
    fig = Figure()
    fig.timestamp(label="Powered by PyGMT", timefmt=faketime)
    return fig


@pytest.mark.mpl_image_compare
def test_timestamp_justify():
    """
    Check if the "justify" parameter works.

    Only a subset of justification codes are tested to avoid overlapping timestamps.
    """
    fig = Figure()
    fig.basemap(projection="X10c/5c", region=[0, 10, 0, 5], frame=0)
    for just in ["BL", "BR", "TL", "TR"]:
        fig.timestamp(justify=just, timefmt=just)
    return fig


@pytest.mark.mpl_image_compare
def test_timestamp_offset():
    """
    Check if the "offset" parameter works.
    """
    fig = Figure()
    fig.basemap(projection="X10c/5c", region=[0, 10, 0, 5], frame="g1")
    for offset in ["1c", "1c/2c", ("1c", "3c"), 4, (4, 1)]:
        fig.timestamp(offset=offset, timefmt=f"offset={offset}")
    return fig


@pytest.mark.benchmark
@pytest.mark.mpl_image_compare
def test_timestamp_font(faketime):
    """
    Test if the "font" parameter works.
    """
    fig = Figure()
    fig.timestamp(font="Times-Roman", label="Powered by GMT", timefmt=faketime)
    return fig


@pytest.mark.mpl_image_compare(filename="test_timestamp.png")
def test_timestamp_text(faketime):
    """
    Test if the "text" parameter works.
    """
    fig = Figure()
    fig.timestamp(text=faketime)
    return fig


@pytest.mark.mpl_image_compare
def test_timestamp_text_truncated():
    """
    Passing a text string longer than 64 characters raises a warning and the string will
    be truncated.
    """
    fig = Figure()
    with pytest.warns(expected_warning=RuntimeWarning) as record:
        # a string with 70 characters will be truncated to 64 characters
        fig.timestamp(text="0123456789" * 7)
    assert len(record) == 1  # check that only one warning was raised
    return fig


def test_timestamp_unsupported_u_timestamp():
    """
    Raise an exception when either U or timestamp is used.

    Parameters U and timestamp are no longer supported since v0.12.0.
    """
    fig = Figure()
    with pytest.raises(GMTInvalidInput):
        fig.plot(x=0, y=0, style="p", projection="X1c", region=[1, 2, 1, 2], U=True)
    with pytest.raises(GMTInvalidInput):
        fig.plot(
            x=0, y=0, style="p", projection="X1c", region=[1, 2, 1, 2], timestamp=True
        )
