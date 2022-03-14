#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 20:53:37 2022

@author: krugernyasulu
"""
import cdsapi
import datetime
import os

#++++++++++++ Customization
file_format = 'netcdf'  # 'grib' or 'netcdf' (but ONLY netcdf is supported by the code below for mapping and time serie extraction)
folder_out = r'/home/kruger/data/utrack/input/era5/'
downloaded_file = 'ERA5-Land hourly.nc'

year=int([
    '2004', '2005', '2006',
    '2007', '2008', '2009',
    '2010', '2011', '2012',])
c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-land',
    {
        'format': 'netcdf',
        'variable': 'total_evaporation',
        'year': [
            '2004', '2005', '2006',
            '2007', '2008', '2009',
            '2010', '2011', '2012',
        ],
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
        ],
        'area': [
            50, -30, -60,
            70,
        ],
    })
    r.download('era5_evapotranspiration_monthly'+str(month).zfill(2)+str(year)+'.nc'))

import cdsapi
import sys

year=int(sys.argv[1])
month=int(sys.argv[2])
day=int(sys.argv[3])
c = cdsapi.Client()
print (year,month,day)

r = c.retrieve(
    'reanalysis-era5-single-levels',
    {
    'variable':['evaporation','total_precipitation'],
        'product_type':'reanalysis',
        'year':str(year),
        'month':str(month).zfill(2),
        'day':str(day).zfill(2),
        'time':[
            '00:00','01:00','02:00',
            '03:00','04:00','05:00',
            '06:00','07:00','08:00',
            '09:00','10:00','11:00',
            '12:00','13:00','14:00',
            '15:00','16:00','17:00',
            '18:00','19:00','20:00',
            '21:00','22:00','23:00'
        ],
        'format':'netcdf'
    })
r.download('era5_evapotranspiration_monthly'+str(month).zfill(2)+str(month).zfill(2)+str(year)+'.nc')



