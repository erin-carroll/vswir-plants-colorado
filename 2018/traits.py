import os
import pandas as pd
import numpy as np

os.chdir('C:\\Users\\carroll\\Documents\\sbgplant')

df = pd.read_csv('data\\col_2018\\raw\\10.15485.1618130\\data\\sample_site.csv')
df = df.rename(columns={'SampleSiteCode': 'plot_name', 'VegetationType': 'plot_veg_type'})
df['campaign_name'] = 'East River 2018'
df['collection_date'] = (df['Year'].astype(str) + '-' + df['Month'].astype(str) + '-' + df['Day'].astype(str))

subplot_cover_method = {
    'Meadow': 'Quadrat',
    'Tree': 'Visual assessment',
    'Shrub': 'Visual assessment'
}
df['subplot_cover_method'] = df['plot_veg_type'].map(subplot_cover_method)

floristic_survey = {
    'Meadow': 1,
    'Tree': 0,
    'Shrub': 0
}
df['floristic_survey'] = df['plot_veg_type'].map(floristic_survey)

df = df[['plot_name', 'SamplingArea', 'campaign_name', 'collection_date', 'plot_veg_type','subplot_cover_method', 'floristic_survey']]

# sample
fractional_cover = pd.read_csv('data\\col_2018\\raw\\10.15485.1618130\\data\\fractional_cover.csv')
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
species_list = pd.read_csv('data\\col_2018\\raw\\10.15485.1618130\\data\\species_list.csv')
species_list['taxa'] = species_list['Genus'] + ' ' + species_list['Species']
species_list.loc[species_list['taxa'].isna(), 'taxa'] = species_list.loc[species_list['Genus'].isna(), 'CoverCode']
species_list = species_list[['CoverCode', 'taxa', 'veg_or_cover_type']]

fractional_cover = pd.merge(fractional_cover, species_list, on='CoverCode', how='left', suffixes=('',''))

fractional_cover['sample_name'] = fractional_cover['plot_name'] + '_' + fractional_cover['CoverCode']
fractional_cover['sample_name'] = fractional_cover['sample_name'].str.replace(' ', '', regex=False)

fractional_cover['phenophase'] = 'Not recorded'

fc_class = {
    'Moss': 'pv',
    'Forb': 'pv',
    'NPV': 'npv',
    'Bare': 'soil',
    'Grass': 'pv',
    'Low Shrub': 'pv',
    'Needleleaf': 'pv',
    'Low shrub': 'pv',
    'Broadleaf': 'pv',
}
fractional_cover['sample_fc_class'] = fractional_cover['veg_or_cover_type'].map(fc_class)
fractional_cover = fractional_cover.rename(columns={'FractionalCover': 'sample_fc_percent'})

fractional_cover = fractional_cover[['plot_name', 'sample_name', 'taxa', 'veg_or_cover_type', 'phenophase', 'sample_fc_class', 'sample_fc_percent', 'CoverCode']]

df = pd.merge(df, fractional_cover, on='plot_name', how='right', suffixes=('',''))
df['plant_status'] = 'Not recorded'
df['canopy position'] = 'Not recorded'

# traits - lma site
lma_site = pd.read_csv('data\\col_2018\\raw\\10.15485.1618132\\data\\lma_site_samples.csv')
lma_site.loc[lma_site.Species=='engelmann', 'Species'] = 'Engelmann'
lma_site = lma_site[['SampleSiteCode', 'Species', 'Wet_Weight_g', 'Dry_Weight_g', 'LMA_gm2', 'LWC_%']]
lma_site = lma_site.rename(columns={
    'SampleSiteCode': 'plot_name',
    'Species': 'CoverCode',
    'Wet_Weight_g': 'Wet weight',
    'Dry_Weight_g': 'Dry weight',
    'LMA_gm2': 'LMA',
    'LWC_%': 'LWC'})
lma_site = lma_site.melt(id_vars=['plot_name', 'CoverCode'], var_name='trait', value_name='value').reset_index()
method = {
    'Wet weight': 'Weight based',
    'Dry weight': 'Weight based',
    'LMA': 'Weight based',
    'LWC': 'Weight based'
}
lma_site['method'] = lma_site['trait'].map(method)
handling = {
    'Wet weight': 'Fresh',
    'Dry weight': 'Oven dried',
    'LMA': 'Oven dried', # ?
    'LWC': 'Oven dried' # ?
}
lma_site['handling'] = lma_site['trait'].map(handling)
units = {
    'Wet weight': 'g',
    'Dry weight': 'g',
    'LMA': 'grams dry mass per g m2',
    'LWC': 'percentage'
}
lma_site['units'] = lma_site['trait'].map(units)
lma_site['error'] = None
lma_site['error_type'] = None

df_lma_site = pd.merge(df, lma_site, left_on=['plot_name', 'CoverCode'], right_on=['plot_name', 'CoverCode'], how='right', suffixes=('',''))
df_lma_site.to_csv('out/2018/traits_lma_site.csv', index=False)

# traits - foliar chemistry
chem = pd.read_csv('data\\col_2018\\raw\\10.15485.1631278\\data\\CN_Results_Foliar.csv')
chem = chem.rename(columns={
    'SampleSiteCode':'plot_name',
    'N_weight_percent': 'Nitrogen',
    'C_weight_percent': 'Carbon'
    })
chem = chem[['plot_name', 'd13C', 'Nitrogen', 'Carbon']]
chem = chem.melt(id_vars=['plot_name'], var_name='trait', value_name='value').reset_index()
method = {
    'd13C': 'Chemical analysis',
    'Nitrogen': 'Chemical analysis',
    'Carbon': 'Chemical analysis',
}
chem['method'] = chem['trait'].map(method)
handling = {
    'd13C': 'Oven dried',
    'Nitrogen': 'Oven dried',
    'Carbon': 'Oven dried',
}
chem['handling'] = chem['trait'].map(handling)
units = {
    'd13C': 'permil',
    'Nitrogen': 'concentration in percent dry mass',
    'Carbon': 'concentration in percent dry mass',
}
chem['units'] = chem['trait'].map(units)
chem['error'] = None
chem['error_type'] = None

df_chem = pd.merge(df, chem, on='plot_name', how='right', suffixes=('',''))
df_chem.to_csv('out/2018/traits_chem.csv', index=False)

# lma - meadow
lma_meadow = pd.read_csv('data\\col_2018\\raw\\10.15485.1618132\\data\\lma_meadow_area_samples.csv')
lma_meadow = lma_meadow[['SampleArea', 'SpeciesCode', 'Wet Weight (g)', 'Dry Weight (g)', 'LMA (g/m2)', 'LWC (%)']]
lma_meadow = lma_meadow.rename(columns={
    'SampleArea': 'SamplingArea',
    'SpeciesCode': 'CoverCode',
    'Wet Weight (g)': 'Wet weight',
    'Dry Weight (g)': 'Dry weight',
    'LMA (g/m2)': 'LMA',
    'LWC (%)': 'LWC'})
lma_meadow = lma_meadow.melt(id_vars=['SamplingArea', 'CoverCode'], var_name='trait', value_name='value').reset_index()
method = {
    'Wet weight': 'Weight based',
    'Dry weight': 'Weight based',
    'LMA': 'Weight based',
    'LWC': 'Weight based'
}
lma_meadow['method'] = lma_meadow['trait'].map(method)
handling = {
    'Wet weight': 'Fresh',
    'Dry weight': 'Oven dried',
    'LMA': 'Oven dried', # ?
    'LWC': 'Oven dried' # ?
}
lma_meadow['handling'] = lma_meadow['trait'].map(handling)
units = {
    'Wet weight': 'g',
    'Dry weight': 'g',
    'LMA': 'grams dry mass per g m2',
    'LWC': 'percentage'
}
lma_meadow['units'] = lma_meadow['trait'].map(units)
lma_meadow['error'] = None
lma_meadow['error_type'] = None

df_lma_meadow = pd.merge(df, lma_meadow, on=['SamplingArea', 'CoverCode'], how='outer', suffixes=('',''))
df_lma_meadow.to_csv('out/2018/traits_lma_meadow.csv', index=False)

df = pd.concat([df_lma_site, df_lma_meadow, df_chem], ignore_index=True)
df = df[df['trait'].notna()]
df = df[['plot_name', 'campaign_name', 'collection_date', 'plot_veg_type',
         'subplot_cover_method', 'floristic_survey',
         'sample_name', 'taxa', 'veg_or_cover_type', 'phenophase', 
         'sample_fc_class', 'sample_fc_percent', 'plant_status', 'canopy position',
         'trait', 'value', 'method', 'handling', 'units', 'error', 'error_type']]
print(df.shape)
print(df.columns)

df.to_csv('out/2018/traits.csv', index=False)

