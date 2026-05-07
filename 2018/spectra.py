import os
import pandas as pd
import geopandas as gpd
import numpy as np
import h5py
from glob import glob
from shapely import contains_xy
from spectral.io import envi
import rasterio
from pyproj import Transformer

# fp = '/store/carroll/col/data/extractions/CRBU2018_AOP_Crowns.geojson'
# plots = gpd.read_file(fp)
# plots = plots.rename(columns={'SiteCode': 'plot_name'})
# plots['campaign_name'] = 'East River 2018'
# plots['sensor_name'] = 'NEON AIS 1'
# plots = plots[['plot_name', 'campaign_name', 'sensor_name', 'geometry']]
# plots = plots.to_crs(epsg=32613)
# poly = plots.geometry.union_all()

# dfs = []
# fps = glob(f'/store/carroll/col/data/2018/raw/L1/radianceH5/*/NEON_D13_CRBU_DP1_*_radiance.h5')

# for fp in fps:
#     date = os.path.basename(fp).split('_')[4]
#     time = os.path.basename(fp).split('_')[5]
#     fid = f'NIS01_{date}_{time}'
#     print(fid)

#     # get rows and cols of px within plot polys
#     with h5py.File(fp, "r") as f:
#         igm = f['/CRBU/Radiance/Metadata/Ancillary_Rasters/IGM_Data'][:]
#     x = igm[:, :, 0]
#     y = igm[:, :, 1]
#     inside = contains_xy(poly, x, y)
#     rows, cols = np.where(inside)
#     print(len(rows), 'px inside polys')

#     if len(rows) == 0:
#         continue

#     # igm
#     lon = x[rows, cols]
#     lat = y[rows, cols]
#     elev = igm[rows, cols, -1]
#     del igm

#     # obs
#     with h5py.File(fp, "r") as f:
#         obs = f['/CRBU/Radiance/Metadata/Ancillary_Rasters/OBS_Data'][:]
#     obs = obs[rows, cols, :]
#     path_length = obs[:, 0]
#     to_sensor_azimuth = obs[:, 1]
#     to_sensor_zenith = obs[:, 2]
#     to_sun_azimuth = obs[:, 3]
#     to_sun_zenith = obs[:, 4]
#     solar_phase = obs[:, 5]
#     slope = obs[:, 6]
#     aspect = obs[:, 7]
#     cosine_i = obs[:, 8]
#     utc_time = obs[:, 9]
#     del obs

#     # glt
#     glt = envi.open(glob(f'/store/carroll/col/data/2018/raw/L1/radianceENVI/*/{fid}_rdn_ort_glt.hdr')[0]).open_memmap()
#     glt_col = glt[rows, cols, 0]
#     glt_row = glt[rows, cols, 1]

#     # shade
#     with rasterio.open(f'/store/carroll/col/data/2018/shade/{fid}_shade.tif') as shade:
#         shade_mask = shade.read(1)[rows, cols]

#     # build df
#     df = pd.DataFrame({
#         'granule_id': fid,
#         'x': x[rows, cols],
#         'y': y[rows, cols],
#         'glt_row': glt_row,
#         'glt_column': glt_col,
#         'lon': lon,
#         'lat': lat,
#         'elevation': elev,
#         'shade_mask': shade_mask,
#         'path_length': path_length,
#         'to_sensor_azimuth': to_sensor_azimuth,
#         'to_sensor_zenith': to_sensor_zenith,
#         'to_sun_azimuth': to_sun_azimuth,
#         'to_sun_zenith': to_sun_zenith,
#         'solar_phase': solar_phase,
#         'slope': slope,
#         'aspect': aspect,
#         'cosine_i': cosine_i,
#         'utc_time': utc_time,
#     })

#     # add radiance
#     rdns = []
#     with h5py.File(fp, "r") as f:
#         rdn = f['/CRBU/Radiance/Radiance_Data']
#         for i in range(len(rows)):
#             rdn_ = rdn[rows[i], cols[i], :].reshape(1, -1)
#             rdn_ = pd.DataFrame(rdn_, columns=[str(x) for x in range(rdn_.shape[-1])])
#             rdns.append(rdn_)
#     rdn = pd.concat(rdns, axis=0, ignore_index=True)
#     df = pd.concat([df.reset_index(drop=True), rdn], axis=1)

#     # join back to plot attributes
#     df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['x'], df['y']), crs='EPSG:32613')
#     df = gpd.sjoin(
#         df,
#         plots,
#         how="inner",
#         predicate="within"
#     )
#     meta_cols = ['plot_name', 'campaign_name', 'sensor_name', 'granule_id', 'glt_row', 'glt_column', 'lon', 'lat', 'elevation', 'shade_mask', 'path_length', 'to_sensor_azimuth', 'to_sensor_zenith', 'to_sun_azimuth', 'to_sun_zenith', 'solar_phase', 'slope', 'aspect', 'cosine_i', 'utc_time']
#     band_cols = [str(i) for i in range(426)]
#     df = df[meta_cols+band_cols]

#     dfs.append(df)

# df = pd.concat(dfs, axis=0, ignore_index=True)
# df = df[df['shade_mask']!=-9999] # drop na px
# df.to_csv('/store/carroll/sbgplants/out/2018/spectra.csv', index=False)
# print('exported', df.shape)

# final patches
df = pd.read_csv('/store/carroll/sbgplants/out/2018/spectra.csv')
# switch shade convention (0=shade, 1=sunlit -> 1=shade, 0=sunlit)
df['shade_mask'] = 1-df['shade_mask']
# remove negatives from glt row/col
df['glt_row'] = df['glt_row'].abs()
df['glt_column'] = df['glt_column'].abs()
# convert lat/lon to epsg 4326
transformer = Transformer.from_crs("EPSG:32613", "EPSG:4326", always_xy=True)
lon, lat = transformer.transform(df['lon'].values, df['lat'].values)
df['lon'] = lon
df['lat'] = lat
df.to_csv('/store/carroll/sbgplants/out/2018/spectra_20260506.csv', index=False)