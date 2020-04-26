from slackeventsapi import SlackEventAdapter
from slack import WebClient
import os
import urllib.parse
import healthyways.path_evaluation as path_eval
from healthyways.vbz_predictions.predict_model import get_vbz_context
import datetime as dt


vbz_context = get_vbz_context()
halteList = path_eval.get_stations()
capacities = path_eval.get_caps()
dirs = path_eval.get_directions()

def route(start, destination, h,m, timebefore):



    time = dt.datetime.now().replace(hour=h , minute=m)  # timezone

    routes = path_eval.get_all_routes(start, destination, time, timebefore)

    routes = path_eval.evaluate_routes(routes, capacities, dirs, halteList, vbz_context)

    bestroute = path_eval.get_best_route(routes)

    bestroute = path_eval.prep_route_output(bestroute)



    return bestroute






# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = WebClient(slack_bot_token)

event_ids = []
count =0
start=""
destination=""
h=0
m=0
timebefore=0



@slack_events_adapter.on("message")
def handle_message(event_data):
    global count, start, destination, h, m, timebefore

    if(event_data["event_id"] in event_ids):
        return
    event_ids.append(event_data["event_id"])

    message = event_data["event"]
    channel = message["channel"]

    if message.get("subtype") is None and ("route" in message.get('text') or "Route" in message.get('text')) and "Calculating" not in message.get('text'):
        print("got request")
        count=1
        text="<@%s> From?" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=text)

    elif message.get("subtype") is None and count == 1 and "From" not in message.get('text'):
        count=2
        start = message["text"]
        text="<@%s> To?" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=text)
    elif message.get("subtype") is None and count == 2 and "To?" not in message.get('text'):
        count=3
        destination = message["text"]
        text="<@%s> Time? (h:m)" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=text)
    elif message.get("subtype") is None and count == 3 and "Time?" not in message.get('text'):
        count=4
        temp = message["text"].split(":")
        h=int(temp[0])
        m=int(temp[1])
        text="<@%s> Time flexibility? (in m)" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=text)
    elif message.get("subtype") is None and count == 4 and "Time flexibility?" not in message.get('text'):
        count =0
        timebefore = int(message["text"])
        text="<@%s> Calculating best route" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=text)
        try:
            bestroute = route(start,destination,h,m,timebefore)
        except:
            text ="maps error"
            slack_client.chat_postMessage(channel=channel, text=text)


        walkfrom=""
        for j in range(len(bestroute[1])):

            if bestroute[1][j].get("type")=="TRANSIT":
                dep = bestroute[1][j].get("dep")
                dep_time = str(bestroute[1][j].get("dep_time"))
                towards = bestroute[1][j].get("towards").replace("ü","ue")
                line = str(bestroute[1][j].get("line"))
                arr = bestroute[1][j].get("arr")
                arr_time = str(bestroute[1][j].get("arr_time"))

                url = "https://www.google.com/maps/dir/?api=1"
                origin = urllib.parse.quote_plus(dep+" Zürich")
                destination= urllib.parse.quote_plus(arr+" Zürich")
                walkfrom = destination
                mode = urllib.parse.quote_plus("transit")
                url = url + "&origin=" +str(origin) +"&destination="+ str(destination) +"&travelmode="+str(mode)


                output = dep+" "+ dep_time+ " Line: "+ line+ " towards: "+ towards
                slack_client.chat_postMessage(channel=channel, text=output)
                output="<"+url+"|"+arr+">"+" "+arr_time
                slack_client.chat_postMessage(channel=channel, text=output)
            elif bestroute[1][j].get("type")=="WALKING":


                url = "https://www.google.com/maps/dir/?api=1"
                origin = walkfrom
                destination= urllib.parse.quote_plus(bestroute[1][j].get("instruction").replace("Walk to",""))
                mode = urllib.parse.quote_plus("walking")
                url = url + "&origin=" +str(origin) +"&destination="+ str(destination) +"&travelmode="+str(mode)

                output = "Walk to " +"<"+url+"|"+ bestroute[1][j].get("instruction").replace("Walk to","")+">"

                slack_client.chat_postMessage(channel=channel, text=output)




        prozent =round(bestroute[2]*100,2)
        text="vehicle occupation: " +str(prozent)+"%"
        slack_client.chat_postMessage(channel=channel, text=text)
        message_route = " <@%s>! :tram: :tada:" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=message_route)
        count=0



# Example responder to greetings
@slack_events_adapter.on("app_mention")
def handle_mention(event_data):
    if(event_data["event_id"] in event_ids):
        return
    event_ids.append(event_data["event_id"])

    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hi" in message.get('text'):
        print("got message hi")
        channel = message["channel"]
        message = "Hoi <@%s>! :tada:" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=message)






# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    slack_client.chat_postMessage(channel=channel, text=text)

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

# Once we have our event listeners configured, we can start the
# Flask server with the default `/events` endpoint on port 3000
slack_events_adapter.start(port=3000)
