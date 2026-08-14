import pandas as pd

v1 = pd.read_csv(r"C:\Users\carroll\Downloads\spectra_2018_v1.csv")
v2 = pd.read_csv(r"C:\Users\carroll\Downloads\spectra_2018_v2.csv")

print(v1.shape)
print(v2.shape)

v1 = v1[['plot_name', 'campaign_name', 'sensor_name', 'granule_id', 'utc_time', 'shade_mask']]

# if we inner join, can we keep all v2 rows?

join_cols = ['plot_name', 'campaign_name', 'sensor_name', 'granule_id', 'utc_time']

df = pd.merge(v1, v2, on=join_cols, how='inner')
print(df.shape)

join_cols = ['plot_name', 'campaign_name', 'sensor_name',
             'granule_id', 'utc_time']

print(v1.duplicated(join_cols).sum())
print(v2.duplicated(join_cols).sum())