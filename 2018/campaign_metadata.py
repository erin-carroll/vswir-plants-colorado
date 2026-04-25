import os
import pandas as pd

os.chdir('C:/Users/carroll/Documents/sbgplant')

campaign_name = 'East River 2018'
primary_funding_source = 'DOE'
data_repository = 'ESS-DIVE'
doi = r'10.15485/1618130, 10.15485/1618132, 10.15485/1631278, 10.15485/1617204, 10.15485/1618131, 10.15485/3017966'
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
df.to_csv('out/2018/campaign_metadata.csv', index=False)