"""iceplot.plot

Provide the actual plotting interface
"""

import numpy as np
from matplotlib import pyplot as mplt
from matplotlib import colors as mcolors

from iceplot import cm as icm
from iceplot import figure as ifig

### Figure functions ###

def gridfigure(mapsize, nrows_ncols, **kwargs):
    """Create a new figure and return an :class:iceplot.figure.GridFigure instance"""
    return mplt.figure(FigureClass=ifig.GridFigure,
      mapsize=mapsize, nrows_ncols=nrows_ncols, **kwargs)

def simplefigure(mapsize, **kwargs):
    """Create a new figure and return a :class:iceplot.figure.SimpleFigure instance"""
    return mplt.figure(FigureClass=ifig.SimpleFigure,
      mapsize=mapsize, **kwargs)

def doubleinlinefigure(mapsize, **kwargs):
    """Create a new figure and return a :class:iceplot.figure.DoubleInlineFigure instance"""
    return mplt.figure(FigureClass=ifig.DoubleInlineFigure,
      mapsize=mapsize, **kwargs)

### Data extraction ###

def _extract(nc, varname, t):
    var = nc.variables[varname]
    """Extract data from a netcdf file"""

    if t == 'djf':
      return var[[12,0,1]].mean(axis=2).T
    if t == 'mam':
      return var[2:5].mean(axis=2).T
    if t == 'jja':
      return var[6:8].mean(axis=2).T
    if t == 'son':
      return var[9:11].mean(axis=2).T
    if t == 'mean':
      return var[:].mean(axis=2).T
    else:
      return var[t].T

### Image mapping functions ###

def bedtopoimage(nc, t=0, **kwargs):
    """Draw bedrock topography."""
    topo = _extract(nc, 'topg', t)
    return mplt.imshow(topo,
      cmap = kwargs.pop('cmap', icm.topo),
      norm = kwargs.pop('norm', mcolors.Normalize(-6000,6000)),
      **kwargs)

def surftopoimage(nc, t=0, **kwargs):
    """Draw ice surface topography."""
    topo = _extract(nc, 'usurf', t)
    return mplt.imshow(topo,
      cmap = kwargs.pop('cmap', icm.land_topo),
      norm = kwargs.pop('norm', mcolors.Normalize(0,6000)),
      **kwargs)

def basetempimage(nc, t=0, **kwargs):
    """Draw pressure-adjusted basal temperature."""
    thk   = _extract(nc, 'thk', t)
    temp  = _extract(nc, 'temppabase', t)
    temp  = np.ma.masked_where(thk < 1, temp)
    return mplt.imshow(temp,
      cmap = kwargs.pop('cmap', mplt.cm.Blues_r),
      norm = kwargs.pop('norm', mcolors.Normalize(-10, 0)),
      **kwargs)

def airtempimage(nc, t=0, **kwargs):
    """Draw near-surface air temperature."""
    temp = _extract(nc, 'air_temp', t)
    return mplt.imshow(temp,
      cmap = kwargs.pop('cmap', mplt.cm.Spectral_r),
      norm = kwargs.pop('norm', mcolors.Normalize(-30,30)),
      **kwargs)

def precipimage(nc, t=0, **kwargs):
    """Draw precipitation rate."""
    prec = _extract(nc, 'precipitation', t)
    return mplt.imshow(prec,
      cmap = kwargs.pop('cmap', mplt.cm.YlGnBu),
      norm = kwargs.pop('norm', mcolors.LogNorm(0.1,10)),
      **kwargs)

def _icevelimage(nc, t=0, surf='surf', **kwargs):
    """Draw ice velocity."""
    thk = _extract(nc, 'thk', t)
    c   = _extract(nc, 'c'+surf, t)
    c   = np.ma.masked_where(thk < 1, c)
    return mplt.imshow(c,
      cmap = kwargs.pop('cmap', icm.velocity),
      norm = kwargs.pop('norm', mcolors.LogNorm(10, 10000)),
      **kwargs)

def basevelimage(nc, t=0, **kwargs):
    """Draw basal velocity."""
    return _icevelimage(nc, t, 'base', **kwargs)

def surfvelimage(nc, t=0, **kwargs):
    """Draw surface velocity."""
    return _icevelimage(nc, t, 'surf', **kwargs)

### Contour mapping functions ###

def _contours(*args, **kwargs):
    """Wrap :func:`~matplotlib.pyplot.contour` and :func:`~matplotlib.pyplot.contours` in a single function."""

    # pop out all special arguments
    colors     = kwargs.pop('colors', None)
    cmap       = kwargs.pop('cmap', None)
    linecolors = kwargs.pop('linecolors', None)
    linecmap   = kwargs.pop('linecmap', None)
    linewidths = kwargs.pop('linewidths', None)
    linestyles = kwargs.pop('linestyles', None)

    # check for filled and lined contours arguments
    has_fill_args = any((colors, cmap))
    has_line_args = any((linecolors, linecmap, linewidths, linestyles))

    # plot filled contours
    cf = None
    if has_fill_args or not has_line_args:
      cf = mplt.contourf(*args,
        cmap   = cmap,
        colors = colors,
        **kwargs)

    # plot lined contours
    cl = None
    if has_line_args or not has_fill_args:
      cl = mplt.contour(*args,
        colors     = linecolors,
        cmap       = linecmap,
        linewidths = linewidths,
        linestyles = linestyles,
        **kwargs)

    # return filled or lined contour set
    return cf or cl

def icemargincontour(nc, t=0, **kwargs):
    """Draw a contour along the ice margin."""
    thk = _extract(nc, 'thk', t)
    return _contours(thk,
      levels     = [kwargs.pop('level', 1), np.inf],
      linecolors = kwargs.pop('linecolors', 'black'),
      **kwargs)

def surftopocontour(nc, t=0, **kwargs):
    """Draw ice surface topography contours."""
    thk   = _extract(nc, 'thk', t)
    usurf = _extract(nc, 'usurf', t)
    usurf = np.ma.masked_where(thk < 1, usurf)
    return _contours(usurf,
      levels     = kwargs.pop('levels', range(1000, 5000, 1000)),
      linecolors = kwargs.pop('linecolors', 'black'),
      linewidths = kwargs.pop('linewidths', 0.5),
      **kwargs)

def basetempcontour(nc, t=0, **kwargs):
    """Draw pressure-adjusted bed temperature contours."""
    thk   = _extract(nc, 'thk', t)
    temp  = _extract(nc, 'temppabase', t)
    temp  = np.ma.masked_where(thk < 1, temp)
    return _contours(temp,
      levels     = kwargs.pop('levels', [-10, -8, -6, -4, -2, -1e-6]),
      cmap       = kwargs.pop('cmap', mplt.cm.Blues_r),
      extend     = kwargs.pop('extend', 'both'),
      linewidths = kwargs.pop('linewidths', 0.2),
      linecolors = kwargs.pop('linecolors', 'black'),
      linestyles = kwargs.pop('linestyles', 'solid'),
      **kwargs)

def airtempcontour(nc, t=0, **kwargs):
    """Draw near-surface air temperature contours."""
    temp = _extract(nc, 'air_temp', t) - 273.15
    return _contours(temp,
      levels     = kwargs.pop('levels', range(-30, 31, 5)),
      cmap       = kwargs.pop('cmap', mplt.cm.Spectral_r),
      norm       = kwargs.pop('norm', mcolors.Normalize(-30,30)),
      linewidths = kwargs.pop('linewidths', 0.2),
      linecolors = kwargs.pop('linecolors', 'black'),
      linestyles = kwargs.pop('linestyles', 'solid'),
      **kwargs)

def precipcontour(nc, t=0, **kwargs):
    """Draw precipitation rate contours."""
    prec = _extract(nc, 'precipitation', t)
    return _contours(prec,
      levels     = kwargs.pop('levels', [0.1, 0.2, 0.5, 1, 2, 5, 10]),
      cmap       = kwargs.pop('cmap', mplt.cm.YlGnBu),
      norm       = kwargs.pop('norm', mcolors.LogNorm(0.1,10)),
      linewidths = kwargs.pop('linewidths', 0.2),
      linecolors = kwargs.pop('linecolors', 'black'),
      **kwargs)

def _icevelcontour(nc, t=0, surf='surf', **kwargs):
    """Draw ice velocity contours."""
    thk = _extract(nc, 'thk', t)
    c   = _extract(nc, 'c'+surf, t)
    c   = np.ma.masked_where(thk < 1, c)
    return _contours(c,
      levels     = kwargs.pop('levels', [10,30,100,300,1000,3000,10000]),
      cmap       = kwargs.pop('cmap', icm.velocity),
      norm       = kwargs.pop('norm', mcolors.LogNorm(10, 10000)),
      linewidths = kwargs.pop('linewidths', 0.2),
      linecolors = kwargs.pop('linecolors', 'black'),
      **kwargs)

def basevelcontour(nc, t=0, **kwargs):
    """Draw basal velocity contours."""
    return _icevelcontour(nc, t, 'base', **kwargs)

def surfvelcontour(nc, t=0, **kwargs):
    """Draw surface velocity contours."""
    return _icevelcontour(nc, t, 'surf', **kwargs)

### Quiver mapping functions ###

def _icevelquiver(nc, t=0, surf='surf', **kwargs):
    """Draw ice velocity quiver"""
    thk = _extract(nc, 'thk', t)
    u = _extract(nc, 'uvel'+surf, t)
    v = _extract(nc, 'vvel'+surf, t)
    c = _extract(nc, 'c'+surf, t)
    scale = kwargs.pop('scale', 100)
    u = np.sign(u)*np.log(1+np.abs(u)/scale)
    v = np.sign(v)*np.log(1+np.abs(v)/scale)
    u = np.ma.masked_where(thk < 1, u)
    v = np.ma.masked_where(thk < 1, v)
    return mplt.quiver(u, v, c,
      scale = scale,
      cmap = kwargs.pop('cmap', icm.velocity),
      norm = kwargs.pop('norm', mcolors.LogNorm(10, 10000)),
      **kwargs)

def basevelquiver(nc, t=0, **kwargs):
    """Draw basal velocity quiver"""
    return _icevelquiver(nc, t, 'base', **kwargs)

def surfvelquiver(nc, t=0, **kwargs):
    """Draw basal velocity quiver"""
    return _icevelquiver(nc, t, 'surf', **kwargs)

### Composite mapping functions ###

def icemap(nc, t=0, **kwargs):
    """Draw basal topography, surface velocity and elevation contours."""

    # draw bed topography
    bedtopoimage(nc, t,
      **{kw: kwargs['bedtopo_'+kw]
        for kw in ('cmap', 'norm') if 'bedtopo_'+kw in kwargs})

    # draw surface velocities
    im = surfvelimage(nc, t,
      **{kw: kwargs['surfvel_'+kw]
        for kw in ('cmap', 'norm') if 'surfvel_'+kw in kwargs})

    # draw surface topography contours
    surftopocontour(nc, t,
      **{kw: kwargs['surftopo_'+kw]
        for kw in ('levels', 'linecolors') if 'surftopo_'+kw in kwargs})

    # draw ice margin contour
    icemargincontour(nc, t)

    # return surface velocity image
    return im

