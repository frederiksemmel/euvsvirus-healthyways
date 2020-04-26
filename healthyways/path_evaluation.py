from pprint import pprint
from datetime import *
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
import numpy as np
import requests
import json
import urllib.parse
import dateutil.parser

from healthyways.vbz_predictions.predict_model import get_vbz_context, occupancies_for_line
from healthyways.maps_api import dir_deptime, dir_arrtime


def parse_overral(route):

    distance = route.get("legs")[0].get("distance").get("value")
    duration = timedelta(seconds=route.get("legs")[0].get("duration").get("value"))

    dict = {"overall_distance": distance, "overall_duration": duration}
    return dict


def parse_steps(route):
    steps = []
    for dict in route.get("legs")[0].get("steps"):
        if dict.get("travel_mode") == "TRANSIT":

            if (
                dict.get("transit_details").get("line").get("vehicle").get("name")
                != "Tram"
                and dict.get("transit_details").get("line").get("vehicle").get("name")
                != "Bus"
            ):

                return []
            else:
                dist = dict.get("distance").get("value")
                dur = timedelta(seconds=dict.get("duration").get("value"))
                dep = dict.get("transit_details").get("departure_stop").get("name")
                dep_time = datetime.utcfromtimestamp(
                    dict.get("transit_details").get("departure_time").get("value")
                )
                arr = dict.get("transit_details").get("arrival_stop").get("name")
                arr_time = datetime.utcfromtimestamp(
                    dict.get("transit_details").get("arrival_time").get("value")
                )
                towards = dict.get("transit_details").get("headsign")
                line = dict.get("transit_details").get("line").get("short_name")
                stops = dict.get("transit_details").get("num_stops")
                type = dict.get("travel_mode")
                steps.append(
                    {
                        "type": type,
                        "dist": dist,
                        "dur": dur,
                        "dep": dep,
                        "dep_time": dep_time,
                        "arr": arr,
                        "arr_time": arr_time,
                        "line": line,
                        "towards": towards,
                        "stops": stops,
                    }
                )

        else:
            dist = dict.get("distance").get("value")
            dur = timedelta(seconds=dict.get("duration").get("value"))
            type = dict.get("travel_mode")
            instruction = dict.get("html_instructions")
            steps.append(
                {"type": type, "instruction": instruction, "dist": dist, "dur": dur}
            )

    return steps


def get_stations():
    try:
        halteList = [
            line.rstrip("\n") for line in open("./data/vbz_predictions/interim/stationen.txt")
        ]  # data bus and tram stations
    except:
        halteList = [
            line.rstrip("\n") for line in open("../data/vbz_predictions/interim/stationen.txt")
        ]  # data bus and tram stations
    return halteList


def get_caps():
    capacities = {  # capacities ToDo: get all capacities
        32: {"seats": 60, "stands": 95, "overall": 155},
        61: {"seats": 43, "stands": 54, "overall": 97},
        62: {"seats": 43, "stands": 54, "overall": 97},
        10: {"seats": 90, "stands": 130, "overall": 220},
        6: {"seats": 90, "stands": 130, "overall": 220},
        15: {"seats": 48, "stands": 72, "overall": 120},
        11: {"seats": 90, "stands": 130, "overall": 220},
    }
    return capacities


def get_directions():  # as in the VVZ data (1 or 2)
    try:
        with open("./data/vbz_predictions/interim/Haltestellen_Richtungen.csv", newline="") as f:   #stationen
            reader = csv.reader(f)
            endstations = list(reader)
        endstations = endstations[1:][:]
    except:
        with open("../data/vbz_predictions/interim/Haltestellen_Richtungen.csv", newline="") as f:   #stationen
            reader = csv.reader(f)
            endstations = list(reader)
        endstations = endstations[1:][:]
    dirs = {}  # directions mapped to endstations
    for i in range(len(endstations)):
        dirs[endstations[i][4]] = endstations[i][1]
    return dirs


def get_all_routes(start, destination, dt, timebefore):

    routes = []

    for i in range(0, timebefore, 10):

        route = dir_arrtime(
            start, destination, dt - timedelta(minutes=i)
        )  # dir_arrtime for arrivaltime; dir_deptime for deptime
        for j in range(0, len(route)):
            r = [
                parse_overral(route[j]),
                parse_steps(route[j]),
                0.0,
            ]  # [overall route infos,steps infos,rating]
            # pprint(r)
            if r not in routes:
                routes.append(r)
    return routes

def get_stops(dep, time, arr):
    url ="http://transport.opendata.ch/v1/connections?from="+dep+"&to="+arr+"&time="+str(time.hour)+":"+str(time.minute)+"&direct=1"
    r = requests.get(url)
    dic = r.json()
    stops=[]
    times=[]
    for step in dic.get("connections")[0].get("sections")[0].get("journey").get("passList"):
        stops.append(step.get("station").get("name"))
        try:
            times.append(dateutil.parser.parse(step.get("departure")))
        except:
            times.append(dateutil.parser.parse(step.get("arrival")))


    return stops, times

def evaluate_routes(routes, capacities, dirs, halteList, vbz_context):
    for r in range(0, len(routes)):
        ratio = 0.0
        count = 0.0
        for j in range(len(routes[r][1])):

            if routes[r][1][j].get("type") == "TRANSIT":
                count += 1
                dep = process.extractOne(routes[r][1][j].get("dep"), halteList)[0]
                dep_time = routes[r][1][j].get("dep_time")
                towards = routes[r][1][j].get("towards")
                line = routes[r][1][j].get("line")
                stops = routes[r][1][j].get("stops")
                direction = dirs.get(process.extractOne(towards, halteList)[0])

                print(dep, dep_time, "Line: ", line, "towards: ", towards)

                arr = process.extractOne(routes[r][1][j].get("arr"), halteList)[0]
                arr_time = routes[r][1][j].get("arr_time")
                print(arr, arr_time)

                stop_list, time_list =get_stops(dep,dep_time,arr)

                try:
                    cap = capacities.get(int(line)).get("overall")
                except:
                    cap = 150

                prediction = occupancies_for_line(  # freddis prediction
                    str(line),
                    int(direction),
                    stop_list,
                    time_list,
                    vbz_context
                )
                prediction_max = max(prediction)
                ratio += prediction_max / cap

        if count != 0:
            ratio /= count
            routes[r][2] = ratio
            print("occupancy rate: ", ratio)
        print()
    return routes


def get_best_route(routes):
    bestratio = 1.0
    bestroute = []
    for r in range(len(routes)):  # get best route
        if routes[r][2] <= bestratio and routes[r][2] > 0.0:
            bestroute = routes[r][:]
            bestratio = routes[r][2]

    return bestroute


def prep_route_output(route):
    route[0]["overall_duration"] = str(route[0].get("overall_duration"))

    for dict in route[1]:  # for outputting datetime as string
        if dict.get("type") == "WALKING":
            dict["dur"] = str(dict.get("dur"))
        else:
            dict["arr_time"] = str(dict.get("arr_time"))
            dict["dep_time"] = str(dict.get("dep_time"))
            dict["dur"] = str(dict.get("dur"))
    return route
