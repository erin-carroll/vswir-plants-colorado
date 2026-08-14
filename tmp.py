import pandas as pd
import geopandas as gpd

plots = gpd.read_file(r"C:\Users\carroll\Downloads\plots (1).geojson")
# print(len(plots['plot_name'].unique()))

spectra = pd.read_csv(r"C:\Users\carroll\Downloads\spectra (3).csv")
# print(spectra.columns)
# print(len(spectra['granule_id'].unique()))
# print(spectra.shape)

traits = pd.read_csv(r"C:\Users\carroll\Downloads\traits (1).csv")
# # traits = traits[traits['trait'] != 'Wet weight']
# # traits = traits[traits['trait'] != 'Dry weight']
# print(traits.columns)
# print(traits.shape)
# print(traits['trait'].unique())

fp = r'C:\Users\carroll\Documents\sbgplant\data\2025\CHESS_2025_crowns.geojson'
gdf = gpd.read_file(fp)
print(gdf.shape)