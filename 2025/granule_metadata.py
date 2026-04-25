import os
import pandas as pd
import h5py
import numpy as np
from glob import glob
from tqdm import tqdm

granule_ids = []
campaign_name = 'Colorado Headwaters Ecological Spectroscopy Study'
sensor_name = 'NEON AIS 1'
acquistion_dates = []
acquistion_start_times = []
cloudy_conditions = []
cloud_types = []
gsd = 1
raster_epsg = 32613
flightline_ids = []

keep = pd.read_csv('/store/carroll/sbgplants/out/2025/spectra.csv')
keep = keep['granule_id'].unique().tolist()

fps = glob('/store/carroll/col/data/2025/raw/L1/radianceH5/*.h5')
for fp in fps:
    with h5py.File(fp, "r") as f:
        time = f['CRBU/Radiance'].attrs['Acquisition_Time']
        cloud_condition = f['CRBU/Radiance/RadianceDecimalPart'].attrs['Cloud conditions']
        cloud_type = f['CRBU/Radiance/RadianceDecimalPart'].attrs['Cloud type']
    acquistion_date = time.split(',')[0]
    acquistion_start_time = time.split(',')[1].replace('[Computer Time in sec]', '').strip()
    granule_id = f'NIS01_{acquistion_date.replace("-", "")}_{acquistion_start_time}'
    flightline_id = granule_id
    cloud_condition = cloud_condition.split(' (')[0]

            
    if granule_id not in keep: # only keep where intersect plots
        continue

    granule_ids.append(granule_id)
    acquistion_dates.append(acquistion_date)
    acquistion_start_times.append(acquistion_start_time)
    cloudy_conditions.append(cloud_condition)
    cloud_types.append(cloud_type)
df = pd.DataFrame({
    'granule_id': granule_ids, 
    'campaign_name': campaign_name,
    'sensor_name': sensor_name,
    'acquisition_date': acquistion_dates,
    'acquisition_start_time': acquistion_start_times,
    'cloudy_conditions': cloudy_conditions,
    'cloud_type': cloud_types,
    'gsd': gsd,
    'raster_epsg': raster_epsg,
    'flightline_id': granule_ids,
    'granule_rad_url': [None] * len(granule_ids),
    'granule_refl_url': [None] * len(granule_ids)
})
df.to_csv('out/2025/granule_metadata.csv', index=False)
