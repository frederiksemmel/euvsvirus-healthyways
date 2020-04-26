import requests


def download_data(location="data/vbz_predictions/raw"):
    """Downloads the vbz dataset containing average statistics about all the zurich bus/tram lines for 2019.
    
    The following CSV files will be donwloaded:
    TAGTYP.csv: contains information about the tagtyp, which represents different time schedules (Monday-Friday, Saturday etc.)
    LINIE.csv: information about each line
    HALTESTELLEN.csv: information about each bus/tram stop operated by VBZ
    REISENDE.csv: this dataset of about 150MB contains the 2019 average occupation for each line, direction, stop, daytype and time"""

    tagtyp_url = "https://data.stadt-zuerich.ch/dataset/560952ab-1028-4de6-ac54-cbb1e0f4e1d7/resource/09ffe483-19da-495e-81c6-711ae8dd49d3/download/tagtyp.csv"
    reisende_url = "https://data.stadt-zuerich.ch/dataset/560952ab-1028-4de6-ac54-cbb1e0f4e1d7/resource/38b0c1e5-1f4e-444d-975c-61a462aa8ca6/download/reisende.csv"
    linie_url = "https://data.stadt-zuerich.ch/dataset/560952ab-1028-4de6-ac54-cbb1e0f4e1d7/resource/463f92e0-5b20-44b3-b27f-59499e331e8d/download/linie.csv"
    haltestellen_url = "https://data.stadt-zuerich.ch/dataset/560952ab-1028-4de6-ac54-cbb1e0f4e1d7/resource/948b6347-8988-4705-9b08-45f0208a15da/download/haltestellen.csv"

    res = requests.get(tagtyp_url)
    with open(f"{location}/TAGTYP.csv", "wb") as f:
        f.write(res.content)

    res = requests.get(reisende_url)
    with open(f"{location}/REISENDE.csv", "wb") as f:
        f.write(res.content)

    res = requests.get(linie_url)
    with open(f"{location}/LINIE.csv", "wb") as f:
        f.write(res.content)

    res = requests.get(haltestellen_url)
    with open(f"{location}/HALTESTELLEN.csv", "wb") as f:
        f.write(res.content)


if __name__ == "__main__":
    download_data(location="data/vbz_predictions/raw")
