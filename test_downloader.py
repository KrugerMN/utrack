#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 17:22:30 2022

@author: krugernyasulu
"""
import cdsapi
import timeit
import os

# +++++++ Customization
file_format = 'netcdf'  # 'grib' or 'netcdf' (but ONLY netcdf is supported by the code below for mapping and time serie extraction)
# folder_nc = r'/home/kruger/data/utrack/input/era5'
folder_nc = r'/home/kruger/data/utrack/input/era5/'
# downloaded_file = 'era5_evapotranspiration_monthly_2004-2014.nc'
#('era5_evapotranspiration_monthly'+str(month).zfill(2)+str(month).zfill(2)+str(year)+'.nc')

# ....... PERIOD to extract
start_year = 2004                                          # from 1981 
end_year = 2006                                              # to present year

# ....... VARIABLE(S) to extract: single name or list of names among those below
#         - total_precipitation, surface_runoff,  runoff, snow_depth_water_equivalent (m)
#         - 2m_temperature (K)
#         - potential_evaporation, total_evaporation, evaporation_from_open_water_surfaces_excluding_ocean, evaporation_from_bare_soil (m negative)
variables_list = ['total_evaporation',
                  #'total_precipitation',
                 ]

# +++++++ Download
years = [ str(start_year +i ) 
         for i in range(end_year - start_year + 1)]
# if not os.path.exists(folder_nc): os.mkdir(folder_nc)
# downloaded_file = os.path.join(folder_nc, downloaded_file)

print('Process started. Please wait the ending message ... ')
start = timeit.default_timer()
c = cdsapi.Client()
for i in range(len(years)):
    c.retrieve(
        'reanalysis-era5-land-monthly-means',
        {
            'format': file_format,                                  
            'product_type': 'monthly_averaged_reanalysis',
            'variable': variables_list,                   
            'year': years[i],
            'month': [ '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12' ],
            'time': '00:00',
            'area': [
                50, -30, -60,
                70,],
            },# downloaded_file
        (folder_nc+'era5_evapotranspiration_monthly'+str(years[i])+'p25.nc')
        )

stop = timeit.default_timer()
print('Process completed in ', (stop - start)/60, ' minutes')