import os
import pandas as pd
from glob import glob

year = 2025
fps = glob(f'/store/carroll/sbgplants/data/extractions/spectra*{year}*.csv')

print(len(fps))
if len(fps)>0:
    dfs = [pd.read_csv(fp) for fp in fps]
    df = pd.concat(dfs, ignore_index=True)
    print('including nodata px', df.shape)
    df = df[df['shade_mask']!=-9999]
    print('excluding nodata px', df.shape)
    fp_out = f'/store/carroll/sbgplants/out/{year}/spectra.csv'
    df.to_csv(fp_out, index=False)