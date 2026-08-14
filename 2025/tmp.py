import pandas as pd

df = pd.read_csv(r"C:\Users\carroll\Downloads\spectra.csv")
print(df.shape)

# df = df.drop_duplicates()
# print(df.shape)

df = df[df.duplicated(subset=['campaign_name', 'plot_name', 'granule_id', 'glt_row', 'glt_column', 'shade_mask'], keep=False)]
print(df.shape)

df.to_csv(r"C:\Users\carroll\Downloads\spectra_duplicates_2025.csv", index=False)