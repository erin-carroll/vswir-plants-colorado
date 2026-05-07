import os
import pandas as pd
import geopandas as gpd


fp = '/store/carroll/col/data/extractions/CRBU2018_AOP_Crowns.geojson'
gdf = gpd.read_file(fp)
gdf = gdf.rename(columns={'SiteCode': 'plot_name'})

gdf['campaign_name'] = 'East River 2018'
gdf['site_id'] = 'CRBU'
gdf['extraction_method'] = 'Internal centroids'
gdf['delineation_method'] = 'Posthoc'
gdf['shape_aligned_to_granule'] = 'False'

# plot type
fp = '/store/carroll/sbgplants/data/raw/10.15485.1618130/sample_site.csv'
sample_site = pd.read_csv(fp)
plot_type = {
    'Meadow': 'Plot',
    'Tree': 'Individual',
    'Shrub': 'Individual'
}
sample_site['plot_method'] = sample_site['VegetationType'].map(plot_type)
sample_site = sample_site.rename(columns={'SampleSiteCode': 'plot_name'}) 
sample_site = sample_site[['plot_name', 'plot_method']]
gdf = gdf.merge(sample_site, on='plot_name', how='left')

# granule id
fp = '/store/carroll/sbgplants/out/2018/spectra.csv'
df = pd.read_csv(fp)
df= df[['plot_name', 'granule_id']].drop_duplicates()
print(df.shape)

gdf = gdf.merge(df, on='plot_name', how='inner')

gdf = gdf[['plot_name', 'campaign_name', 'site_id', 'plot_method', 'granule_id', 'extraction_method', 'delineation_method', 'shape_aligned_to_granule', 'geometry']]

# multipoly to poly
gdf = gdf.explode(index_parts=False).reset_index(drop=True)

# project to 4326
gdf = gdf.to_crs(4326)

print(gdf.shape)

gdf.to_file('/store/carroll/sbgplants/out/2018/plots.geojson', driver='GeoJSON')
