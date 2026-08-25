import os
import pandas as pd
import h5py
import numpy as np
from glob import glob
from tqdm import tqdm

granule_ids = []
campaign_name = 'East River 2018'
sensor_name = 'NEON AIS 1'
acquisition_dates = []
acquisition_start_times = []
cloudy_conditions = []
cloud_types = []
gsd = 1
raster_epsg = 32613
flightline_ids = []

keep = pd.read_csv('/store/carroll/sbgplants/out/2018/spectra.csv')
keep = keep['granule_id'].unique().tolist()

fps = glob('/store/carroll/col/data/2018/raw/L1/radianceH5/*/*.h5')

for fp in fps:
    try:
        with h5py.File(fp, "r") as f:
            time = f['CRBU/Radiance'].attrs['Acquisition_Time']
            cloud_condition = f['CRBU/Radiance/Radiance_Data'].attrs['Cloud conditions']
            cloud_type = f['CRBU/Radiance/Radiance_Data'].attrs['Cloud type']
        acquisition_date = time.split(',')[0]
        acquisition_start_time = time.split(',')[1].replace('[Computer Time in sec]', '').strip()
        granule_id = f'NIS01_{acquisition_date.replace("-", "")}_{acquisition_start_time}'
        flightline_id = granule_id
        cloud_condition = cloud_condition.split(' (')[0]
        
        if granule_id not in keep: # only keep where intersect plots
            continue
        
        acquisition_start_time = acquisition_start_time[:2] + ':' + acquisition_start_time[2:4] + ':' + acquisition_start_time[4:]
        print(acquisition_start_time)
        granule_ids.append(granule_id)
        acquisition_dates.append(acquisition_date)
        acquisition_start_times.append(acquisition_start_time)
        cloudy_conditions.append(cloud_condition)
        cloud_types.append(cloud_type)
    except Exception as e:
        print(fp)

print(acquisition_start_times)

df = pd.DataFrame({
    'granule_id': granule_ids, 
    'campaign_name': campaign_name,
    'sensor_name': sensor_name,
    'acquisition_date': acquisition_dates,
    'acquisition_start_time': acquisition_start_times,
    'cloudy_conditions': cloudy_conditions,
    'cloud_type': cloud_types,
    'gsd': gsd,
    'raster_epsg': raster_epsg,
    'flightline_id': granule_ids,
    'granule_rad_url': ['https://data.ess-dive.lbl.gov/datasets/doi:10.15485/3017966 '] * len(granule_ids),
    'granule_refl_url': ['https://data.ess-dive.lbl.gov/datasets/doi:10.15485/3013527'] * len(granule_ids)
})

df['cloudy_conditions'] = df['cloudy_conditions'].str.lower()
df['cloud_type'] = df['cloud_type'].str.lower()

df.to_csv('/store/carroll/sbgplants/out/2018/granule_metadata.csv', index=False)
