from datetime import *
from pprint import pprint
import time
import sys

from healthyways.path_evaluation import *





vbz_context = get_vbz_context()
halteList = get_stations()
capacities = get_caps()
dirs = get_directions()


if len(sys.argv) == 1:

    finished = False
    while not finished:
        try:
            start = input("From? ")
            destination = input("To? ")
            h = int(input("Hour? "))
            m = int(input("Minute? "))
            timebefore = int(input("Time flexibility in mins? "))
        except:
            print("wrong input try again")
            print()
            continue
        dt = datetime.now().replace(hour=h + 2, minute=m)  # timezone

        routes = get_all_routes(start, destination, dt, timebefore)

        print()
        print("Calculating ", len(routes), "possible routes...")
        print()


        routes = evaluate_routes(routes, capacities, dirs, halteList, vbz_context)

        bestroute = get_best_route(routes)

        bestroute = prep_route_output(bestroute)

        print()
        print("-----best route:-----")
        print()
        pprint(bestroute)
        print("best mean occupancy rate: ", bestroute[2])
        print()

        inp = input("do you want to start another request?y/n ")
        if inp != "y":
            finished = True
else:
    start = str(sys.argv[1])
    destination = str(sys.argv[2])
    h = int(sys.argv[3])
    m = int(sys.argv[4])
    timebefore = int(sys.argv[5])
    dt = datetime.now().replace(hour=h + 2, minute=m)  # timezone

    routes = get_all_routes(start, destination, dt, timebefore)

    print()
    print("Calculating ", len(routes), "possible routes...")
    print()

    routes = evaluate_routes(routes, capacities, dirs, halteList, vbz_context)

    bestroute = get_best_route(routes)

    bestroute = prep_route_output(bestroute)


    pprint(bestroute)
