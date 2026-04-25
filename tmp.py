import os
import pandas as pd
import geopandas as gpd
import numpy as np
import h5py
from glob import glob
from shapely.geometry import Point
from shapely import contains_xy
from spectral.io import envi
import rasterio

fp = '/store/carroll/col/data/2025/raw/L1/radianceH5/2025062115/NEON_D13_ALMO_DP1_L001-1_20250621_radiance.h5'
domain = os.path.basename(fp).split('_')[2]
with h5py.File(fp, "r") as f:
    time = f[f'/{domain}/Radiance'].attrs['Acquisition_Time']
    
acquistion_date = time.split(',')[0]
acquistion_start_time = time.split(',')[1].replace('[Computer Time in sec]', '').strip()
fid = f'NIS01_{acquistion_date.replace("-", "")}_{acquistion_start_time}'
print(fid)