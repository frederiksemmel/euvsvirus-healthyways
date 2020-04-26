import pickle

from loguru import logger
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD

from .build_features import nn_bins_preprocess_features


def get_nn_bins_context():
    """Contains all models and data in order to quickly make predictions for vbz NN Bins model"""
    interim_location = "data/vbz_predictions/interim"
    model_location = "models/vbz_predictions"
    locations = pickle.load(open(f"{interim_location}/nn_bins_locations.pkl", "rb"))
    model = tf.keras.models.load_model(f'{model_location}/model_nn_bins.h5')
    return (locations, model)


def nn_bins_predict(data, context):
    """Returns predicted occupation from model inside the context.

    data: pandas DataFrame. Columns are:
        - Uhrzeit_h: float
        - Tag: int
        - Linie: str
        - Haltestelle: str
        - Richtung: int
    context: Context object
    """
    locations, model = context
    X = nn_bins_preprocess_features(data, locations)
    Y = model.predict(X)
    data["Besetzung"] = Y.reshape(-1)
    return data

def get_vbz_context():
    """This returns the context for the predictions model."""
    return get_nn_bins_context()

def occupancies_for_line(line, direction, stops, times, vbz_context):
    """Returns the list of occupancies on eacy stop in stops.

    line: str. See all options in data/vbz_predicitons/raw/LINIE.csv column Linienname_Fahrgastauskunft
    direction: int. Either 1 or 2, figure it out yourself
    stops: list(str). The stops have to be named as in data/vbz_predicitons/raw/HALTESTELLEN.csv column Haltestellenlangname
    times: list(datetime.datetime). List of python datetimes. Corresponds to the time when the bus stops at stop
    vbz_context: the object from get_vbz_context
    """
    # construct DataFrame for nn_bins
    df = pd.DataFrame()
    df["Haltestelle"] = stops
    df["Uhrzeit_h"] = [t.hour + t.minute/60 for t in times]
    df["Tag"] = [t.day for t in times]
    df["Richtung"] = direction
    df["Linie"] = line

    data = nn_bins_predict(df, vbz_context)
    occupancies = list(data['Besetzung'])
    logger.debug(f"occupancies for line {line} direction{direction} stops {stops} times {times} are {occupancies}")
    return occupancies
    