import os
import pandas as pd
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask

fp = r'C:\Users\carroll\Documents\sbgplant\data\2025\CHESS_2025_crowns.geojson'
gdf = gpd.read_file(fp)

gdf = gdf.rename(columns={
    'site_number': 'plot_name',
    'domain': 'site_id'
    })

gdf['campaign_name'] = 'Colorado Headwaters Ecological Spectroscopy Study'
gdf['extraction_method'] = 'Internal centroids'
gdf['delineation_method'] = 'Posthoc'

# plot type
plot_type = {
    'Meadow': 'Plot',
    'Tree': 'Individual',
    'Shrub': 'Individual'
}
gdf['plot_method'] = gdf['site_type'].map(plot_type)

# granule id
fp = r'C:\Users\carroll\Documents\sbgplant\out\2025\spectra.csv'
df = pd.read_csv(fp)
df= df[['plot_name', 'granule_id']].drop_duplicates()

gdf['plot_name'] = gdf['plot_name'].astype(int)
gdf = gdf.merge(df, on='plot_name', how='inner')

# shape aligned to granule
gdfs = []
for domain in ['ALMO', 'CRBU', 'UPTA']:
    with open(f'C:/Users/carroll/Documents/sbgplant/data/2025/mosaic_glt_{domain}.txt') as f:
        mosaic_ids = [x.strip() for x in f.read().splitlines()]
    gdf_ = gdf[gdf['site_id']==domain]
    shape_algned_to_granule = []
    with rasterio.open(f'C:/Users/carroll/Documents/sbgplant/data/2025/{domain}_2025_mosaic_glt.tif') as src:
        for geom, gid in zip(gdf_.geometry, gdf_.granule_id):
            out_image, _ = rasterio.mask.mask(src, [geom], crop=True, filled=False)
            vals = np.unique(out_image[2].compressed())
            ids = np.array(mosaic_ids)[vals]
            if len(ids) > 1:
                val = False
            elif gid in ids[0]:
                val = True
            else:
                val = False
            shape_algned_to_granule.append(val)
    gdf_['shape_aligned_to_granule'] = shape_algned_to_granule
    gdfs.append(gdf_)

gdf = pd.concat(gdfs, ignore_index=True)

gdf = gdf[['plot_name', 'campaign_name', 'site_id', 'plot_method', 'granule_id', 'extraction_method', 'delineation_method', 'shape_aligned_to_granule', 'geometry']]

# project to 4326
gdf = gdf.to_crs(4326)

print(gdf.shape)

# filter to plots with traits
traits = pd.read_csv(r'C:\Users\carroll\Documents\sbgplant\out\2025\traits.csv')
gdf = gdf[gdf['plot_name'].isin(traits['plot_name'])].reset_index(drop=True)
print(gdf.shape)

gdf.to_file('C:/Users/carroll/Documents/sbgplant/out/2025/plots.geojson', driver='GeoJSON')

