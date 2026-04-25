import os
import pandas as pd
import geopandas as gpd

os.chdir('C:/Users/carroll/Documents/sbgplant')

fp = r'C:\Users\carroll\Documents\sbgplant\data\CRBU2018_AOP_Crowns.geojson'
gdf = gpd.read_file(fp)
gdf = gdf.rename(columns={'SiteCode': 'plot_name'})

gdf['campaign_name'] = 'East River 2018'
gdf['site_id'] = 'CRBU' # ?

# plot type
fp = r'C:\Users\carroll\Documents\sbgplant\data\col_2018\raw\10.15485.1618130\data\sample_site.csv'
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
fp = r"C:\Users\carroll\Documents\col\data\2018\crbu_2018_fid_boundaries.geojson"
fids = gpd.read_file(fp)
fids = fids[['flightline', 'geometry']]
fids = fids.rename(columns={'flightline': 'granule_id'})
gdf = gpd.sjoin(
    gdf,
    fids,
    how="left",
    predicate="covered_by"
).drop(columns="index_right").reset_index(drop=True)

gdf['extraction_method'] = 'Internal centroids'
gdf['delineation_method'] = 'Posthoc'
gdf['shape_aligned_to_granule'] = 'False'

gdf = gdf[['plot_name', 'campaign_name', 'site_id', 'plot_method', 'granule_id', 'extraction_method', 'delineation_method', 'shape_aligned_to_granule', 'geometry']]

# multipoly to poly
gdf = gdf.explode(index_parts=False).reset_index(drop=True)

# project to 4326
gdf = gdf.to_crs(4326)

gdf.to_file('out/2018/plots.geojson', driver='GeoJSON')
