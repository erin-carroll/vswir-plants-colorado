import os
import pandas as pd

os.chdir('C:/Users/erinc/Documents/sbgplant')

campaign_name = 'East River 2018'
primary_funding_source = 'DOE'
data_repository = 'ESS-DIVE'
taxa_system = None
sensor_name = 'NEON AIS 1'
elevation_source = 'NEON AOP Lidar'

doi = ['10.15485/1618130', '10.15485/1618132', '10.15485/1631278', '10.15485/1617204', '10.15485/3013527']
doi_type = ['metadata', 'dataset', 'dataset', 'dataset', 'dataset']
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

df.to_csv('out/2018/campaign_metadata.csv', index=False)
