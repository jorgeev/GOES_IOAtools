#!/usr/bin/env python
# coding: utf-8
# NECDF from GOES for OWGIS, xarray only V2

import xarray as xr
import numpy as np
import scipy as cp
from glob import glob
from pyresample.geometry import AreaDefinition
from pyresample import image

# Path to storage folder
path = '/home/jorge/Storage/nc/*CMIP*C13*.nc'
files = sorted(glob(path))
doy = str.split(str.split(files[0],'/')[-1],'s2019')[-1][:3]

# NEW NETCDF name
newnc = '/home/jorge/Storage/nc/xarray_test_%s_OWCDF.nc'%doy
f0 = xr.open_dataset(files[0])
x = xr.open_dataset(files[0]).load().x.data
y = xr.open_dataset(files[0]).load().y.data

# Area Definition GOES
def goesAD(f0):
    area_id = 'GOES_R'
    description = 'FullDisk GOES-R Projection'
    proj_id = 'GOES_R'
    projection = {'proj': 'geos',
            'h': 1000 * f0.nominal_satellite_height.data,
            'lat_0': f0.geospatial_lat_lon_extent.geospatial_lat_center,
            'lon_0': f0.geospatial_lat_lon_extent.geospatial_lon_center,
            'a': f0.goes_imager_projection.semi_major_axis,
            'b': f0.goes_imager_projection.semi_minor_axis,
            'units': 'meters',
            'sweep': f0.goes_imager_projection.sweep_angle_axis,
            'ellps': 'GRS80'}

    width = 5424
    height = 5424
    h = 1000 * f0.nominal_satellite_height.data
    x_l = h * x[0]
    x_r = h * x[-1]
    y_l = h * y[-1]
    y_u = h * y[0]
    x_half = (x_r - x_l) / (width - 1) / 2.
    y_half = (y_u - y_l) / (height - 1) / 2.
    area_extent = (x_l - x_half, y_l - y_half, x_r + x_half, y_u + y_half)

    goesproj = AreaDefinition(area_id = area_id, 
                          description = description, 
                          proj_id = proj_id, 
                          projection = projection, 
                          width = width, height = height, 
                          area_extent = area_extent)
    
    return goesproj

def IOAD1():
    # Dominio 1 remuestreado a aprox 1'
    area_id = 'IOA_D1'
    description = 'Dominio 1 Grupo IOA'
    proj_id = 'IOA_D1'
    projection = '+init=EPSG:4326'
    width = 2909
    height = 2058
    area_extent = (-123.3613, 4.1260, -74.8779, 38.4260)
    #width = 2910
    #height = 2179
    #area_extent = (-123.3663889, 4., -74.3663889, 40.)
    ioa1 = AreaDefinition(area_id = area_id, 
                         description = description, 
                         proj_id = proj_id, 
                         projection = projection, 
                         width = width, height = height, 
                         area_extent = area_extent)
    return ioa1

ioa1 = IOAD1()
ioa_lon, ioa_lat = ioa1.get_lonlats()
ioa_lon = ioa_lon[0,:]
ioa_lat = ioa_lat[:,0]


# Initialize vector coordinates for Dataset
arr = np.empty([ioa_lat.shape[0], ioa_lon.shape[0], len(files)])
tt = np.empty([len(files)], dtype = 'datetime64[s]')
for ii in range(len(files)):
    xc = xr.open_dataset(files[ii]).load()
    goesproj = goesAD(xc)
    arr[:,:,ii] = image.ImageContainerNearest(np.round(xc.CMI.data, decimals=6), goesproj, radius_of_influence=10000, nprocs=8).resample(ioa1).image_data
    tt[ii] = xc.t.data


# NEW xarray Dataset
nwnc = xr.Dataset(coords={'lon': ('lon' , ioa_lon), 'lat': ('lat', ioa_lat), 'time': tt})
nwnc['CMI'] = (['lat', 'lon', 'time'], arr)
# Remove variables
del arr, tt, xc


# Basic Attributes for the new NETCDF
nwnc.time.attrs['axis'] = "time"
nwnc.CMI.attrs['units'] = "K"
nwnc.CMI.attrs['axis'] = "lat lon time"
nwnc.CMI.attrs['sensor_band_bit_depth'] = 12
nwnc.lon.attrs['units'] = "degree"
nwnc.lon.attrs['axis'] = 'lon'
nwnc.lat.attrs['units'] = "degree"
nwnc.lat.attrs['axis'] = 'lat'

# Write NEW NETCDF
nwnc.to_netcdf(path=newnc, format='netCDF4', 
               encoding = {'CMI': {'_FillValue': -273.15, 'zlib': True, 'complevel' : 9}, 'time' : {'units':'seconds since 2000-01-01 12:00:00', 'calendar':'gregorian'}})


