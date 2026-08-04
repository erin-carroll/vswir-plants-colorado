import os
import pandas as pd

os.chdir('C:/Users/carroll/Documents/sbgplant')

campaign_name = 'Colorado Headwaters Ecological Spectroscopy Study'
primary_funding_source = 'DOE'
data_repository = 'ESS-DIVE'
taxa_system = None
sensor_name = 'NEON AIS 1'
elevation_source = 'NEON AOP Lidar'

# 2025
# to add more traits later
doi = ['10.15485/3014404', '10.15485/3029300', '10.15485/3022242', '10.15485/3017965', '10.15485/3013535'] # crown polygons, LAI, radiance, reflectance
doi_type = ['metadata', 'metadata', 'dataset', 'dataset', 'dataset']
doi_subtype = ['location', 'field', 'field', 'airborne', 'airborne']

df = pd.DataFrame({
    'campaign_name': campaign_name,
    'primary_funding_source': primary_funding_source,
    'data_repository': data_repository,
    'taxa_system': taxa_system,
    'sensor_name': sensor_name,
    'elevation_source': elevation_source,
    'doi': doi,
    'doi_type': doi_type,
    'doi_subtype': doi_subtype
})

df.to_csv('out/2025/campaign_metadata.csv', index=False)
