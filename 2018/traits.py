import os
import pandas as pd
import geopandas as gpd
import numpy as np

os.chdir('C:\\Users\\erinc\\Documents\\sbgplant')

df = pd.read_csv('data\\2018\\raw\\10.15485.1618130\\data\\sample_site.csv')
df = df.rename(columns={'SampleSiteCode': 'plot_name', 'VegetationType': 'plot_veg_type'})
df['campaign_name'] = 'East River 2018'
df['collection_date'] = (df['Year'].astype(str) + '-' + df['Month'].astype(str) + '-' + df['Day'].astype(str))

df['plot_veg_type'] = df['plot_veg_type'].str.lower()
subplot_cover_method = {
    'meadow': 'quadrat',
    'tree': 'visual assessment',
    'shrub': 'visual assessment'
}
df['subplot_cover_method'] = df['plot_veg_type'].map(subplot_cover_method)

floristic_survey = {
    'meadow': 1,
    'tree': 0,
    'shrub': 0
}
df['floristic_survey'] = df['plot_veg_type'].map(floristic_survey)

df = df[['plot_name', 'campaign_name', 'collection_date', 'plot_veg_type','subplot_cover_method', 'floristic_survey']]

# sample
fractional_cover = pd.read_csv('data\\2018\\raw\\10.15485.1618130\\data\\fractional_cover.csv')
fractional_cover = fractional_cover.rename(columns={'SampleSiteCode': 'plot_name'})
# fix some errors
fractional_cover.loc[fractional_cover.CoverCode=='engelmann', 'CoverCode'] = 'Engelmann'
fractional_cover.loc[fractional_cover.CoverCode=='RibMon', 'CoverCode'] = 'Gooseberry' # confirm this with Dana?
fractional_cover.loc[fractional_cover.CoverCode=='RubIda', 'CoverCode'] = 'Raspberry' # confirm this with Dana?
# merge duplicate rows
keys = ['CoverCode', 'plot_name']
agg_ = {'SamplingArea': 'first', 'CollectionDate': 'first', 'FractionalCover': 'sum', 'Note': 'first'}
fractional_cover = (fractional_cover.groupby(keys, dropna=False, sort=False).agg(agg_).reset_index())

# get taxa from spp list
species_list = pd.read_csv('data\\2018\\raw\\10.15485.1618130\\data\\species_list.csv')
species_list['taxa'] = species_list['Genus'] + ' ' + species_list['Species']
species_list.loc[species_list['taxa'].isna(), 'taxa'] = species_list.loc[species_list['Genus'].isna(), 'CoverCode']
species_list = species_list[['CoverCode', 'taxa']]
fractional_cover = pd.merge(fractional_cover, species_list, on='CoverCode', how='left', suffixes=('',''))

# merge back to df
fractional_cover = fractional_cover[['plot_name', 'taxa', 'FractionalCover']]
df = pd.merge(df, fractional_cover, on=['plot_name'], how='outer', suffixes=('',''))

df['sample_name'] = df['plot_name'] + '-' + 'FO'
df['sample_name'] = df['sample_name'].str.replace(' ', '', regex=False)

# tmp = df[['taxa', 'plot_veg_type']].drop_duplicates()
# tmp.to_csv('data/2018/veg_or_cover_type.csv', index=False)
tmp = pd.read_csv('data/2018/veg_or_cover_type.csv')
df = pd.merge(df, tmp, how='left', on=['taxa', 'plot_veg_type'])

# summarize meadow plots over pv
df = df.groupby(['plot_name', 'campaign_name', 'collection_date', 'plot_veg_type','subplot_cover_method', 'floristic_survey', 'sample_name', 'veg_or_cover_type']).agg({
          'taxa': 'first',
          'FractionalCover': 'sum'}).reset_index()

df.loc[df['veg_or_cover_type'].isin(['bare', 'moss', 'npv']), 'sample_name'] = pd.NA
df.loc[df['veg_or_cover_type'].isin(['bare', 'moss', 'npv']), 'taxa'] = pd.NA
df.loc[df['veg_or_cover_type']=='herbaceous aggregate sample', 'taxa'] = 'not recorded'

df = df.rename(columns={'FractionalCover': 'sample_fc_percent'})

fc_class = {
    'moss': 'pv',
    'npv': 'npv',
    'bare': 'soil',
    'low shrub': 'pv',
    'needleleaf': 'pv',
    'broadleaf': 'pv',
    'herbaceous aggregate sample': 'pv'
}
df['sample_fc_class'] = df['veg_or_cover_type'].map(fc_class)

df['phenophase'] = 'not recorded'
df['plant_status'] = 'not recorded'
df['canopy_position'] = 'not recorded'

df = df[['plot_name', 'campaign_name', 'collection_date', 'plot_veg_type','subplot_cover_method', 'floristic_survey', 'sample_name', 'taxa', 'veg_or_cover_type', 'phenophase', 'sample_fc_class', 'sample_fc_percent', 'plant_status', 'canopy_position']]

# traits - lma (tree, shrub only. Meadow lma data was not collected per-plot, but rather as a composite sample across the sampling areas)
lma_site = pd.read_csv('data\\2018\\raw\\10.15485.1618132\\data\\lma_site_samples.csv')
lma_site = lma_site.rename(columns={
    'SampleSiteCode': 'plot_name',
    'Wet_Weight_g': 'wet weight',
    'Dry_Weight_g': 'dry weight',
    'LMA_gm2': 'lma',
    'LWC_%': 'lwc'})
lma_site = lma_site[['plot_name', 'wet weight', 'dry weight', 'lma', 'lwc']]
lma_site = lma_site.melt(id_vars=['plot_name'], var_name='trait', value_name='value')
method = {
    'wet weight': 'weight based',
    'dry weight': 'weight based',
    'lma': 'weight based',
    'lwc': 'weight based'
}
lma_site['method'] = lma_site['trait'].map(method)
handling = {
    'wet weight': 'fresh',
    'dry weight': 'oven dried',
    'lma': 'oven dried',
    'lwc': 'oven dried'
}
lma_site['handling'] = lma_site['trait'].map(handling)
units = {
    'wet weight': 'g',
    'dry weight': 'g',
    'lma': 'grams dry mass per g m2',
    'lwc': 'percentage'
}
lma_site['units'] = lma_site['trait'].map(units)
lma_site['error'] = None
lma_site['error_type'] = None

lma_site['sample_fc_class'] = 'pv'

df_lma_site = pd.merge(df, lma_site, on=['plot_name', 'sample_fc_class'], how='outer', suffixes=('',''))

# traits - foliar chemistry
chem = pd.read_csv('data\\2018\\raw\\10.15485.1631278\\data\\CN_Results_Foliar.csv')
chem = chem.rename(columns={
    'SampleSiteCode':'plot_name',
    'N_weight_percent': 'nitrogen',
    'C_weight_percent': 'carbon',
    })
chem = chem[['plot_name', 'd13C', 'nitrogen', 'carbon']]
chem = chem.melt(id_vars=['plot_name'], var_name='trait', value_name='value')
method = {
    'd13C': 'chemical analysis',
    'nitrogen': 'chemical analysis',
    'carbon': 'chemical analysis',
}
chem['method'] = chem['trait'].map(method)
handling = {
    'd13C': 'oven dried',
    'nitrogen': 'oven dried',
    'carbon': 'oven dried',
}
chem['handling'] = chem['trait'].map(handling)
units = {
    'd13C': 'permil',
    'nitrogen': 'concentration in percent dry mass',
    'carbon': 'concentration in percent dry mass',
}
chem['units'] = chem['trait'].map(units)
chem['error'] = None
chem['error_type'] = None

chem['sample_fc_class'] = 'pv'

df_chem = pd.merge(df, chem, on=['plot_name', 'sample_fc_class'], how='outer', suffixes=('',''))

df = pd.concat([df_lma_site, df_chem], ignore_index=True)
df = df[['plot_name', 'campaign_name', 'collection_date', 'plot_veg_type',
         'subplot_cover_method', 'floristic_survey',
         'sample_name', 'taxa', 'veg_or_cover_type', 'phenophase', 
         'sample_fc_class', 'sample_fc_percent', 'plant_status', 'canopy_position',
         'trait', 'value', 'method', 'handling', 'units', 'error', 'error_type']]
print(df.shape)

# qaqc
# two sites dropped where there were no fractional cover estimates
df = df[~df['sample_fc_percent'].isna()]
# df = df[~df['value'].isna()]

# populate missing sample names
df['sample_name'] = df['sample_name'].fillna(df['plot_name'].astype(str) + '_fc_' + df['sample_fc_class'])

df.to_csv('out/2018/traits.csv', index=False)