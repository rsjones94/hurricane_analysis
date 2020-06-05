"""
Functions to help with extracting rain gauge data from .bils format raster files
"""

import os
from datetime import datetime
import time

import gdal
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from read import clean_read


def date_from_prism_file(file):
    """
    Returns a datetime object representing the date that that the prism file has data for

    Args:
        file: prism filename

    Returns:
        datetime object

    """

    raw = file[-16:-8]
    year = int(raw[:4])
    month = int(raw[4:6])
    day = int(raw[6:])

    return datetime(year,month,day)


def value_at_coords(file, x_coords, y_coords):
    """
    Returns the value in a raster that a coordinate falls within (raster and coords must be in same projection)

    Args:
        file: filepath
        x_coords: x coords list of floats
        y_coord: y coords list of floats

    Returns:
        values at the coordinates

    """

    dataset = gdal.Open(file)
    band = dataset.GetRasterBand(1)

    cols = dataset.RasterXSize
    rows = dataset.RasterYSize

    transform = dataset.GetGeoTransform()

    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = -transform[5]

    data = band.ReadAsArray(0, 0, cols, rows)

    cols = [int((x_coord - xOrigin) / pixelWidth) for x_coord in x_coords]
    rows = [int((yOrigin - y_coord) / pixelHeight) for y_coord in y_coords]

    dataset = None

    vals = [data[row][col] for row,col in zip(rows,cols)]

    return vals


def date_and_vals(file, x_coords, y_coords):
    """
    Returns the date and value of a prism raster at a given coordinate

    Args:
        file: filepath
        x_coord: x coord as float
        y_coord: y coord as float

    Returns:
        tuple, (date, list of values at the coordinate)

    """

    val = value_at_coords(file, x_coords, y_coords)
    date = date_from_prism_file(file)

    return date,val


def get_bils(parent):
    """
    Gets all .bil files in a parent directory's subdirectories

    Args:
        parent: parent directory

    Returns:
        list of file filepaths to all .bil files

    """
    files = []
    subs = os.listdir(parent)
    for sub in subs:
        sub_path = os.path.join(parent,sub)
        all_files = os.listdir(sub_path)
        bils = [file for file in all_files if file[-4:] == '.bil']
        full_bils = [os.path.join(parent, sub, file) for file in bils]
        files.extend(full_bils)
    return files


def extract_timeseries(x_coords, y_coords, bils):
    """
    Creates a time series from a list of prism .bils rasters and a coordinate pair

    Args:
        names: names to associate with returned value
        x_coord: x coords
        y_coord: y coords
        bils: list of full paths to .bil prism rasters

    Returns:
        a tuple; one entry is a list of dates and the other is a list of lists of vals at a coordinate

    """
    start = time.time()
    extracted = []
    n = len(bils)
    for i,file in enumerate(bils):
        intermediate1 = time.time()
        extracted.append(date_and_vals(file, x_coords, y_coords))

        intermediate2 = time.time()
        intermediate_elap = round(intermediate2-intermediate1, 2) # in seconds
        running_time = round(intermediate2-start, 2)/60 # in minutes
        frac_progress = (i+1)/n
        estimated_total_time = round(running_time*(1/frac_progress) - running_time, 2)

        print(f'Processing time: {intermediate_elap} seconds. File {i+1} of {n} complete. Estimated time remaining: '
              f'{estimated_total_time} minutes')
    dates = [i[0] for i in extracted]
    vals = [i[1] for i in extracted]

    final = time.time()
    elap = round(final-start, 2)
    print(f'FINISHED. Elapsed time: {elap/60} minutes')

    return dates, vals


def unpack_timeseries(names, dates, val_rows):
    """
    Unpacks the dates and vals from extract_timeseries

    Args:
        names: column names
        dates: list of dates
        val_rows: list of rows of values

    Returns:
        a pd DataFrame

    """

    print('Unpacking...')

    row_dicts = []
    for i,(date, row_vals) in enumerate(zip(dates,val_rows)):
        row = {name:v for name,v in zip(names,row_vals)}
        row['date'] = date
        row_dicts.append(row)
    #return(row_dicts)
    df = pd.DataFrame(row_dicts)
    df = df.set_index('date')

    return df

