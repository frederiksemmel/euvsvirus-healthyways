import pickle

from loguru import logger
import pandas as pd
import numpy as np


def clean_reisende(reisende, tagtyp, linie, haltestellen):
    """Cleans the raw VBZ Fahrgastzahlen data
    
    reisende, tagtyp, linie, haltestellen is the raw data from VBZ Fahrgastzahlen.
    
    The returned dataset has at least the following columns:
    - Uhrzeit_h: float
    - Tag: category(int) 
    - Linie: category(str)
    - Haltestelle: category(str)
    - Richtung: category(int)
    - Besetzung: float
    """
    reisende = reisende[
        [
            "Tagtyp_Id",
            "Linienname",
            "Richtung",
            "Sequenz",
            "Haltestellen_Id",
            "Nach_Hst_Id",
            "FZ_AB",
            "Anzahl_Messungen",
            "Einsteiger",
            "Aussteiger",
            "Besetzung",
            "Distanz",
        ]
    ].copy()
    reisende = reisende.rename(
        columns={
            "Linienname": "Linie",
            "Sequenz": "Anzahl_Haltestellen",
            "Haltestellen_Id": "Haltestelle_Id",
            "Nach_Hst_Id": "Nachste_Haltestelle_Id",
            "FZ_AB": "Uhrzeit",
        }
    )
    reisende = reisende.astype(
        {
            "Tagtyp_Id": "category",
            "Linie": "category",
            "Richtung": "category",
            "Anzahl_Haltestellen": "int32",
            "Haltestelle_Id": "category",
            "Nachste_Haltestelle_Id": "category",
            "Uhrzeit": "str",
            "Anzahl_Messungen": "int32",
            "Einsteiger": "float32",
            "Aussteiger": "float32",
            "Besetzung": "float32",
            "Distanz": "float32",
        }
    )
    linie = linie.set_index('Linienname')
    haltestellen = haltestellen.set_index('Haltestellen_Id')

    id_to_name = haltestellen["Haltestellenlangname"].astype('str')
    id_to_linienname = linie["Linienname_Fahrgastauskunft"].astype('str')

    mon_thu = [7, 12, 18, 23]
    mon_fri = [6, 17, 22]
    fri = [5, 10, 16, 21]
    sat = [4, 9, 15, 20]
    sun = [3, 8, 14, 19, 13]
    id_to_days = {i: tuple(range(4)) for i in mon_thu}
    id_to_days.update({i: tuple(range(5)) for i in mon_fri})
    id_to_days.update({i: (4) for i in fri})
    id_to_days.update({i: (5) for i in sat})
    id_to_days.update({i: (6) for i in sun})
    reisende["Tag"] = reisende["Tagtyp_Id"].map(id_to_days)
    reisende = reisende.explode("Tag")
    reisende = reisende.astype({"Tag": "category"}, copy=False)
    logger.info("Augmented vbz dataset to every day of the week")

    reisende["Haltestelle"] = (
        reisende["Haltestelle_Id"].map(id_to_name).astype("category", copy=False)
    )
    reisende["Nachste_Haltestelle"] = (
        reisende["Nachste_Haltestelle_Id"]
        .map(id_to_name)
        .astype("category", copy=False)
    )
    reisende["Linie"] = (
        reisende["Linie"].map(id_to_linienname).astype("category", copy=False)
    )

    time = reisende["Uhrzeit"].copy().str.split(":", expand=True).astype(int)
    reisende["Uhrzeit"] = (
        pd.to_timedelta(time[0], unit="h")
        + pd.to_timedelta(time[1], unit="m")
        + pd.to_timedelta(time[2], unit="s")
    )
    reisende["Uhrzeit_h"] = reisende.Uhrzeit / pd.Timedelta("1 Hour")
    reisende = reisende[reisende.Uhrzeit_h <= 24]
    logger.info("Parsed Uhrzeit on vbz dataset")

    reisende = reisende.reset_index(drop=True)
    reisende = reisende.dropna(
        subset=["Linie", "Haltestelle", "Richtung", "Tag", "Uhrzeit_h", "Besetzung"]
    )
    logger.info("Dropped NaN on vbz dataset")
    return reisende


def clean_data():
    raw_location = "data/vbz_predictions/raw"
    interim_location = "data/vbz_predictions/interim"
    tagtyp = pd.read_csv(f"{raw_location}/TAGTYP.csv", sep=";")
    linie = pd.read_csv(f"{raw_location}/LINIE.csv", sep=";")
    haltestellen = pd.read_csv(f"{raw_location}/HALTESTELLEN.csv", sep=";")
    reisende = pd.read_csv(f"{raw_location}/REISENDE.csv", sep=";")
    logger.info("Loaded vbz predictions datasets")
    reisende = clean_reisende(reisende, tagtyp, linie, haltestellen)
    with open(f"{interim_location}/reisende.pkl", "wb") as f:
        pickle.dump(reisende, f)
    return reisende


if __name__ == "__main__":
    clean_data()
