import os
import pandas as pd
import geopandas as gpd

os.chdir('C:/Users/erinc/Documents/sbgplant')

traits = pd.read_csv('out/2018/traits.csv')
spectra = pd.read_csv('out/2018/spectra.csv')
granule = pd.read_csv('out/2018/granule_metadata.csv')
plots = gpd.read_file('out/2018/plots.geojson')

print(traits.shape, spectra.shape, granule.shape, plots.shape)

# get plot_names where there are traits and plot polygons and spectra
plot_names = set(traits['plot_name']) & set(plots['plot_name']) & set(spectra['plot_name'])
print(len(plot_names))

# filter traits
print('\ntraits')
print(traits.shape)
traits = traits[traits['plot_name'].isin(plot_names)].reset_index(drop=True)
# # we're dropping a lot of traits as a function of missing plot polygons
# tmp = traits[~traits['plot_name'].isin(plot_names)].reset_index(drop=True)
# tmp.to_csv('out/2018/filtered/traits_dropped.csv', index=False)
# print(tmp.shape)
print(traits.shape)

# # filter to where there is actually a measurement
# df = df[df['value'].notna()]
# print(df.shape)

# filter plots
print('\nplots')
print(plots.shape) 
plots = plots[plots['plot_name'].isin(plot_names)].reset_index(drop=True)
print(plots.shape)

# filter spectra
print('\nspectra')
print(spectra.shape)
spectra = spectra[spectra['plot_name'].isin(plot_names)].reset_index(drop=True)
print(spectra.shape)

# filter granule to only where there are extracted spectra
print('\ngranule')
print(granule.shape)
granule = granule[granule['granule_id'].isin(spectra['granule_id'])].reset_index(drop=True)
print(granule.shape)

traits.to_csv('out/2018/filtered/traits.csv', index=False)
plots.to_file('out/2018/filtered/plots.geojson', driver='GeoJSON')
spectra.to_csv('out/2018/filtered/spectra.csv', index=False)
granule.to_csv('out/2018/filtered/granule_metadata.csv', index=False)