import xarray as xr
import numpy as np
import scipy as cp
from scipy.signal import hilbert

import geoviews as gv
import geoviews.feature as gf

from cartopy import crs
from geoviews import opts

from pyresample import AreaDefinition

import holoviews as hv
from holoviews import opts
from holoviews.plotting.links import RangeToolLink

hv.extension('bokeh')
gv.extension('bokeh')

#plot raw geographic netcdf
def fastplot(dframe, var, coords, raxis, cm='Jet'):
    lcoords = len(coords)
    if lcoords == 2:
        gvdata = gv.Dataset(dframe, kdims=[coords[0], coords[1], raxis], vdims=var)
        back = gvdata.to(gv.Image, [coords[0], coords[1]], var)
        return gv.output(back.opts(colorbar=True, backend='bokeh', cmap=cm, width=600, height=400), backend='bokeh')
    else:
        print("Incomplete coordinates")
def shapeplot(dframe, var, coords, raxis, cm='Jet_r', extralayers=[], lcolor = 'black'):
    lcoords = len(coords)
    xly = len(extralayers)
    if lcoords == 2 and xly > 0:
        gvdata = gv.Dataset(dframe, kdims=[coords[0], coords[1], raxis], vdims=var)
        back = gvdata.to(gv.Image, [coords[0], coords[1]], var)
        back = back.opts(colorbar=True, backend='bokeh', cmap=cm, width=600, height=400)
        for layer in extralayers:
            ss = gv.Shape.from_shapefile(layer).opts(line_color = lcolor)
            back *= ss
        return gv.output(back.opts(width=600, height=400), backend='bokeh')
    else:
        print("Incomplete coordinates")
