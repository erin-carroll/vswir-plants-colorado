import h5py

fp = r"C:\Users\carroll\Downloads\2025_FullSite_D13_2025_CRBU_2_L1_Spectrometer_RadianceH5_2025062714_NEON_D13_CRBU_DP1_L003-1_20250627_radiance.h5"
# with h5py.File(fp, 'r') as f:
#     dset = f["/CRBU/Radiance/RadianceIntegerPart"]
#     for key, val in dset.attrs.items():
#         print(f"{key}: {val}")   # print all attributes in dataset

with h5py.File(fp, "r") as f:
    for path in [
        "/",
        "/CRBU",
        "/CRBU/Radiance",
        "/CRBU/Radiance/Metadata",
        "/CRBU/Radiance/Metadata/Spectral_Data",
    ]:
        print(f"\n--- {path} ---")
        obj = f[path]
        for k, v in obj.attrs.items():
            print(k, ":", v)