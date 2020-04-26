import pickle

from loguru import logger
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD


def train_nn_bins(X, Y):
    """Trains the neural network with time bins. X,Y are numpy 2d-arrays.
    
    Features:
    - Onehot of Locations. A location is the tuple (line, direction, stop)
    - Onhot day. A day is a number between 0-6
    - Onehot time-bin. Per default the timebins are 30min long 

    Labels:
    - Occupation: float
    """
    _, d = X.shape
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(units=16, activation="relu", input_dim=d,))
    model.add(tf.keras.layers.Dense(units=1))

    sgd = tf.keras.optimizers.SGD(learning_rate=0.005, momentum=0.00, nesterov=False)
    model.compile(
        loss="mean_squared_error", optimizer=sgd, metrics=["mean_squared_error"]
    )

    logger.info(model.summary())
    model.fit(X, Y, batch_size=128, epochs=8)
    return model


def train_models():
    processed_location = "data/vbz_predictions/processed"
    model_location = "models/vbz_predictions"
    X = pickle.load(open(f"{processed_location}/X_nn_bins.pkl", "rb"))
    Y = pickle.load(open(f"{processed_location}/Y_nn_bins.pkl", "rb"))
    logger.info("Training the vbz predictions NN Bins model")
    model = train_nn_bins(X, Y)
    model.reset_metrics()
    model.save(f"{model_location}/model_nn_bins.h5")


if __name__ == "__main__":
    train_models()
