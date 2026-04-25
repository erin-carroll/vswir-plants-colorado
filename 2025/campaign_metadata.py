import os
import pandas as pd

os.chdir('C:/Users/carroll/Documents/sbgplant')

campaign_name = 'Colorado Headwaters Ecological Spectroscopy Study'
primary_funding_source = 'DOE'
data_repository = 'ESS-DIVE'
doi = r'10.15485/3017965, 10.15485/3029300, 10.15485/3022242, 10.15485/3014404'
taxa_system = None
sensor_name = 'NEON AIS 1'
elevation_source = 'NEON AOP Lidar'
df = pd.DataFrame({
    'campaign_name': campaign_name,
    'primary_funding_source': primary_funding_source,
    'data_repository': data_repository,
    'doi': doi,
    'taxa_system': taxa_system,
    'sensor_name': sensor_name,
    'elevation_source': elevation_source
}, index=[0])
df.to_csv('out/2025/campaign_metadata.csv', index=False)
