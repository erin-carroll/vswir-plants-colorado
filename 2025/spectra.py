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
from tqdm import tqdm
import argparse
import sys

# set up parser so flight id submitted from batch script
parser = argparse.ArgumentParser()
parser.add_argument("--fid", required=True)
args = parser.parse_args()
fid = args.fid
print(fid)

date = fid.split('_')[1]
domain = fid.split('_')[3]
line = fid.split('_')[-1]

fp = '/store/carroll/col/data/extractions/crown_delineation_all.geojson'
plots = gpd.read_file(fp)
plots = plots.rename(columns={'site_number': 'plot_name'})
plots['campaign_name'] = 'Colorado Headwaters Ecological Spectroscopy Study'
plots['sensor_name'] = 'NEON AIS 1'
plots = plots[['plot_name', 'campaign_name', 'sensor_name', 'geometry']]
plots = plots.to_crs(epsg=32613)
poly = plots.geometry.union_all()

fp = glob(f'/store/carroll/col/data/2025/raw/L1/radianceH5/*/NEON_D13_{domain}*{line}*{date}_radiance.h5')[0]

domain = os.path.basename(fp).split('_')[2]
with h5py.File(fp, "r") as f:
    time = f[f'/{domain}/Radiance'].attrs['Acquisition_Time']
acquisition_date = time.split(',')[0]
acquisition_start_time = time.split(',')[1].replace('[Computer Time in sec]', '').strip()
fid = f'NIS01_{acquisition_date.replace("-", "")}_{acquisition_start_time}'

# get rows and cols of px within plot polys
with h5py.File(fp, "r") as f:
    igm = f[f'/{domain}/Radiance/Metadata/Ancillary_Rasters/IGM_Data'][:]
x = igm[:, :, 0]
y = igm[:, :, 1]
inside = contains_xy(poly, x, y)
rows, cols = np.where(inside)
print(fid, 'px inside polys', len(rows), flush=True)

if len(rows) == 0:
    print('     skipping')
    sys.exit()

# igm
print('     igm')
lon = x[rows, cols]
lat = y[rows, cols]
elev = igm[rows, cols, -1]
del igm

# obs
print('     obs')
with h5py.File(fp, "r") as f:
    obs = f[f'/{domain}/Radiance/Metadata/Ancillary_Rasters/OBS_Data'][:]
obs = obs[rows, cols, :]
path_length = obs[:, 0]
to_sensor_azimuth = obs[:, 1]
to_sensor_zenith = obs[:, 2]
to_sun_azimuth = obs[:, 3]
to_sun_zenith = obs[:, 4]
solar_phase = obs[:, 5]
slope = obs[:, 6]
aspect = obs[:, 7]
cosine_i = obs[:, 8]
utc_time = obs[:, 9]
del obs

# glt
print('     glt')
with h5py.File(fp, "r") as f:
    glt = f[f'/{domain}/Radiance/Metadata/Ancillary_Rasters/GLT_Data'][:]
glt_col = glt[rows, cols, 0]
glt_row = glt[rows, cols, 1]

# shade
print('     shade')
with rasterio.open(f'/store/carroll/col/data/2025/shade/{fid}_shade.tif') as shade:
    shade_mask = shade.read(1)[rows, cols]

# radiance
print('     rdn')
rdns = []
with h5py.File(fp, "r") as f:
    rdn_int = f[f'/{domain}/Radiance/RadianceIntegerPart']
    rdn_dec = f[f'/{domain}/Radiance/RadianceDecimalPart']
    scale_factor = rdn_dec.attrs['Scale_Factor']
    for i in range(len(rows)):
        rdn_int_ = rdn_int[rows[i], cols[i], :].reshape(1, -1)
        rdn_dec_ = rdn_dec[rows[i], cols[i], :].reshape(1, -1)/scale_factor
        rdn_ = rdn_int_ + rdn_dec_
        rdn_ = pd.DataFrame(rdn_, columns=[str(x) for x in range(rdn_.shape[-1])])
        rdns.append(rdn_)
rdn = pd.concat(rdns, axis=0, ignore_index=True)

# build df
df = pd.DataFrame({
    'granule_id': fid,
    'x': x[rows, cols],
    'y': y[rows, cols],
    'glt_row': glt_row,
    'glt_column': glt_col,
    'lon': lon,
    'lat': lat,
    'elevation': elev,
    'shade_mask': shade_mask,
    'path_length': path_length,
    'to_sensor_azimuth': to_sensor_azimuth,
    'to_sensor_zenith': to_sensor_zenith,
    'to_sun_azimuth': to_sun_azimuth,
    'to_sun_zenith': to_sun_zenith,
    'solar_phase': solar_phase,
    'slope': slope,
    'aspect': aspect,
    'cosine_i': cosine_i,
    'utc_time': utc_time,
})
df = pd.concat([df.reset_index(drop=True), rdn], axis=1)

# join back to plot attributes
df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['x'], df['y']), crs='EPSG:32613')
df = gpd.sjoin(
    df,
    plots,
    how="inner",
    predicate="within"
)
meta_cols = ['plot_name', 'campaign_name', 'sensor_name', 'granule_id', 'glt_row', 'glt_column', 'lon', 'lat', 'elevation', 'shade_mask', 'path_length', 'to_sensor_azimuth', 'to_sensor_zenith', 'to_sun_azimuth', 'to_sun_zenith', 'solar_phase', 'slope', 'aspect', 'cosine_i', 'utc_time']
band_cols = [str(i) for i in range(426)]
df = df[meta_cols+band_cols]

df = df[df['shade_mask']!=-9999] # drop na px
df.to_csv(f'/store/carroll/sbgplants/data/extractions/spectra_{domain}_{fid}.csv', index=False)
print('exported', df.shape)