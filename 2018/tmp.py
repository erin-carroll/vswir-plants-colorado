import pandas as pd

df18 = pd.read_csv(r"C:\Users\carroll\Documents\sbgplant\data\2018\raw\10.15485.1618130\data\species_list.csv")
df25 = pd.read_csv(r"C:\Users\carroll\Documents\sbgplant\data\2025\veg_or_cover_type.csv")

df18['taxa'] = df18['Genus'] + ' ' + df18['Species']
print(set(df18['taxa']))

print(df18.columns)
print(df25.columns)