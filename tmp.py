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

fp = '/store/carroll/sbgplants/out/2018/plots.geojson'
plots = gpd.read_file(fp)
plots = plots[['plot_name', 'campaign_name', 'granule_id', 'geometry']]
plots['sensor_name'] = 'NEON AIS 1'
plots = plots.to_crs(epsg=32613)

fids = plots['granule_id'].unique().tolist()

fid = 'NIS01_20180613_162848'
print(fid)
fid_plots = plots[plots.granule_id==fid]
poly = fid_plots.geometry.union_all()

date = fid.split('_')[1]
time = fid.split('_')[2]
fp = glob(f'/store/carroll/col/data/2018/raw/L1/radianceH5/*/NEON_D13_CRBU_DP1_{date}_{time}_radiance.h5')[0]

# get rows and cols of px within plot polys
with h5py.File(fp, "r") as f:
    igm = f['/CRBU/Radiance/Metadata/Ancillary_Rasters/IGM_Data'][:]
x = igm[:, :, 0]
y = igm[:, :, 1]
print(np.min(x), np.max(x), np.min(y), np.max(y))
inside = contains_xy(poly, x, y)
rows, cols = np.where(inside)
print(len(fid_plots), 'plots', len(rows), 'px inside polys')

# igm
lon = x[rows, cols]
lat = y[rows, cols]
elev = igm[rows, cols, -1]
del igm

# obs
with h5py.File(fp, "r") as f:
    obs = f['/CRBU/Radiance/Metadata/Ancillary_Rasters/OBS_Data'][:]
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
glt = envi.open(glob(f'/store/carroll/col/data/2018/raw/L1/radianceENVI/*/{fid}_rdn_ort_glt.hdr')[0]).open_memmap()
glt_col = glt[rows, cols, 0]
glt_row = glt[rows, cols, 1]

# shade
shade = rasterio.open(f'/store/carroll/col/data/2018/shade/{fid}_shade.tif')
shade_mask = shade.read(1)[rows, cols]

# build df
df = pd.DataFrame({
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

# join back to plot attributes
df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['x'], df['y']), crs='EPSG:32613')
df = gpd.sjoin(
    df,
    fid_plots,
    how="inner",
    predicate="within"
).drop(columns=["x", "y", "index_right","geometry"])
df = df[['plot_name', 'campaign_name', 'sensor_name', 'granule_id', 'glt_row', 'glt_column', 'lon', 'lat', 'elevation', 'shade_mask', 'path_length', 'to_sensor_azimuth', 'to_sensor_zenith', 'to_sun_azimuth', 'to_sun_zenith', 'solar_phase', 'slope', 'aspect', 'cosine_i', 'utc_time']]

# add radiance
rdns = []
with h5py.File(fp, "r") as f:
    rdn = f['/CRBU/Radiance/Radiance_Data']
    for i in range(len(rows)):
        rdn_ = rdn[rows[i], cols[i], :].reshape(1, -1)
        rdn_ = pd.DataFrame(rdn_, columns=[str(x) for x in range(rdn_.shape[-1])])
        rdns.append(rdn_)
rdn = pd.concat(rdns, axis=0, ignore_index=True)
df = pd.concat([df.reset_index(drop=True), rdn], axis=1)
