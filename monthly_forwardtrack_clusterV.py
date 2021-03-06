#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 00:44:00 2022

 @author: krugernyasulu

 Master Code from Chandrakant Singh 

"""

import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy
import numpy as np
from tqdm import tqdm, tnrange
import pandas as pd


"""
1a. Directory
"""
outputdir = '/p/projects/open/Kruger/utrack/output/'
inputdir = '/p/projects/open/Kruger/utrack/input/'
plotsdir = '/p/projects/open/Kruger/utrack/plots/'


"""
1b. Load your evaporation dataset here
"""
print('To run the model, your data format should be:')
print('Latitude = [ 90 → -90 ]')
print('Longitude = [ 0 → 360 ]')
print(' ')
Evap_agg = xr.open_mfdataset(inputdir+'/home/chandra/data/Paper4_Self-influencing_feedback/ERA5_monthly/era5_evaporation_monthly_*_p25.nc').__xarray_dataarray_variable__; # 0.5 degree resolution

# Convert to multi-year mean
Evap_agg = Evap_agg.groupby('time.month').mean(dim = 'time')
Evap_agg = (Evap_agg.where(Evap_agg >= 0))

print('Your Evaporation data:')
print('Latitude = [', Evap_agg.lat[0].values, '→', Evap_agg.lat[-1].values, ']')
print('Longitude = [', Evap_agg.lon[0].values, '→', Evap_agg.lon[-1].values, ']')

"""
2. Load your dataset for forwardtracking in Dataframe format
Note: Longitude should be from 0 to 360 degrees 
"""
Data = xr.open_dataset(inputdir+'Afric_TropcForest.nc').get("htrop_forest_20km") 
# Run this part to convert latitude 90:-90 & longitude 0:360 
lon = Data.longitude
lon = lon.values
Data = Data.assign_coords(longitude=np.where(lon>= 0,lon,lon+360))
Data = Data.sortby(Data.longitude)

Screening = (Data/Data.values) # Classifies the sink regions to 1 

lat = []
lon = []
Screened_data = []
for y in range(Screening.shape[0]):
    for x in range(Screening.shape[1]):
        if np.isnan(Screening[y,x].values) == True:
            continue
        else:
            lat.append(round(float(Screening[y,x].latitude.values),2)) #
            lon.append(round(float(Screening[y,x].longitude.values),2))
            Screened_data.append(Screening[y,x].values)

# Extraxt the data as dataframe
Screened_data = pd.DataFrame({'Lat': lat,'Lon': lon,'Screened': Screened_data})

####### Only for trial run 
#Screened_data = Screened_data1[0:10]
#Screened_data = Screened_data.where(Screened_data['Lat'] == 0.25).dropna()[0:10]


"""
3. Funtion for backtracking (both monthly and annual) 
"""
def MR_yearly_sink(source_lat, source_lon):
    global Evap_footprint_annual, Evap_footprint_monthly
    Evap_footprint_monthly = np.zeros(shape=(12,360,720))
    Evap_footprint_monthly[:] = np.nan
    Evap_footprint_annual = np.zeros(shape=(360,720))
    Evap_footprint_annual[:] = np.nan

    month_name = ['01','02','03','04','05','06','07','08','09','10','11','12']
    for i in (range(12)):
        MR = xr.open_dataset(inputdir+'utrack_climatology/utrack_climatology_0.5_'+
                                                     str(month_name[i])+'.nc').moisture_flow
        source = MR.sel(sourcelat = source_lat, sourcelon= source_lon, method = 'nearest')
        source = source.where(source != 255)
        source.values = np.exp(source.values*-0.1)
        Evap = (Evap_agg[i]).sel(lat = source_lat, lon = source_lon, method = 'nearest')
        Evap_footprint_monthly[i] = (Evap.values*source.values)
        #print('Recy-total', np.nansum(Evap_footprint_monthly[i]),' ,','Evap',Evap.values.sum())
    Evap_footprint_annual = np.nansum(Evap_footprint_monthly,axis = 0)
    MR.close()
    source.close()

"""
4. Running the forwardtrack code for the screened dataframe 
"""
Evap_footprint_annual_sum = 0
Evap_footprint_monthly_sum = 0
#### Run in parallel by changing dataframe range 
for i in tqdm(range(Screened_data.shape[0])):
    source_lat, source_lon = np.array(Screened_data[['Lat','Lon']])[i]
    MR_yearly_sink(source_lat,source_lon)
    Evap_footprint_annual_sum += Evap_footprint_annual
    Evap_footprint_monthly_sum += Evap_footprint_monthly

"""
5. Saving the dataset as NetCDF 
"""
Evap_footprint_annual_sum = xr.DataArray(Evap_footprint_annual_sum, coords=[Evap_agg.lat.values, Evap_agg.lon.values],
             dims=['lat', 'lon'], name = 'Evap_footprint', attrs=dict(description="Evaporation Footprint", units="mm/year"))

Evap_footprint_monthly_sum = xr.DataArray(Evap_footprint_monthly_sum, coords=[Evap_agg.month.values, Evap_agg.lat.values, Evap_agg.lon.values],
             dims=['month', 'lat', 'lon'], name = 'Evap_footprint', attrs=dict(description="Evaporation Footprint", units="mm/month"))
# Change name here for saving file
Evap_footprint_annual_sum.to_netcdf(outputdir+'Forwardtracking_Evap_footprint_annual_sum.nc')
Evap_footprint_monthly_sum.to_netcdf(outputdir+'Forwardtracking_Evap_footprint_monthly_sum.nc')

"""
6. Plotting the results
"""
fig = plt.figure(figsize=(3.5, 2.5), dpi = 200)
ax = [plt.subplot(111,projection=ccrs.PlateCarree(), aspect='auto')]
Evap_footprint_annual_sum.plot(ax = ax[0], transform=ccrs.PlateCarree(), vmin = 0, cmap = 'viridis_r',)
ax[0].coastlines(lw = 1)
ax[0].add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.3)
ax[0].set_xlim(-20,60)
ax[0].set_ylim(-40, 20)
ax[0].scatter(np.array(Screened_data['Lon']), np.array(Screened_data['Lat']), c='red', alpha = 0.7, s = .5, marker = '.')
ax[0].set_title('Forwardtracking: mm/year')
plt.savefig(plotsdir+'Forwardtracking.png')


fig = plt.figure(figsize=(3.5, 2.5), dpi = 200)
ax = [plt.subplot(111,projection=ccrs.PlateCarree(), aspect='auto')]
Evap_agg.plot(ax = ax[0], transform=ccrs.PlateCarree(), vmin = 0, cmap = 'viridis_r',)
ax[0].coastlines(lw = 1)
ax[0].add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.3)





