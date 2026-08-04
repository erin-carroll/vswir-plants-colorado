import os
import pandas as pd
from glob import glob
from pyproj import Transformer

import numpy as np
import matplotlib.pyplot as plt

fps = glob(f'/store/carroll/sbgplants/data/extractions/spectra*2025*.csv')

print(len(fps))
dfs = [pd.read_csv(fp) for fp in fps]
df = pd.concat(dfs, ignore_index=True)
print('including nodata px', df.shape)
df = df[df['shade_mask']!=-9999]
print('excluding nodata px', df.shape)

# switch shade convention (0=shade, 1=sunlit -> 1=shade, 0=sunlit)
df['shade_mask'] = 1-df['shade_mask']

# remove negatives/duplicates from glt row/col
df['glt_row'] = df['glt_row'].abs()
df['glt_column'] = df['glt_column'].abs()
df = df.drop_duplicates()
print('drop duplicates', df.shape)

# convert lat/lon to epsg 4326
transformer = Transformer.from_crs("EPSG:32613", "EPSG:4326", always_xy=True)
lon, lat = transformer.transform(df['lon'].values, df['lat'].values)
df['lon'] = lon
df['lat'] = lat

print(df.shape)

# filter shade duplicates
id_cols = ['campaign_name', 'plot_name', 'granule_id', 'glt_row', 'glt_column']
df = (
    df.assign(_preferred=df['shade_mask'].eq(0))
      .sort_values('_preferred', ascending=False)
      .drop_duplicates(subset=id_cols, keep='first')
      .drop(columns='_preferred')
)
print(df.shape)
print(df['shade_mask'].value_counts())

fp_out = f'/store/carroll/sbgplants/out/2025/spectra.csv'
df.to_csv(fp_out, index=False)