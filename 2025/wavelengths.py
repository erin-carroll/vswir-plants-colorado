import os
import pandas as pd
import h5py

# 2025
fp = '/store/carroll/col/data/2025/raw/L1/radianceH5/2025062115/NEON_D13_ALMO_DP1_L001-1_20250621_radiance.h5'
with h5py.File(fp, "r") as f:
    wavelength = f["/ALMO/Radiance/Metadata/Spectral_Data/Wavelength"][:]
    fwhm = f["/ALMO/Radiance/Metadata/Spectral_Data/FWHM"][:]
campaign_name = 'Colorado Headwaters Ecological Spectroscopy Study'
sensor_name = 'NEON AIS 1'
df = pd.DataFrame({
    'campaign_name': campaign_name,
    'sensor_name': sensor_name,
    'band': range(len(wavelength)),
    'wavelength': wavelength,
    'fwhm': fwhm
})
df.to_csv('/store/carroll/sbgplants/out/2025/wavelengths.csv', index=False)