import pandas as pd


def load_data():
    df = pd.read_csv("./PowerData/FY2024.csv",
                     encoding="ISO-8859-1")
    return df


def load_lat_lngs():
    df = pd.read_csv("./PowerData/CityLatLng.csv",
                     encoding="ISO-8859-1")
    return df
