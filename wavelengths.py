import os
import pandas as pd
import h5py

# 2018
fp = '/store/carroll/col/data/2018/raw/L1/radianceH5/2018061214/NEON_D13_CRBU_DP1_20180612_154959_radiance.h5'
with h5py.File(fp, "r") as f:
    wavelength = f["/CRBU/Radiance/Metadata/Spectral_Data/Wavelength"][:]
    fwhm = f["/CRBU/Radiance/Metadata/Spectral_Data/FWHM"][:]
campaign_name = 'East River 2018'
sensor_name = 'NEON AIS 1'
df = pd.DataFrame({
    'campaign_name': campaign_name,
    'sensor_name': sensor_name,
    'band': range(len(wavelength)),
    'wavelength': wavelength,
    'fwhm': fwhm
})
df.to_csv('/store/carroll/sbgplants/out/2018/wavelengths.csv', index=False)

# # 2025
# fp = r"C:\Users\carroll\Downloads\2025_FullSite_D13_2025_CRBU_2_L1_Spectrometer_RadianceH5_2025062714_NEON_D13_CRBU_DP1_L003-1_20250627_radiance.h5"
# with h5py.File(fp, "r") as f:
#     wavelength = f["/CRBU/Radiance/Metadata/Spectral_Data/Wavelength"][:]
#     fwhm = f["/CRBU/Radiance/Metadata/Spectral_Data/FWHM"][:]
# campaign_name = 'Colorado Headwaters Ecological Spectroscopy Study'
# sensor_name = 'NEON AIS 1'
# df = pd.DataFrame({
#     'campaign_name': campaign_name,
#     'sensor_name': sensor_name,
#     'band': range(1, len(wavelength) + 1),
#     'wavelength': wavelength,
#     'fwhm': fwhm
# })
# df.to_csv('out/2025/wavelengths.csv', index=False)