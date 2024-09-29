# import libraries

import numpy as np
import pandas as pd
from geopy.distance import geodesic
from osgeo import gdal

# tiff file to calculate the distance to offshore, can be downloaded from GFW(https://globalfishingwatch.org/data-download/datasets/public-distance-from-shore-v1)
tif_path = 'distance/distance.tif'
dataset = gdal.Open(tif_path)
geotransform = dataset.GetGeoTransform()
band = dataset.GetRasterBand(1)
band_data = band.ReadAsArray()


# feature calculate function
def process(test):
    # calculate time difference
    time = pd.to_datetime(test["time"])
    time_gap = time.diff()[1:]
    time_gap = np.array([t.total_seconds() for t in time_gap])
    
    time_gap = np.array([i if i!=0 else np.inf for i in time_gap])

    # speed
    v = np.array(test["速度"] * 0.514444)
    # speed change
    vd = np.diff(v)
    v = v[1:]
    # a
    a = vd / time_gap

    # distance between two adjacant points
    coordinates = [(test.loc[i, "lat"], test.loc[i, "lon"]) for i in range(len(test))]
    d = np.array([geodesic(coord1, coord2).meters for coord1, coord2 in zip(coordinates[:-1], coordinates[1:])])

    # d / time_gap
    dt = d / time_gap

    # distance to offershore
    target_latitude = np.array(test.loc[:, "lat"])
    target_longitude = np.array(test.loc[:, "lon"])

    pixel_x = ((target_longitude - geotransform[0]) / geotransform[1]).astype("int")
    pixel_y = ((target_latitude - geotransform[3]) / geotransform[5]).astype("int")

    s = band_data[pixel_y, pixel_x]

    # distance change
    sd = np.diff(s)
    s = s[1:]
    # distance change / time_gap
    sdt = sd / time_gap


    # course change
    c = np.array(test["方向"] / 180 * np.pi)
    cd = np.diff(c).tolist()
    cd = [ccd if ccd < np.pi else ccd - 2 * np.pi for ccd in cd]
    cd = np.array([ccd if ccd > -np.pi else ccd + 2 * np.pi for ccd in cd])
    # course change / time_gap
    cdt = cd / time_gap

    f = np.stack([v, vd, a, d, dt, s, sd, sdt, cd, cdt],axis=-1)

    f = pd.DataFrame(f, columns=["v","vd","a","d","dt","s","sd","sdt","cd","cdt"])
    return f