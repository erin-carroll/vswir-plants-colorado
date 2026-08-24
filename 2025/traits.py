import os
import pandas as pd
import geopandas as gpd
import numpy as np
from glob import glob 

os.chdir('C:/Users/erinc/Documents/sbgplant')

fps = glob('data/2025/loc/*site_cleaned.csv')

# load plot metadata
dfs = []
for fp in fps:
    df = pd.read_csv(fp)
    if 'meadow' in fp:
        df = df[['Location_Type', 'Site_Number', 'Collection_Date']]
        df['Vegetation_Species'] = 'not recorded'
    else:
        df = df[['Location_Type', 'Site_Number', 'Collection_Date', 'Vegetation_Species']]
        df['Vegetation_Species'] = [x.split('-')[-1] for x in df['Vegetation_Species']]
    dfs.append(df)
df = pd.concat(dfs, ignore_index=True)

# fix NA
mask = df['Site_Number'].eq(1146)
df.loc[mask, 'Location_Type'] = 'meadow'
df.loc[mask, 'Collection_Date'] = '6/28/2025'

df = df[df['Location_Type'].notna()]

df = df.rename(columns={
    'Site_Number': 'plot_name',
    'Location_Type': 'plot_veg_type',
    'Collection_Date': 'collection_date',
    'Vegetation_Species': 'taxa'
    })
df['campaign_name'] = 'Colorado Headwaters Ecological Spectroscopy Study'

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

df['sample_name'] = [str(x)+'_lai' for x in df['plot_name']]

df = df[['plot_name', 'campaign_name', 'collection_date', 'plot_veg_type','subplot_cover_method', 'floristic_survey', 'sample_name', 'taxa']]

# tmp = df[['taxa', 'plot_veg_type']].drop_duplicates()
# tmp.to_csv('data/2025/veg_or_cover_type.csv', index=False)
tmp = pd.read_csv('data/2025/veg_or_cover_type.csv')[['taxa', 'veg_or_cover_type']]
df = pd.merge(df, tmp, how='left', on='taxa')

frac = pd.read_csv('data/2025/loc/chess_meadow_cover_cleaned.csv')
frac['Cover_Type'] = [x.split(' ')[0] for x in frac['Cover_Type']]
frac['Cover_Class_Name'][frac['Cover_Type']=='Live'] = 'pv'
frac['Cover_Class_Name'][frac['Cover_Class_Name']=='Nonvegetated Dirt'] = 'soil'
frac['Cover_Class_Name'][frac['Cover_Class_Name']=='Nonvegetated Dirt '] = 'soil'
frac['Cover_Class_Name'][frac['Cover_Class_Name']=='Nonvegetated Rock'] = 'soil'
frac['Cover_Class_Name'][frac['Cover_Class_Name']=='Non-Photosynthetic Vegetation'] = 'npv'
frac = (frac.groupby(['Site_Number', 'Cover_Class_Name'], as_index=False)['Cover_Percent'].sum())
frac = frac.rename(columns={
    'Site_Number': 'plot_name',
    'Cover_Class_Name': 'sample_fc_class',
    'Cover_Percent': 'sample_fc_percent'
    })

df = pd.merge(df, frac, how='outer', on='plot_name')

# fractional cover, tree & shrub
df['sample_fc_class'] = df['sample_fc_class'].str.strip()
df.loc[df['plot_veg_type'].isin(['tree', 'shrub']), 'sample_fc_class'] = 'pv'
df.loc[df['plot_veg_type'].isin(['tree', 'shrub']), 'sample_fc_percent'] = 100

# fractional cover, meadow
df.loc[df['sample_fc_class']=='Non-Photosynthetic Vegetation', 'sample_fc_class'] = 'npv'
df.loc[df['sample_fc_class']=='Nonvegetated Dirt', 'sample_fc_class'] = 'soil'
df.loc[df['sample_fc_class']=='Nonvegetated Rock', 'sample_fc_class'] = 'rock' # is this soil, or should we add another enum for rock?
df.loc[df['sample_fc_class']=='Other Moss/Lichen', 'sample_fc_class'] = 'npv' # moss is pv, lichen is npv? But for veg_or_cover_type logic, we don't want them to be pv?
df.loc[~df['sample_fc_class'].isin(['npv', 'soil', 'rock']), 'sample_fc_class'] = 'pv'

df.loc[df['sample_fc_class']=='npv', 'veg_or_cover_type'] = 'npv'
df.loc[df['sample_fc_class']=='soil', 'veg_or_cover_type'] = 'bare'
df.loc[df['sample_fc_class']=='rock', 'veg_or_cover_type'] = 'bare'

# dissolve pv columns
df = df.groupby(['plot_name', 'campaign_name', 'collection_date', 'plot_veg_type', 'subplot_cover_method', 'floristic_survey', 'sample_name', 'taxa', 'veg_or_cover_type', 'sample_fc_class']).agg({
          'sample_fc_percent': 'sum',
      }).reset_index()

df['phenophase'] = 'not recorded'
df['plant_status'] = 'not recorded'
df['canopy_position'] = 'not recorded'

df['trait'] = 'lai'
df['method'] = 'field measured'
df['handling'] = 'fresh'
df['units'] = 'ratio'
df['error_type'] = 'standard error of measurement'

# join value, error
fps = glob('data/2025/lai/*cleaned.csv')
dfs = []
for fp in fps:
    vals = pd.read_csv(fp)
    vals = vals[['Site_Number', 'L_2200', 'SEL_2200']]
    if 'meadow' in fp:
        vals = (
            vals.groupby('Site_Number', as_index=False)
            .agg(
                L_2200=('L_2200', 'mean'),
                SD_2200=('L_2200', 'std'),
                n=('L_2200', 'count')
            )
        )
        vals['SEL_2200'] = vals['SD_2200'] / np.sqrt(vals['n'])
        vals = vals[['Site_Number', 'L_2200', 'SEL_2200']]
    if 'tree' in fp:
        vals['Site_Number'] = [int(x.removesuffix('_LAI')) for x in vals['Site_Number']]
    dfs.append(vals)
vals = pd.concat(dfs, axis=0)
vals = vals.rename(columns={
    'Site_Number': 'plot_name',
    'L_2200': 'value',
    'SEL_2200': 'error'
})
vals['sample_fc_class'] = 'pv'
df = pd.merge(df, vals, how='left', on=['plot_name', 'sample_fc_class'])

# export
df = df[['plot_name', 'campaign_name', 'collection_date', 'plot_veg_type',
         'subplot_cover_method', 'floristic_survey',
         'sample_name', 'taxa', 'veg_or_cover_type', 'phenophase', 
         'sample_fc_class', 'sample_fc_percent', 'plant_status', 'canopy_position',
         'trait', 'value', 'method', 'handling', 'units', 'error', 'error_type']]
print(df.shape)

# blank columns with no trait measurement
mask = df['value'].isna()
blank_cols = ['sample_name', 'trait', 'value', 'method','handling', 'units', 'error', 'error_type']
df.loc[mask, blank_cols] = pd.NA
df.loc[df['sample_fc_class']!='pv', 'taxa'] = pd.NA

# any duplicates?
tmp = df[df.duplicated(subset=['plot_name', 'campaign_name', 'collection_date', 'sample_fc_class'], keep=False)]
print(tmp.shape)
# print(tmp)
# just one duplicated, error from site_cleaned. Remove
# df = df.drop_duplicates()
# print(df.shape)

df.to_csv('out/2025/traits.csv', index=False)