import googlemaps
import os


def dir_deptime(start, dest, dep_time):

    api = os.environ["GOOGLE_API_KEY"]
    gmaps = googlemaps.Client(key=api)
    route = gmaps.directions(
        start, dest, mode="transit", departure_time=dep_time, alternatives=True
    )

    return route


def dir_arrtime(start, dest, arr_time):

    api = os.environ["GOOGLE_API_KEY"]
    gmaps = googlemaps.Client(key=api)
    route = gmaps.directions(
        start, dest, mode="transit", arrival_time=arr_time, alternatives=True
    )

    return route
