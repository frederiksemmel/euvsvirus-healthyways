import pickle

from loguru import logger
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder


def ort_tag_categories(reisende):
    """Returns all location-day tuples in reisende.
    
    A location-day is the tuple:
    (line: str, direction: int, station: str, day: int)
    """
    ort_tag = reisende[["Linie", "Richtung", "Haltestelle", "Tag"]].itertuples(
        index=False, name=None
    )
    ort_tag = list(set(ort_tag))
    return ort_tag


def ort_categories(reisende):
    """Returns all unique location tuples in reisende"""
    ort = reisende[["Linie", "Richtung", "Haltestelle"]].itertuples(
        index=False, name=None
    )
    ort = list(set(ort))
    return ort


def balance_data(reisende, min=30, max=200):
    """Drops locations-days with less than min (default 70) datapoints and samples max (default 200) from each"""
    total = len(reisende[["Linie", "Richtung", "Haltestelle", "Tag"]].drop_duplicates())
    reisende = reisende.groupby(
        ["Linie", "Richtung", "Haltestelle_Id", "Tag"], observed=True
    ).filter(lambda x: len(x) > min)
    dropped = total - len(
        reisende[["Linie", "Richtung", "Haltestelle_Id", "Tag"]].drop_duplicates()
    )
    logger.info(
        f"Dropped {dropped} ({dropped/total:.2f}) location-days as they had less than {min} datapoints"
    )
    reisende = reisende.groupby(
        ["Linie", "Richtung", "Haltestelle_Id", "Tag"], observed=True
    ).head(max)
    sampled = len(
        reisende[["Linie", "Richtung", "Haltestelle_Id", "Tag"]].drop_duplicates()
    )
    logger.info(f"Sampled {max} points from {sampled} location-days to balance data")
    return reisende


def nn_bins_preprocess_features(data, all_ort_categories):
    """Takes the cleaned dataset and preprocesses it for training/predictions.

    all_locations: list of location tuples (line, direction, station). This has to be always the same
    so that the OneHotEncoder works. List should come from /interim/all_locations.pkl
    
    data is the data saved in interim or created by clean_reisende. Neccessary fields are:
    - Uhrzeit_h: float
    - Tag: category(int) 
    - Linie: category(str)
    - Haltestelle: category(str)
    - Richtung: category(int)
    """
    bins_per_day = 48
    df = data[
        ["Linie", "Richtung", "Haltestelle", "Tag", "Uhrzeit_h"]
    ].copy()
    intervals = pd.interval_range(start=0, end=24, periods=bins_per_day, closed="right")
    df["Uhrzeit_bin"] = pd.cut(df["Uhrzeit_h"], bins=intervals)
    df["Ort"] = pd.Categorical(
        data[["Linie", "Richtung", "Haltestelle"]].itertuples(index=False, name=None),
        categories=all_ort_categories,
    )
    all_days = list(range(0,7))
    df["Tag"] = pd.Categorical(df.Tag, categories=all_days)
    logger.info("Binned Uhrzeit on vbz dataset for nn_bins model")

    n = len(data)
    feature_d = 3
    X = np.zeros((n, feature_d), dtype="int32")
    X[:, 0] = df.Ort.cat.codes
    X[:, 1] = df.Uhrzeit_bin.cat.codes
    X[:, 2] = df.Tag.cat.codes

    time_bin_cats = np.arange(0, bins_per_day)
    day_cats = np.arange(7)
    location_cats = np.arange(0, len(all_ort_categories))
    enc = OneHotEncoder(
        handle_unknown="ignore",
        categories=[location_cats, time_bin_cats, day_cats],
        sparse=True,
    )
    X = enc.fit_transform(X)
    logger.info("OneHot encoded vbz dataset for nn_bins model")
    return X


def nn_bins_preprocess_labels(data, all_ort_categories):
    """Returns Y, which is data.Besetzung, as numpy 2d-array"""
    n = len(data)
    label_d = 1
    Y = np.zeros((n, label_d), dtype="float32")
    Y[:, 0] = data.Besetzung
    return Y


def build_features():
    interim_location = "data/vbz_predictions/interim"
    processed_location = "data/vbz_predictions/processed"

    reisende = pickle.load(open(f"{interim_location}/reisende.pkl", "rb"))
    logger.info("Balancing vbz prediction data")
    reisende = balance_data(reisende)
    all_categories = ort_categories(reisende)
    with open(f"{interim_location}/nn_bins_locations.pkl", "wb") as f:
        pickle.dump(all_categories, f)
    X = nn_bins_preprocess_features(reisende, all_categories)
    with open(f"{processed_location}/X_nn_bins.pkl", "wb") as f:
        pickle.dump(X, f)
    Y = nn_bins_preprocess_labels(reisende, all_categories)
    with open(f"{processed_location}/Y_nn_bins.pkl", "wb") as f:
        pickle.dump(Y, f)

    return reisende


if __name__ == "__main__":
    build_features()
